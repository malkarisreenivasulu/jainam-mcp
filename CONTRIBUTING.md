# Contributing

Use Python 3.11–3.14 and a separate virtual environment. This project is independent of KuberaOS and the maintainer's live trading scripts.

```sh
python -m pip install -e '.[dev]'
python -m pytest
python -m ruff check .
python -m build
python scripts/scan_secrets.py
```

Tests must be offline: synthetic IDs/sessions and mocked HTTP only. Never require CI secrets, a broker account or market hours. Add regression and failure-path tests for functional changes. Schema checks should confirm tool annotations and absence of trading/credential tools. Preserve stdio output: stdout is MCP protocol only while serving; diagnostics go to stderr.

API behavior comes from the pinned public Jainam Python SDK and broker documentation. Update docs and compatibility tests when changing the pinned dependency. Do not add live execution tools, arbitrary URLs/paths, callback listeners, automatic login/password collection or account-protection layers as incidental changes.

## Releases

1. Update version, changelog and current client-documentation links.
2. Run tests, lint, dependency audit and package build on supported Python versions. Resolve actionable failures before releasing.
3. Inspect the **complete tracked file list and both wheel/sdist contents**, not only `.gitignore`.
4. Run the repository scanner and a real secret scanner such as Gitleaks on staged content/history. Review findings without printing the secret value.
5. Check no real credentials, `.env`, logs, token/session caches, local paths identifying the maintainer's machine or private account data appear in source, Git history or artifacts.
6. Tag the reviewed commit. Publish source and built artifacts on GitHub. PyPI upload is a separate action; this project currently installs its pinned SDK from GitHub and requires Git.
7. Verify the hosted source, downloadable release and public CI results. CI is evidence for the platforms it actually ran on, not universal compatibility.

## Architecture

`config.py` owns local secrets; `cli.py` is human-operated setup; `service.py` explicitly adapts read SDK calls and redacts responses; `server.py` registers typed MCP tools. `scripts/scan_secrets.py` examines tracked source without displaying matching values. Avoid copying any existing personal project's configuration or deployment files.

MIT contributions are welcome. Keep changes small and document limits honestly.
