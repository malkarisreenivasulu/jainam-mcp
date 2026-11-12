# ChatGPT: connect your private local server

ChatGPT does not launch the Claude/VS Code JSON configuration. OpenAI documents **Secure MCP Tunnel** for private stdio servers. Access depends on your account, workspace and tunnel permissions; there is no universal one-click setup.

1. Finish [local setup](GETTING_STARTED.md) and `doctor`.
2. Follow [OpenAI's tunnel guide](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels): obtain `tunnel-client` from its official link, a tunnel ID, runtime key, and the required organization/workspace associations.
3. Supply the runtime key privately as instructed there. Never commit it or paste it into chat.
4. Configure the local stdio command using your installed Python:

   ```sh
   tunnel-client init --sample sample_mcp_stdio_local --profile jainam \
     --tunnel-id YOUR_TUNNEL_ID \
     --mcp-command "/absolute/path/jainam-mcp-agent/.venv/bin/python -m jainam_mcp serve"
   tunnel-client doctor --profile jainam --explain
   tunnel-client run --profile jainam
   ```

5. Keep the client running. In ChatGPT's custom MCP setup choose **Tunnel**, select the associated tunnel, review access, and test `jainam_status`.

Use official CLI help for Windows quoting and current UI names. Credentials remain locally configured; requested financial data crosses the tunnel to ChatGPT. This project does not create tunnels or publish a hosted ChatGPT plugin. If tunnel access is unavailable, use Claude or VS Code. Live ChatGPT integration has not been verified by this project's tests.
