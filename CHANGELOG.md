# Changelog

## 0.1.2 — 2026-11-12

- Reject HTML, empty and unusable contract-master responses instead of reporting misleading empty matches.
- Include configured SDK session headers on contract reads; authenticated production access remains unverified without an account.
- Reject redirect responses as broker failures while continuing to disable redirect following.
- Correct online doctor output to indicate that a connection was attempted.
- Add configured-protocol coverage for all ten tools using synthetic network responses.
- Add fresh-wheel installation and generated-client-command smoke checks to every OS/Python CI combination.
- Publish an explicit validation report separating automated checks from real-account and AI-client UI validation.

## 0.1.1 — 2026-11-12

- Rename the public project/package to Jainam MCP Agent (`jainam-mcp-agent`).
- Preserve `jainam_mcp`, the `jainam-mcp` CLI and existing credential-file locations; add the new CLI alias.
- Add a visual prompt library for sector-wise donuts, acquisition-cost pies, holdings dashboards, positions and trade analysis.
- Expose five reusable, read-only analysis prompt templates through MCP.
- Explain client-side chart rendering, sector-mapping requirements, data coverage and P&L calculation limits.

## 0.1.0 — 2026-11-12

- Initial standalone stdio MCP server using the pinned Jainam ProTrade Python SDK.
- Ten read-only tools: configuration, profile, funds, holdings, positions, order/trade books, order history, contract search and historical candles.
- Human-operated hidden-prompt session configuration and browser SSO exchange.
- Credential-free client JSON generation and offline/optional online diagnostics.
- Read-endpoint HTTP allowlist, sanitized errors and response redaction.
- Beginner guides for macOS/Windows/Linux, Claude Desktop, VS Code and ChatGPT tunnel setup.
- Mocked protocol/HTTP tests, lint/build CI, dependency audit, credential scan and MIT license.

Known limits: no order execution, quote subscription/streaming, remote hosting, guaranteed API entitlement, or tested live client-account integration. Sessions require user renewal. Git is required for the pinned SDK dependency.
