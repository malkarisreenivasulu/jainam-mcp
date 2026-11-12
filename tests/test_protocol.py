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
                prompts = await client.list_prompts()
                assert {item.name for item in prompts.prompts} == {
                    "holdings_dashboard",
                    "positions_review",
                    "trade_journal_review",
                    "account_reconciliation",
                    "historical_chart",
                }
                prompt = await client.get_prompt("holdings_dashboard")
                assert "holdings dashboard" in prompt.messages[0].content.text
                assert "sector" in prompt.messages[0].content.text.lower()
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


def test_prompt_retrieval_never_reads_account_data():
    from unittest.mock import Mock

    service = Service(None)
    service.account = Mock(side_effect=AssertionError("Prompt retrieval must not read accounts"))
    service.search_contracts = Mock(side_effect=AssertionError("Prompt retrieval must not fetch masters"))
    service.historical = Mock(side_effect=AssertionError("Prompt retrieval must not fetch candles"))

    async def exercise():
        import re

        server = create_server(service)
        prompts = await server.list_prompts()
        assert len(prompts) == 5
        for prompt in prompts:
            result = await server.get_prompt(prompt.name)
            text = result.messages[0].content.text
            assert "read-only" in text
            assert "missing" in text.lower()
            assert set(re.findall(r"\bjainam_[a-z_]+", text)).issubset(EXPECTED)
        service.account.assert_not_called()
        service.search_contracts.assert_not_called()
        service.historical.assert_not_called()

    asyncio.run(exercise())
