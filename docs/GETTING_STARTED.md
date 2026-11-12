# Set up Jainam MCP on your computer

You do not need to be a programmer. Do each step in order. Never paste your API secret, session or authorization code into an AI conversation, GitHub issue or screenshot.

## 1. What you need

- A Jainam account with access to [ProTrade developer applications](https://protrade.jainam.in/developers). Check API eligibility and charges directly with Jainam.
- Python 3.11, 3.12, 3.13 or 3.14 from [python.org](https://www.python.org/downloads/). On Windows select **Add Python to PATH**.
- [Git](https://git-scm.com/downloads), including on Windows: installation fetches the pinned SDK from GitHub.
- Claude Desktop or VS Code with an MCP-capable Copilot setup. ChatGPT has additional tunnel/workspace requirements explained separately.

Verify in Terminal (macOS/Linux) or PowerShell (Windows):

```sh
python --version
git --version
```

If `python` is not found on macOS/Linux, try `python3`. On Windows try `py -3`. Use the same Python throughout. Stop if it is older than 3.11.

## 2. Download the released source

```sh
git clone --branch v0.1.0 https://github.com/malkarisreenivasulu/jainam-mcp.git
cd jainam-mcp
```

A detached-HEAD message from cloning a release tag is normal. You are using a fixed release rather than a moving development branch.

## 3. Install in its own environment

macOS/Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

Windows PowerShell (activation is not necessary):

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
```

For subsequent Windows commands in this guide, use `.\.venv\Scripts\python.exe` wherever you see `python`. This also avoids PowerShell script-execution-policy issues. Never install this using `sudo pip`.

The installation downloads the MCP SDK and the maintainer's public Jainam Python SDK, pinned to the commit behind v0.1.1. Nothing is read from the maintainer's private computer or from your existing project `.env` files.

## 4. Choose one sign-in method

A **user session** is a secret temporary credential issued by Jainam. Your developer **appCode** identifies an app; **apiSecret** signs its login exchange. They are different from the issued session.

### If you already have a valid session

```sh
python -m jainam_mcp configure
```

At the hidden prompts enter your Jainam user ID and user session. Input is deliberately not echoed. Paste only the session value, not an entire response or callback URL. Credentials are saved outside this repository:

- macOS/Linux: `~/.config/jainam-mcp/credentials.json`
- Windows: `%APPDATA%\jainam-mcp\credentials.json` when APPDATA is available; otherwise `~/.config/jainam-mcp/credentials.json`.

On POSIX the new file is mode `0600`. On Windows protect it with your user account's normal private file permissions; POSIX modes are not Windows ACL guarantees. This is plaintext local storage, not a vault or encryption. Prefer a non-synced private location. See [Security](../SECURITY.md).

### Sign in with your own developer app

1. Sign in to the [Jainam developer portal](https://protrade.jainam.in/developers).
2. Follow its application-creation flow, register a callback URL you control, and note your `appCode` and `apiSecret`. The package does not create an account or provision API access for you.
3. Run:

   ```sh
   python -m jainam_mcp login
   ```

4. Enter your appCode at the hidden prompt. The command opens Jainam's sign-in page in your browser.
5. Complete Jainam's own login. Observe your registered redirect/callback and obtain its `userId` and fresh `authCode`. Do not send these to another person or this project's maintainer.
6. Return to Terminal. Enter userId, authCode and apiSecret at the hidden prompts. The command exchanges the code through the public Python SDK. It saves only userId and userSession, not the API secret or authorization code.

The project does not run a callback web server, collect broker passwords, or bypass MFA. Your callback must already be reachable and under your control. If Jainam returns a different response shape without a unique `userSession`, the command stops without dumping the response; obtain your session through Jainam's documented flow and use `configure`. Expired/used codes require fresh authorization. See the [SDK guide](https://github.com/malkarisreenivasulu/jainam-api-python/blob/v0.1.1/docs/GETTING_STARTED.md) and [broker API documentation](https://protrade.jainam.in/open-apidocs/v2/index.html).

### Advanced: environment variables

If both `JAINAM_USER_ID` and `JAINAM_USER_SESSION` are present, they override the file. A partial pair fails explicitly; it will not combine one account's ID with another session. Use your local secret manager to set them. The server never auto-loads `.env`, and examples deliberately contain no secret values. Clear old variables if changing back to file configuration.

## 5. Check setup

```sh
python -m jainam_mcp doctor
```

Expected: `credentials_configured: true`, `connection_tested: false`. This proves configuration can load, **not** that Jainam accepts the session.

Optionally verify the session using one read-only funds request:

```sh
python -m jainam_mcp doctor --online
```

Expected: `online_ok: true`. The diagnostic does not print funds, session tokens, account IDs or broker error bodies. If it fails, use [Troubleshooting](TROUBLESHOOTING.md).

## 6. Connect your AI client

Choose [Claude](CLAUDE.md), [VS Code](VSCODE.md), or [ChatGPT](CHATGPT.md). Run the client-config command with **this environment's Python** so it generates the right absolute path.

## 7. First requests

- “Use jainam_status to check configuration.”
- “Using Jainam tools, summarize my holdings. Do not make recommendations.”
- “Show my existing positions and explain the returned fields.”
- “Search MCX contracts containing GOLD, limit 5.”

If you run `serve` yourself, a quiet terminal is normal: it waits for MCP protocol messages from a client. Do not type secrets into it. Ctrl+C stops it.

## Renew a session / remove the project

When the broker expires a session, rerun `login` or `configure`, then **restart the MCP server in each client**. Sessions load once per server process. Expiry is set by Jainam, not promised by this project.

To remove it, delete the client's `jainam` entry and the local credentials file, revoke the session/app at Jainam where available, then delete the project folder. Uninstalling the Python package alone does not revoke a broker session.
