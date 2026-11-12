# Changelog

## 0.1.0 — 2026-11-12

- Initial standalone stdio MCP server using the pinned Jainam ProTrade Python SDK.
- Ten read-only tools: configuration, profile, funds, holdings, positions, order/trade books, order history, contract search and historical candles.
- Human-operated hidden-prompt session configuration and browser SSO exchange.
- Credential-free client JSON generation and offline/optional online diagnostics.
- Read-endpoint HTTP allowlist, sanitized errors and response redaction.
- Beginner guides for macOS/Windows/Linux, Claude Desktop, VS Code and ChatGPT tunnel setup.
- Mocked protocol/HTTP tests, lint/build CI, dependency audit, credential scan and MIT license.

Known limits: no order execution, quote subscription/streaming, remote hosting, guaranteed API entitlement, or tested live client-account integration. Sessions require user renewal. Git is required for the pinned SDK dependency.
