# VS Code with Copilot

Complete [Getting started](GETTING_STARTED.md). Use a current VS Code version and an MCP-capable Copilot agent setup enabled for your account/workspace.

1. Run this with the installed environment's Python:

   ```sh
   python -m jainam_mcp client-config vscode
   ```

2. Open **MCP: Open User Configuration** from the Command Palette, or create `.vscode/mcp.json` for a workspace. Merge the generated `jainam` entry under `servers`, preserving existing entries.
3. Review and trust the launch command when VS Code asks. Start the server using **MCP: List Servers**.
4. In Copilot's agent chat enable the Jainam tools and ask: “Call jainam_status.”

Example structure:

```json
{
  "servers": {
    "jainam": {
      "type": "stdio",
      "command": "/absolute/path/jainam-mcp-agent/.venv/bin/python",
      "args": ["-m", "jainam_mcp", "serve"]
    }
  }
}
```

Use generated paths on Windows. Do not put secrets in a committed workspace file. User-level configuration and a credentials file outside your repository avoid accidental sharing. Remote SSH, containers and WSL launch servers in their own environment; install/configure there if that is where Copilot runs the command.

Renewing credentials requires an MCP server restart. Use VS Code's MCP output logs for launch errors, but redact any private data before sharing them.

Sources: [official add/use guide](https://code.visualstudio.com/docs/agent-customization/mcp-servers), [configuration reference](https://code.visualstudio.com/docs/reference/mcp-configuration). Account access and UI names may change. The generated JSON is tested; real-client acceptance is a user-side check.
