"""Full MCP -> production service -> pinned SDK -> synthetic HTTP responses."""

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def test_all_tools_with_configured_credentials_through_real_protocol(tmp_path):
    async def exercise():
        environment = {k: v for k, v in os.environ.items() if not k.startswith("JAINAM_")}
        environment.update(JAINAM_USER_ID="synthetic-user", JAINAM_USER_SESSION="synthetic-session-not-real")
        fixture = Path(__file__).parent / "fixtures" / "mock_transport_server.py"
        parameters = StdioServerParameters(
            command=sys.executable,
            env=environment,
            args=[str(fixture), "--config", str(tmp_path / "absent"), "serve"],
        )
        calls = [
            ("jainam_status", {}),
            ("jainam_profile", {}),
            ("jainam_funds", {}),
            ("jainam_holdings", {}),
            ("jainam_positions", {}),
            ("jainam_order_book", {}),
            ("jainam_trade_book", {}),
            ("jainam_order_history", {"broker_order_id": "synthetic-order"}),
            ("jainam_search_instruments", {"exchange": "NSE", "query": "DEMO", "limit": 5}),
            (
                "jainam_historical_candles",
                {
                    "exchange": "NSE",
                    "token": "123",
                    "resolution": "1",
                    "from_ms": 1700000000000,
                    "to_ms": 1700000060000,
                },
            ),
        ]
        async with stdio_client(parameters) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                for name, arguments in calls:
                    result = await session.call_tool(name, arguments)
                    assert not result.isError, name
                    payload = json.loads(result.content[0].text)
                    assert payload["ok"], (name, payload)
                    assert "synthetic-session-not-real" not in str(payload)
                    assert "synthetic@example.invalid" not in str(payload)
                    if name == "jainam_search_instruments":
                        assert payload["data"]["matches"][0]["instrument_token"] == "123"
                forbidden = await session.call_tool("place_order", {})
                assert forbidden.isError

    asyncio.run(exercise())
