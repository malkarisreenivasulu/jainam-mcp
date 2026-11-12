# Jainam MCP

[![CI](https://github.com/malkarisreenivasulu/jainam-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/malkarisreenivasulu/jainam-mcp/actions/workflows/ci.yml)
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

**No order placement, modification, cancellation, square-off, autonomous trading, or generic HTTP tool.** No subscription, multicast server, Redis, Docker, or KuberaOS installation is needed. Live streaming and live quotes are not exposed in this first release.

## Start here

1. Install **Python 3.11–3.14** and **Git**.
2. Follow [Getting started](docs/GETTING_STARTED.md) for macOS, Windows or Linux.
3. Connect [Claude Desktop](docs/CLAUDE.md), [VS Code](docs/VSCODE.md), or [ChatGPT](docs/CHATGPT.md).
4. Ask: **“Use jainam_status and tell me whether it is configured.”** This first call is offline.

If you already have Python and Git, these commands install the tagged release in an isolated folder:

```sh
git clone --branch v0.1.0 https://github.com/malkarisreenivasulu/jainam-mcp.git
cd jainam-mcp
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

## Privacy and limitations

Credentials stay in your local environment or private credentials file. This repository contains no maintainer account credentials. The server never returns the configured session token, redacts common identifiers and secret fields, and does not print raw broker errors. Account balances, holdings and trades **are sent to your chosen AI client when you request them**; they may be processed by that client's provider. Review its privacy settings. Local execution does not mean all data stays offline.

You need your own Jainam account, developer application, API entitlement and valid session. Broker access, rate limits and data availability are controlled by Jainam; availability to every account is not guaranteed. This release uses **ProTrade Open API v2**, not XTS/JLite APIs. It is not a public hosted service, financial adviser, or a guarantee of price/data accuracy.

## Documentation

- [Beginner setup and sign-in](docs/GETTING_STARTED.md)
- [Claude Desktop](docs/CLAUDE.md) · [VS Code](docs/VSCODE.md) · [ChatGPT](docs/CHATGPT.md)
- [Tools and response formats](docs/TOOLS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Security policy](SECURITY.md) · [Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md)

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
