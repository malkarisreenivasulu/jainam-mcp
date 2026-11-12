# Jainam MCP Agent

[![CI](https://github.com/malkarisreenivasulu/jainam-mcp-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/malkarisreenivasulu/jainam-mcp-agent/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Connect Claude Desktop, VS Code Copilot, or a supported ChatGPT tunnel to **your own Jainam account**, using a local, read-only Model Context Protocol server.

**Developed by Sreenivasulu Malkari.** Built on [Jainam API Python](https://github.com/malkarisreenivasulu/jainam-api-python) and the official MCP Python SDK. Independent community software, not an official Jainam product.

| You can ask | What the server does |
|---|---|
| “Show my funds and holdings” | Reads your account data |
| “Summarize my current positions” | Reads positions; does not close them |
| “Show my existing orders and trades” | Reads broker books and order history |
| “Find GOLD contracts on MCX” | Searches the broker's current contract master |
| “Fetch historical candles for this token” | Reads historical data, subject to broker availability |

**No order placement, modification, cancellation, square-off, autonomous trading, or generic HTTP tool.** No subscription, multicast server, Redis, Docker, or KuberaOS installation is needed. Live streaming and live quotes are not exposed. Five reusable MCP prompt templates help clients structure analysis.

## Copy a prompt. See your portfolio clearly.

After connecting your client, try:

> **Sector-wise donut:** “Show my holdings by sector as a donut chart, weighted by current market value. Use only sourced sector classifications, keep unmapped stocks as Unclassified, and show INR values, percentages and data coverage.”

> **Investment-wise pie:** “Show my stock-wise invested capital as a pie chart using acquisition cost. Show the top 8 stocks plus Other, total invested capital and an underlying table. Do not substitute market value for invested cost.”

> **Holdings dashboard:** “Create KPI cards for invested capital, market value and unrealized P&L, a stock-allocation donut, signed P&L bars and a holdings table. Label missing data and snapshot time.”

> **Positions:** “Show my existing positions as a signed unrealized-P&L bar chart. Separate realized and unrealized P&L, and verify contract units before calculating futures or options exposure.”

> **Trades:** “Show traded turnover by symbol as a donut and fill counts by hour as bars. Count fills, orders and completed round trips separately. Do not treat turnover as profit.”

**[Open the full visual prompt library →](docs/EXAMPLE_PROMPTS.md)** for copy-and-paste prompts, sector/cost/market-value comparisons, treemaps, reconciliation and private HTML reports.

The MCP server reads data; your AI client renders charts if supported. Sector charts require returned classifications or a sourced mapping you provide. Charts cannot establish missing realized P&L, charges or contract multipliers.

## Start here

1. Install **Python 3.11–3.14** and **Git**.
2. Follow [Getting started](docs/GETTING_STARTED.md) for macOS, Windows or Linux.
3. Connect [Claude Desktop](docs/CLAUDE.md), [VS Code](docs/VSCODE.md), or [ChatGPT](docs/CHATGPT.md).
4. Ask: **“Use jainam_status and tell me whether it is configured.”** This first call is offline.

If you already have Python and Git, these commands install the tagged release in an isolated folder:

```sh
git clone --branch v0.1.2 https://github.com/malkarisreenivasulu/jainam-mcp-agent.git
cd jainam-mcp-agent
python3 -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
python -m pip install .
python -m jainam_mcp configure
python -m jainam_mcp doctor
```

`configure` asks for your user ID and existing user session **in hidden terminal prompts**. If you only have developer keys, use the documented [browser authorization flow](docs/GETTING_STARTED.md#sign-in-with-your-own-developer-app). An app key alone is not an authenticated session.

Generate your client configuration rather than editing Python paths by hand:

```sh
python -m jainam_mcp client-config claude
python -m jainam_mcp client-config vscode
```

The output contains a local executable path and launch arguments, **not credentials**. Merge it into your client's configuration using its guide. ChatGPT does not use this desktop JSON; follow its separate tunnel guide.

## Verification before you use real account data

See the [validation report](docs/VALIDATION.md) for exactly what is tested.
The suite covers all ten tools over MCP with synthetic broker responses, and CI
installs the built wheel in fresh environments across Windows, macOS and Linux.
These checks do **not** prove real Jainam login, API entitlement, production data
schemas or a particular client's chart rendering. Run `doctor --online` and verify
a small real read with your own account after setup. A broker HTML error page is
reported as an error, never a successful empty instrument search.

## Privacy and limitations

Credentials stay in your local environment or private credentials file. This repository contains no maintainer account credentials. The server never returns the configured session token, redacts common identifiers and secret fields, and does not print raw broker errors. Account balances, holdings and trades **are sent to your chosen AI client when you request them**; they may be processed by that client's provider. Review its privacy settings. Local execution does not mean all data stays offline.

You need your own Jainam account, developer application, API entitlement and valid session. Broker access, rate limits and data availability are controlled by Jainam; availability to every account is not guaranteed. This release uses **ProTrade Open API v2**, not XTS/JLite APIs. It is not a public hosted service, financial adviser, or a guarantee of price/data accuracy.

## Documentation

- [Beginner setup and sign-in](docs/GETTING_STARTED.md)
- [Claude Desktop](docs/CLAUDE.md) · [VS Code](docs/VSCODE.md) · [ChatGPT](docs/CHATGPT.md)
- [Visual example prompts](docs/EXAMPLE_PROMPTS.md)
- [Tools and response formats](docs/TOOLS.md)
- [Testing and validation limits](docs/VALIDATION.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Security policy](SECURITY.md) · [Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md)

## Upgrade from v0.1.0

The repository/package is now **jainam-mcp-agent**. The `jainam_mcp` Python module,
legacy `jainam-mcp` command and existing `~/.config/jainam-mcp/credentials.json`
location remain compatible. The new `jainam-mcp-agent` command is an alias for the
same CLI. Existing client JSON does not need a module or credentials-path change.
When replacing an installed v0.1.0 package in the same environment, uninstall
`jainam-mcp` first, then install this renamed package to avoid overlapping package
files. Keep your private credentials file. New clone folders use
`jainam-mcp-agent`; generate client JSON with that install's Python. Old GitHub repository URLs redirect, but update remotes to the new URL.

## Development

```sh
python -m pip install -e '.[dev]'
python -m pytest
python -m ruff check .
python -m build
python scripts/scan_secrets.py
```

Tests use synthetic credentials and mocked HTTP. They do not log into a real account or place orders. See [Contributing](CONTRIBUTING.md) for the release checklist and tested boundaries.

MIT licensed. Jainam and ProTrade are trademarks of their respective owners. No affiliation or endorsement is implied. Not investment advice.
