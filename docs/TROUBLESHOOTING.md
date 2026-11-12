# Troubleshooting

Start with `python -m jainam_mcp doctor`. To test broker connectivity explicitly, add `--online`.

| Symptom | Action |
|---|---|
| Python/Git not found | Install prerequisites, reopen Terminal; on Windows try `py -3` |
| Unsupported Python | Create a new venv with Python 3.11–3.14; do not reuse another project's old venv |
| Installation cannot fetch SDK | Git and outbound GitHub access are required. Check your proxy/certificates; never disable TLS verification |
| `No module named jainam_mcp` | Use this project's `.venv` Python and install with `python -m pip install .` |
| `NOT_CONFIGURED` | Run `configure` in your own terminal under the same OS user as the client |
| Partial environment configuration | Set both JAINAM variables or unset both; no partial file fallback |
| `SESSION_EXPIRED_OR_DENIED` | Renew your own session using login/configure and restart every MCP client process |
| `BROKER_ERROR` | Check account entitlement and current API docs; a broker may report errors with HTTP 200 |
| `RATE_LIMITED` | Stop repeated requests and retry later according to broker guidance |
| `NETWORK_ERROR` | Check internet, Jainam availability and certificates; no DNS/IP patches are installed |
| No candles | Verify current token, exchange, resolution, millisecond timestamps and broker data availability |
| No instrument matches | Use a shorter query and correct exchange; contract masters change |
| POSIX permission error | Run `chmod 600` on your private credentials file, not on a shared directory |
| Server is silent in Terminal | Normal for stdio MCP: the AI client must launch it; Ctrl+C exits |
| Tools absent in Claude/VS Code | Generate config with the correct venv Python, merge valid JSON, restart server/client and review tool selection |
| ChatGPT cannot see a tunnel | Check its organization/workspace association, access and running tunnel client using OpenAI's guide |

`jainam_status` is an offline configuration check. Only `doctor --online` or a broker-reading tool verifies connectivity. Never treat `credentials_configured: true` as proof of a valid session.

`login` needs your existing registered callback; it does not capture redirects itself. If the exchange response cannot be recognized, the command fails safely without printing it. Use Jainam's documented process to obtain a session and run `configure`.

When reporting a bug include OS, Python/package versions, failing tool name and the sanitized error code. Do not include `.env`, credentials files, broker HTTP bodies/headers, full callback URLs, account screenshots or raw financial results. Never paste secrets into a GitHub issue.
