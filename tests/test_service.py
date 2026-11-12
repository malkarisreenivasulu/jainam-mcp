import json
from unittest.mock import Mock

import pytest
import requests
from jainam_api import Client

from jainam_mcp.config import Credentials
from jainam_mcp.service import READ_ROUTES, ReadOnlySession, Service

CREDS = Credentials("synthetic-user", "synthetic-session-not-real")


def response(data, status=200):
    r = requests.Response()
    r.status_code = status
    r._content = json.dumps(data).encode()
    return r


@pytest.mark.parametrize(
    "kind,method,path",
    [
        ("profile", "GET", "/omt/api-order-rest/v1/profile/"),
        ("funds", "GET", "/omt/api-order-rest/v1/limits/"),
        ("positions", "GET", "/omt/api-order-rest/v1/positions"),
        ("orders", "GET", "/omt/api-order-rest/v1/orders/book"),
        ("trades", "GET", "/omt/api-order-rest/v1/orders/trades"),
        ("holdings", "GET", "/omt/api-order-rest/v1/holdings/cnc"),
    ],
)
def test_real_sdk_read_routes_and_secret_redaction(monkeypatch, kind, method, path):
    def send(self, actual_method, url, **kw):
        assert actual_method == method and url.endswith(path)
        assert kw["allow_redirects"] is False
        assert kw["headers"]["token"] == CREDS.user_session
        return response(
            {
                "status": "ok",
                "nested": {
                    "userSession": CREDS.user_session,
                    "userId": CREDS.user_id,
                    "PAN": "synthetic-pan",
                },
                "description": f"echo {CREDS.user_session}",
                "amount": 125.5,
            }
        )

    monkeypatch.setattr(requests.Session, "request", send)
    result = Service(CREDS).account(kind)
    assert result["ok"] and result["data"]["amount"] == 125.5
    serialized = json.dumps(result)
    assert CREDS.user_session not in serialized and CREDS.user_id not in serialized
    assert "synthetic-pan" not in serialized


@pytest.mark.parametrize(
    "method,url",
    [
        ("POST", "https://protrade.jainam.in/omt/api-order-rest/v1/orders/placeorder"),
        ("POST", "https://protrade.jainam.in/omt/api-order-rest/v1/orders/cancel"),
        ("POST", "https://protrade.jainam.in/omt/api-order-rest/v1/orders/modify"),
        ("POST", "https://protrade.jainam.in/omt/api-order-rest/v1/orders/positions/sqroff"),
        ("GET", "https://attacker.invalid/omt/api-order-rest/v1/profile/"),
        ("GET", "http://protrade.jainam.in/omt/api-order-rest/v1/profile/"),
        ("GET", "https://protrade.jainam.in/omt/api-order-rest/v1/profile/?secret=x"),
    ],
)
def test_disallowed_requests_never_reach_transport(monkeypatch, method, url):
    transport = Mock()
    monkeypatch.setattr(requests.Session, "request", transport)
    with ReadOnlySession() as session:
        with pytest.raises(PermissionError):
            session.request(method, url)
    transport.assert_not_called()


def test_no_config_does_not_make_client():
    factory = Mock()
    assert Service(None, factory).account("funds")["error"] == "NOT_CONFIGURED"
    factory.assert_not_called()


@pytest.mark.parametrize(
    "status,expected",
    [
        (401, "SESSION_EXPIRED_OR_DENIED"),
        (403, "SESSION_EXPIRED_OR_DENIED"),
        (429, "RATE_LIMITED"),
        (500, "BROKER_ERROR"),
    ],
)
def test_error_bodies_are_never_exposed(monkeypatch, status, expected):
    monkeypatch.setattr(
        requests.Session,
        "request",
        lambda *a, **kw: response({"status": "error", "message": CREDS.user_session}, status),
    )
    result = Service(CREDS).account("funds")
    assert result["error"] == expected
    assert CREDS.user_session not in json.dumps(result)


def test_network_error_does_not_echo_sensitive_exception(monkeypatch):
    def fail(*a, **kw):
        raise requests.Timeout(CREDS.user_session)

    monkeypatch.setattr(requests.Session, "request", fail)
    result = Service(CREDS).account("funds")
    assert result["error"] == "NETWORK_ERROR" and CREDS.user_session not in str(result)


def test_history_uses_read_post(monkeypatch):
    def send(self, method, url, **kw):
        assert method == "POST" and url.endswith("/orders/history")
        assert kw["json"] == {"brokerOrderId": "synthetic-order"}
        return response({"status": "ok"})

    monkeypatch.setattr(requests.Session, "request", send)
    assert Service(CREDS).order_history("synthetic-order")["ok"]


def test_historical_input_and_millisecond_payload(monkeypatch):
    def send(self, method, url, **kw):
        assert method == "POST" and url.endswith("/chart/history")
        assert kw["json"]["from"] == "1700000000000"
        return response({"candles": []})

    monkeypatch.setattr(requests.Session, "request", send)
    service = Service(CREDS)
    assert service.historical("NSE", "123", "1", 1700000000000, 1700000060000)["ok"]
    assert service.historical("NSE", "123", "1", 2, 1)["error"] == "INVALID_REQUEST"
    assert service.historical("NSE", "123", "1", 1, 32 * 86400000)["error"] == "INVALID_REQUEST"
    assert service.historical("BAD", "123", "1", 1, 100)["error"] == "INVALID_REQUEST"


def test_master_search_bounds_and_token_normalization(monkeypatch):
    raw = b"Token,Symbol\n123,GOLD-TEST\n124,SILVER-TEST\n125,GOLD-SECOND\n"

    class Download:
        status_code = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return None

        def iter_content(self, size):
            yield raw

    def send(self, method, url, **kw):
        assert method == "GET" and url.endswith("/contract/MCX.csv")
        assert kw["allow_redirects"] is False
        return Download()

    monkeypatch.setattr(requests.Session, "request", send)
    result = Service(CREDS).search_contracts("MCX", "gold", 1)
    assert result["ok"]
    assert result["data"]["matches"] == [{"instrument_token": "123", "Symbol": "GOLD-TEST"}]
    assert not Service(CREDS).search_contracts("BAD", "gold", 1)["ok"]
    assert not Service(CREDS).search_contracts("MCX", "", 1)["ok"]
    assert not Service(CREDS).search_contracts("MCX", "gold", 51)["ok"]


def test_html_and_http200_error_gracefully_degrade(monkeypatch):
    r = response({"status": "error", "message": "synthetic-private-body"})
    monkeypatch.setattr(requests.Session, "request", lambda *a, **kw: r)
    assert Service(CREDS).account("funds")["error"] == "BROKER_ERROR"
    r._content = b"<html>not JSON</html>"
    assert Service(CREDS).account("funds")["error"] == "BROKER_ERROR"


def test_oversized_tool_result_rejected():
    client = Mock()
    client.funds.return_value = {"large": "a" * (1024 * 1024)}
    assert Service(CREDS, lambda **kw: client).account("funds")["error"] == "RESPONSE_TOO_LARGE"


def test_read_allowlist_has_no_mutation_paths():
    assert all(
        not any(term in path for term in ("placeorder", "/cancel", "/modify", "sqroff"))
        for _, path in READ_ROUTES
    )
    assert Client is not None
