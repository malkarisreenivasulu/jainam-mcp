# Security policy

## Credential handling

This project is distributed as source. It contains **no maintainer broker credentials**, personal token caches, account exports or private KuberaOS files. Each user supplies their own credentials locally.

- No credentials are passed as MCP tool arguments or returned by the configuration-status tool.
- `configure` and `login` use hidden terminal input, not command-line secret arguments. They must be run by a human in a trusted local terminal.
- The saved session is plaintext outside the checkout: POSIX file mode 0600, with a newly created final directory mode 0700. On Windows use private account ACLs; POSIX modes do not establish equivalent ACL guarantees.
- `login` keeps app secrets/auth codes in process memory only; only user ID/session are persisted. Python cannot promise immediate memory zeroization.
- Environment variables override the file only when the complete pair is provided. This server does not discover `.env` or arbitrary token files.
- Broker errors are converted to stable sanitized codes, not raw exception text or HTTP response bodies. Successful results redact common secret/contact identifiers and the configured credential strings. Redaction is defensive and cannot guarantee removal of all private financial/identity fields in arbitrary broker data.
- The SDK dependency includes trading methods, but this server registers only ten read tools. An explicit method/path/origin allowlist rejects all other SDK HTTP calls. There are no order placement, modify, cancel, square-off or generic HTTP MCP tools.
- HTTPS verification stays enabled. Redirects are disabled to avoid forwarding broker credentials. No hard-coded DNS overrides, private feed endpoints, access passwords or maintainer IPs are included.

## Trust boundaries

Stdio is the only server transport. It runs as your local OS user, has no login accounts or public listener, and is not a hosted multi-user app. Do not share one person's configured server with other users. A client, local administrator or compromised OS that can access your environment/files can access your session; read-only MCP does not make a stolen broker session read-only.

Account results intentionally cross into your chosen AI client when called. Balances, holdings, orders and trades are private data even when session fields are removed. Review that provider's privacy/retention settings and tool permissions. Treat broker text/contract names as data, not executable instructions.

ChatGPT tunnels are an optional separate, user-managed connection. Follow OpenAI's access controls and secret handling. Do not turn this server into an unauthenticated public endpoint. This release does not implement remote OAuth, network hosting, background services or telemetry.

The repository's synthetic tests, scanner and CI reduce accidental disclosure; they are not an independent penetration test, certification, or promise of defect-free code. No real-account/client UI integration is implied by mocked tests.

## Reporting a vulnerability

Use the repository's private **Security → Report a vulnerability** feature when available:
https://github.com/malkarisreenivasulu/jainam-mcp/security/advisories/new

Do not disclose credentials in public issues. If a credential leaks, revoke/rotate it with Jainam immediately; deleting a Git commit is not enough. For a non-sensitive bug use the issue tracker with sanitized error codes.

Version 0.1.x is the currently maintained series. No guaranteed response SLA is offered.
