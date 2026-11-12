# Claude Desktop

Complete [Getting started](GETTING_STARTED.md), including `doctor`, first.

1. In Claude Desktop open **Settings → Developer → Edit Config**.
2. In the project terminal run:

   ```sh
   python -m jainam_mcp client-config claude
   ```

3. Copy the generated `jainam` entry into the file's `mcpServers` object. Preserve existing servers. Do not add credentials to this JSON.
4. Save valid JSON, fully quit Claude, and reopen it.
5. Confirm the Jainam tools appear. Ask: “Call jainam_status.” Approve the tool if requested.

Example shape only; use your generated absolute Python path:

```json
{
  "mcpServers": {
    "jainam": {
      "command": "/absolute/path/jainam-mcp/.venv/bin/python",
      "args": ["-m", "jainam_mcp", "serve"]
    }
  }
}
```

On Windows the generated command ends in `.venv\\Scripts\\python.exe` with JSON escaping already handled. Do not use macOS paths on Windows.

For a custom local credential location, generate the entry using:

```sh
python -m jainam_mcp --config /absolute/private/credentials.json client-config claude
```

A success response with `credentials_configured: false` means the server launches but needs `configure`. Restart the server after changing a session. Claude may receive requested holdings, balances and trades; read its data-use settings.

Source: [MCP's official local-server guide](https://modelcontextprotocol.io/docs/develop/connect-local-servers). Client menus can change. This project has protocol-level tests; configuring a real Claude account is a user-side step.
