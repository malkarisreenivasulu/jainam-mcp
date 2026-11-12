"""Explicit read-only adapter around the independently published Jainam SDK."""

from __future__ import annotations

import csv
import io
import json
import re
from collections.abc import Callable
from urllib.parse import urlsplit

import requests
from jainam_api import APIError, Client

from jainam_mcp import __version__
from jainam_mcp.config import Credentials

BASE_URL = "https://protrade.jainam.in/"
EXCHANGES = {"NSE", "NFO", "CDS", "BSE", "BFO", "BCD", "MCX", "INDICES"}
# Only documented read operations. Some read endpoints use HTTP POST.
READ_ROUTES = {
    ("GET", "/omt/api-order-rest/v1/profile/"),
    ("GET", "/omt/api-order-rest/v1/limits/"),
    ("GET", "/omt/api-order-rest/v1/orders/book"),
    ("GET", "/omt/api-order-rest/v1/orders/trades"),
    ("GET", "/omt/api-order-rest/v1/positions"),
    *(("GET", f"/omt/api-order-rest/v1/holdings/{product}") for product in ("cnc", "mtf", "mis")),
    ("POST", "/omt/api-order-rest/v1/orders/history"),
    ("POST", "/chart/history"),
    *(("GET", f"/contract/{exchange}.csv") for exchange in EXCHANGES),
}
SENSITIVE_KEYS = {
    "usersession",
    "session",
    "sessiontoken",
    "accesstoken",
    "refreshtoken",
    "authorization",
    "apisecret",
    "apikey",
    "authcode",
    "appcode",
    "password",
    "token",
    "userid",
    "clientid",
    "pan",
    "panno",
    "pannumber",
    "email",
    "emailid",
    "mobile",
    "mobileno",
    "mobilenumber",
    "phone",
    "phonenumber",
    "bankaccount",
    "bankaccountnumber",
    "accountnumber",
    "ifsc",
    "address",
    "residentialaddress",
    "dateofbirth",
    "dob",
}


class ReadOnlySession(requests.Session):
    """Reject any SDK request outside the fixed read-operation list."""

    def request(self, method, url, **kwargs):
        parsed = urlsplit(url)
        if (
            parsed.scheme != "https"
            or parsed.netloc != "protrade.jainam.in"
            or parsed.query
            or parsed.fragment
            or (method.upper(), parsed.path) not in READ_ROUTES
        ):
            raise PermissionError("Request is outside the read-only API allowlist.")
        kwargs["allow_redirects"] = False
        response = super().request(method, url, **kwargs)
        if 300 <= response.status_code < 400:
            response.close()
            raise APIError("Unexpected broker redirect", response.status_code)
        return response


