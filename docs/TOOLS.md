# Tool reference

All ten tools declare MCP read-only, non-destructive, idempotent annotations. Annotations are hints; the explicit SDK/HTTP read allowlist is the implementation boundary. No trading-mutation tool or arbitrary request tool is registered.

| Tool | Inputs | Result |
|---|---|---|
| `jainam_status` | None | Configuration presence and version; no network |
| `jainam_profile` | None | Profile with common identifiers/contact fields redacted |
| `jainam_funds` | None | Broker funds/limits |
| `jainam_holdings` | `product_type`: `cnc` (default), `mtf`, `mis` | Broker holdings |
| `jainam_positions` | None | Current positions |
| `jainam_order_book` | None | Existing orders |
| `jainam_trade_book` | None | Broker trade book |
| `jainam_order_history` | Existing `broker_order_id`, 1–100 characters | Existing order's history |
| `jainam_search_instruments` | `exchange`, `query`, `limit` (1–50, default 20) | Bounded text matches from current contract CSV |
| `jainam_historical_candles` | `exchange`, `token`, `resolution`, `from_ms`, `to_ms` | Broker historical response |

Exchanges: `NSE`, `NFO`, `CDS`, `BSE`, `BFO`, `BCD`, `MCX`, `INDICES`. Broker availability varies by endpoint and entitlement. A listed exchange is a validated input, not a guarantee of historical support.

Instrument IDs must come from a current broker master. A matching name alone does not establish tradability or liquidity. Contract-search rows rename `token` to `instrument_token` so public instrument IDs remain usable. Ambiguous `token` fields in other broker responses are redacted. Use clearly named instrument-ID fields where present; never substitute a session token for an instrument ID.

Historical times are **Unix milliseconds**, not seconds. `to_ms` must exceed `from_ms`, with at most 31 days per request. Resolution values follow the broker: pass the value it currently documents; the SDK notes documentation inconsistencies, so this package does not invent a universal resolution list. The master download is capped at 25 MiB, matches at 50, and serialized returned data at 1 MiB. Contract search fetches afresh; avoid repeated polling. Broker requests time out after 20 seconds. No automatic retries or live streams are started.

Success:

```json
{"ok": true, "data": {"example": "broker data, shape varies"}}
```

Failure:

```json
{"ok": false, "error": "SESSION_EXPIRED_OR_DENIED", "message": "Jainam could not complete the read request.", "http_status": 401}
```

Other errors include `NOT_CONFIGURED`, `RATE_LIMITED`, `NETWORK_ERROR`, `INVALID_REQUEST`, `RESPONSE_TOO_LARGE`, `BROKER_ERROR`, and `INTERNAL_ERROR`. MCP schema validation can reject malformed inputs before the service runs. Error messages deliberately omit raw broker exception text and response bodies. HTTP 200 responses marked as errors by the SDK are also failures, but session expiry in that shape may appear as `BROKER_ERROR`; renew the session and check Jainam's guidance.

Balances, holdings, orders and P&L fields are broker data, not computed predictions. Currency, units, timestamps and realized/unrealized definitions follow the response; do not invent missing values. Tool responses can contain private financial information despite credential redaction.


## Analysis prompts and charts

Five MCP prompt templates are available separately from the ten read-only tools:
`holdings_dashboard`, `positions_review`, `trade_journal_review`,
`account_reconciliation` and `historical_chart`. They provide analysis instructions;
they neither fetch data automatically nor change account state. Use the
[visual prompt library](EXAMPLE_PROMPTS.md) for sector-wise donuts, investment-wise
pies, stock-allocation views, positions/trade charts and report examples.
Rendering and optional local file creation are client capabilities, not additional
MCP tools exposed by this server. Sector enrichment is not built into the API
adapter and must never be guessed.
