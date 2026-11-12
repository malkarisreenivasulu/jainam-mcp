# What is tested, and what still needs your account

This report describes v0.1.2 validation on 12 November 2026. It is evidence of the checks below, not a promise that every broker account, provider outage or AI-client version will behave identically.

## Automated checks

- **61 offline tests** cover credentials/configuration, permissions, hidden input, CLI generation, read-only route restrictions, error redaction, input validation, prompts and protocol behavior.
- A real stdio MCP handshake discovers all ten tools and five prompts. Unconfigured calls fail explicitly.
- A configured protocol test traverses the production server, production adapter and pinned Jainam SDK for **all ten tools**, substituting synthetic HTTP responses only at the network boundary. It verifies successful response handling, credential redaction and contract-token normalization. These fixtures do **not** validate actual production broker schemas or entitlements.
- An attempted `place_order` MCP call is rejected because no such tool exists. Endpoint tests reject place/modify/cancel/square-off routes before network transport.
- Contract reads include the configured SDK authentication headers. HTML, empty or unusable contract CSV responses fail with `BROKER_ERROR` instead of appearing as successful empty searches.
- Redirect responses cannot appear as successful account reads. Redirect following remains disabled.
- Every supported OS/Python CI combination builds a wheel, creates a **new virtual environment**, installs that wheel without editable/source import paths, and launches both actual generated Claude/VS Code commands through an MCP client. The smoke check verifies both CLI aliases, tool/prompt discovery and expected unconfigured failures. It is not a GUI-client test.
- CI covers Windows, macOS and Linux on Python 3.11–3.14. See [current CI results](https://github.com/malkarisreenivasulu/jainam-mcp-agent/actions/workflows/ci.yml); only completed passing runs establish a result.
- Dependency audit, tracked-source scanning and Gitleaks Git-history scanning run separately. These are automated checks, not independent security certification.

## Public release checks

The public v0.1.1 tag was cloned from GitHub into a new directory following the documented clone step. Earlier wheel downloads were re-downloaded and checksum-verified. The new patch is built and checked as an installed wheel with the same automated smoke procedure. Release assets include SHA256 checksums; Git is required for the pinned public SDK dependency.

## Live broker observation

An **unauthenticated** GET to `https://protrade.jainam.in/contract/NSE.csv` returned HTTP 200 with HTML, not CSV, during this review. This is why v0.1.2 rejects web pages as unusable broker responses. It does not establish that adding authentication fixes the provider's endpoint, or that the current endpoint works for any particular account. The adapter now supplies its configured session headers, but a valid-session contract search is still a user-side verification step.

No ProTrade user session was configured in the review environment. Therefore **authenticated login, funds, holdings, positions, trade-book contents and production historical/contract data have not been validated against a real account**. No account data or credentials were published.

## Your final account checks

After following [Getting started](GETTING_STARTED.md):

```sh
python -m jainam_mcp doctor
python -m jainam_mcp doctor --online
```

The first checks local configuration. The second attempts a real, read-only funds request and reports `connection_tested: true` with `online_ok: true` only if the request succeeds. Neither prints financial contents or session values. If the account check fails, renew the session and review broker entitlement/connectivity; a passing install test cannot override a denied or unavailable API.

In your client, try `jainam_status`, one funds/holdings read, one small instrument search and one historical request using a verified token. Check the response's `ok` field; successful MCP transport does not mean the broker accepted a request. Compare returned quantities, units and totals with your broker account before using any analysis.

Claude Desktop/VS Code UI discovery, ChatGPT tunnel/account permissions, real SSO callbacks, session lifetime and client chart rendering are not automated end-to-end here. Follow the client guides and the broker's current documentation. If a contract request returns a broker error, do not treat it as “no such stock” or invent an instrument ID.