def sanitize(value, secrets: tuple[str, ...]):
    if isinstance(value, dict):
        return {
            key: "[REDACTED]"
            if re.sub(r"[^a-z0-9]", "", str(key).lower()) in SENSITIVE_KEYS
            else sanitize(item, secrets)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [sanitize(item, secrets) for item in value]
    if isinstance(value, str):
        for secret in secrets:
            if secret:
                value = value.replace(secret, "[REDACTED]")
    return value


class Service:
    def __init__(self, credentials: Credentials | None, client_factory: Callable = Client):
        self.credentials = credentials
        self.client_factory = client_factory

    def status(self) -> dict:
        return {
            "ok": True,
            "mode": "read_only",
            "credentials_configured": self.credentials is not None,
            "connection_tested": False,
            "version": __version__,
        }

    def _run(self, operation: Callable) -> dict:
        if not self.credentials:
            return {"ok": False, "error": "NOT_CONFIGURED", "message": "Run jainam-mcp configure locally."}
        transport = ReadOnlySession()
        try:
            client = self.client_factory(
                user_session=self.credentials.user_session,
                user_id=self.credentials.user_id,
                session=transport,
                timeout=20,
            )
            result = operation(client)
            cleaned = sanitize(result, (self.credentials.user_session, self.credentials.user_id))
            if len(json.dumps(cleaned, allow_nan=False).encode()) > 1024 * 1024:
                return {"ok": False, "error": "RESPONSE_TOO_LARGE", "message": "Request a smaller result."}
            return {"ok": True, "data": cleaned}
        except APIError as exc:
            status = exc.status_code
            code = (
                "SESSION_EXPIRED_OR_DENIED"
                if status in (401, 403)
                else "RATE_LIMITED"
                if status == 429
                else "BROKER_ERROR"
            )
            return {
                "ok": False,
                "error": code,
                "message": "Jainam could not complete the read request.",
                "http_status": status,
            }
        except requests.RequestException:
            return {
                "ok": False,
                "error": "NETWORK_ERROR",
                "message": "Cannot reach Jainam. Check connectivity.",
            }
        except (ValueError, PermissionError):
            return {
                "ok": False,
                "error": "INVALID_REQUEST",
                "message": "Check tool arguments and supported values.",
            }
        except Exception:
            # Raw SDK errors and broker payloads can contain secrets or account information.
            return {
                "ok": False,
                "error": "INTERNAL_ERROR",
                "message": "Unexpected API response; see troubleshooting.",
            }
        finally:
            transport.close()

    def account(self, kind: str, product_type: str = "cnc") -> dict:
        methods = {
            "profile": "profile",
            "funds": "funds",
            "holdings": "holdings",
            "positions": "positions",
            "orders": "order_book",
            "trades": "trade_book",
        }
        if kind not in methods:
            return {"ok": False, "error": "INVALID_REQUEST"}
        return self._run(
            lambda client: (
                getattr(client, methods[kind])(product_type)
                if kind == "holdings"
                else getattr(client, methods[kind])()
            )
        )

    def order_history(self, order_id: str) -> dict:
        if not order_id.strip() or len(order_id) > 100:
            return {"ok": False, "error": "INVALID_REQUEST"}
        return self._run(lambda client: client.order_history(order_id))

    def historical(self, exchange: str, token: str, resolution: str, from_ms: int, to_ms: int) -> dict:
        if (
            exchange not in EXCHANGES
            or not token.strip()
            or len(token) > 100
            or not resolution.strip()
            or len(resolution) > 20
            or not 0 < from_ms < to_ms
            or to_ms - from_ms > 31 * 24 * 60 * 60 * 1000
        ):
            return {
                "ok": False,
                "error": "INVALID_REQUEST",
                "message": "Use a supported exchange and a range up to 31 days.",
            }
        return self._run(lambda client: client.historical_data(token, resolution, from_ms, to_ms, exchange))

    def search_contracts(self, exchange: str, query: str, limit: int) -> dict:
        if exchange not in EXCHANGES or not query.strip() or len(query) > 100 or not 1 <= limit <= 50:
            return {"ok": False, "error": "INVALID_REQUEST"}

        def operation(client):
            # Keep downloads in memory and bounded. No model-supplied paths or URLs.
            with client.session.get(
                client.contract_url(exchange), headers=client.headers, timeout=20, stream=True
            ) as response:
                if response.status_code != 200:
                    raise APIError("Contract download failed", response.status_code)
                chunks, size = [], 0
                for chunk in response.iter_content(65536):
                    size += len(chunk)
                    if size > 25 * 1024 * 1024:
                        raise ValueError("Contract master exceeds limit")
                    chunks.append(chunk)
                text = b"".join(chunks).decode("utf-8-sig")
                if "text/html" in response.headers.get(
                    "Content-Type", ""
                ).lower() or text.lstrip().startswith("<"):
                    raise APIError(
                        "Broker returned a web page instead of contract data", response.status_code
                    )
                rows = csv.DictReader(io.StringIO(text))
                if not rows.fieldnames or len(rows.fieldnames) < 2:
                    raise APIError("Broker did not return a usable contract CSV", response.status_code)
                matches = []
                for row in rows:
                    if query.casefold() in " ".join(str(v) for v in row.values()).casefold():
                        matches.append(
                            {
                                "instrument_token" if key.lower() == "token" else key: value
                                for key, value in row.items()
                            }
                        )
                        if len(matches) == limit:
                            break
                return {
                    "exchange": exchange,
                    "matches": matches,
                    "limit": limit,
                    "note": "Current downloaded master; refresh tokens before use. Matching is text search.",
                }

        return self._run(operation)
