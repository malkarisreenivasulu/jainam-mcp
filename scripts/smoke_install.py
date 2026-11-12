"""Verify an installed wheel in a fresh venv, outside the checkout and editable paths."""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
import venv
from pathlib import Path

SMOKE = r"""
import asyncio, json, os, subprocess, sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from jainam_mcp import __version__

async def main():
    folder=Path.cwd()
    for name in ('jainam-mcp-agent','jainam-mcp'):
        command=Path(sys.executable).parent/(name+'.exe' if os.name=='nt' else name)
        completed=subprocess.run([str(command),'--version'],capture_output=True,text=True,check=True)
        assert completed.stdout.strip()==__version__
    # These are the actual generated client launch commands, not hand-written equivalents.
    for client,key in [('claude','mcpServers'),('vscode','servers')]:
        config=json.loads(subprocess.check_output([
            sys.executable,'-m','jainam_mcp','--config',str(folder/'absent'),
            'client-config',client],text=True))
        launch=config[key]['jainam']
        parameters=StdioServerParameters(command=launch['command'],args=launch['args'],env=dict(os.environ))
        async with stdio_client(parameters) as (read,write):
            async with ClientSession(read,write) as session:
                await session.initialize()
                assert len((await session.list_tools()).tools)==10
                assert len((await session.list_prompts()).prompts)==5
                for prompt in (await session.list_prompts()).prompts:
                    assert (await session.get_prompt(prompt.name)).messages
                status=await session.call_tool('jainam_status',{})
                assert json.loads(status.content[0].text)['credentials_configured'] is False
                denied=await session.call_tool('jainam_funds',{})
                assert json.loads(denied.content[0].text)['error']=='NOT_CONFIGURED'
    print('Fresh-wheel smoke passed: CLI aliases, generated configurations, 10 tools, 5 prompts.')
asyncio.run(main())
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path)
    args = parser.parse_args()
    wheel = args.wheel.resolve(strict=True)
    clean = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("JAINAM_") and k not in {"PYTHONPATH", "PYTHONHOME"}
    }
    with tempfile.TemporaryDirectory(prefix="jainam-install-smoke-") as directory:
        root = Path(directory)
        venv.create(root / "venv", with_pip=True)
        python = root / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        subprocess.run([str(python), "-m", "pip", "install", str(wheel)], env=clean, check=True)
        subprocess.run([str(python), "-c", SMOKE], cwd=root, env=clean, check=True, timeout=120)


if __name__ == "__main__":
    main()
