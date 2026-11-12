import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from jainam_mcp.server import create_server
from jainam_mcp.service import Service

EXPECTED = {
    "jainam_status",
    "jainam_profile",
    "jainam_funds",
    "jainam_holdings",
    "jainam_positions",
    "jainam_order_book",
    "jainam_trade_book",
    "jainam_order_history",
    "jainam_search_instruments",
    "jainam_historical_candles",
}


def test_real_stdio_handshake_list_and_safe_calls(tmp_path):
    async def exercise():
        environment = {k: v for k, v in os.environ.items() if not k.startswith("JAINAM_")}
        parameters = StdioServerParameters(
            command=sys.executable,
            env=environment,
            args=["-m", "jainam_mcp", "--config", str(tmp_path / "absent"), "serve"],
        )
        async with stdio_client(parameters) as (read, write):
            async with ClientSession(read, write) as client:
                await client.initialize()
                listing = await client.list_tools()
                assert {tool.name for tool in listing.tools} == EXPECTED
                for tool in listing.tools:
                    assert tool.annotations.readOnlyHint is True
                    assert tool.annotations.destructiveHint is False
                    assert not any(
                        "secret" in key or "session" in key or "password" in key
                        for key in tool.inputSchema.get("properties", {})
                    )
                status = await client.call_tool("jainam_status", {})
                assert not status.isError
                payload = json.loads(status.content[0].text)
                assert payload["credentials_configured"] is False
                funds = await client.call_tool("jainam_funds", {})
                assert json.loads(funds.content[0].text)["error"] == "NOT_CONFIGURED"
                invalid = await client.call_tool(
                    "jainam_search_instruments", {"exchange": "BAD", "query": "x"}
                )
                assert invalid.isError

    asyncio.run(exercise())


def test_inprocess_schema_is_readonly_and_no_arbitrary_paths():
    async def exercise():
        tools = await create_server(Service(None)).list_tools()
        assert len(tools) == 10
        for tool in tools:
            schema = json.dumps(tool.inputSchema).lower()
            assert "env_file" not in schema and "url" not in schema and "file_path" not in schema

    asyncio.run(exercise())
