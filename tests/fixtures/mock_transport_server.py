"""Test-only broker response fixture. Never used by the production CLI."""

import json
from unittest.mock import patch
from urllib.parse import urlsplit

import requests

from jainam_mcp.cli import main


def broker_response(self, method, url, **kwargs):
    parsed = urlsplit(url)
    assert parsed.netloc == "protrade.jainam.in"
    assert kwargs["allow_redirects"] is False
    assert kwargs["headers"]["token"] == "synthetic-session-not-real"
    response = requests.Response()
    response.status_code = 200
    response._content_consumed = True
    if parsed.path == "/contract/NSE.csv":
        response.headers["Content-Type"] = "text/csv"
        response._content = b"Token,Symbol,Exchange\n123,DEMO-TEST,NSE\n"
        return response
    response.headers["Content-Type"] = "application/json"
    payload = {"status": "ok", "data": {"synthetic": True, "userSession": "synthetic-session-not-real"}}
    if parsed.path.endswith("/profile/"):
        payload["data"]["email"] = "synthetic@example.invalid"
    elif parsed.path.endswith("/limits/"):
        payload["data"]["availableFunds"] = 1000
    elif "/holdings/" in parsed.path:
        payload["data"]["holdings"] = [{"symbol": "DEMO-TEST", "quantity": 5}]
    elif parsed.path.endswith("/positions"):
        payload["data"]["positions"] = []
    elif parsed.path.endswith("/orders/book"):
        payload["data"]["orders"] = []
    elif parsed.path.endswith("/orders/trades"):
        payload["data"]["trades"] = []
    elif parsed.path.endswith("/orders/history"):
        assert kwargs["json"]["brokerOrderId"] == "synthetic-order"
        payload["data"]["history"] = []
    elif parsed.path == "/chart/history":
        assert kwargs["json"]["token"] == "123"
        payload["data"]["candles"] = []
    else:
        raise AssertionError("Unexpected endpoint in test fixture")
    response._content = json.dumps(payload).encode()
    return response


if __name__ == "__main__":
    with patch.object(requests.Session, "request", broker_response):
        raise SystemExit(main())
