"""Human-operated setup; no credential prompts are exposed as MCP tools."""

from __future__ import annotations

import argparse
import getpass
import json
import sys
import warnings
import webbrowser
from pathlib import Path

import requests
from jainam_api import Client, build_login_url

from jainam_mcp import __version__
from jainam_mcp.config import ConfigError, Credentials, default_path, load, save
from jainam_mcp.service import Service


def extract_session(value) -> str:
    """Only accept an unambiguous explicitly named userSession field."""
    found = set()

    def visit(item):
        if isinstance(item, dict):
            for key, child in item.items():
                if key.lower().replace("_", "") == "usersession" and isinstance(child, str) and child.strip():
                    found.add(child)
                elif isinstance(child, (dict, list)):
                    visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)

    visit(value)
    if len(found) != 1:
        raise ConfigError("No unique userSession found. Use configure with the session provided by Jainam.")
    return found.pop()


class LoginSession(requests.Session):
    def request(self, method, url, **kwargs):
        if method.upper() != "POST" or url != "https://protrade.jainam.in/omt/auth/sso/vendor/getUserDetails":
            raise PermissionError("Unsupported session-exchange endpoint.")
        kwargs["allow_redirects"] = False
        return super().request(method, url, **kwargs)


def configuration(client: str, config_path: Path | None = None) -> dict:
    args = ["-m", "jainam_mcp"]
    if config_path:
        args.extend(["--config", str(config_path.expanduser().resolve())])
    args.append("serve")
    server = {"command": sys.executable, "args": args}
    if client == "vscode":
        server["type"] = "stdio"
    return {"servers" if client == "vscode" else "mcpServers": {"jainam": server}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local read-only Jainam MCP Agent server")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--config", type=Path, help="Explicit local credentials file (before subcommand)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("serve", help="Run MCP over stdio; usually launched by your AI client")
    sub.add_parser("configure", help="Store an existing session using hidden terminal prompts")
    sub.add_parser("login", help="Open Jainam SSO and exchange a fresh auth code locally")
    doctor = sub.add_parser("doctor", help="Offline configuration check by default")
    doctor.add_argument("--online", action="store_true", help="Make one read-only funds request")
    client_config = sub.add_parser("client-config", help="Print credential-free client JSON")
    client_config.add_argument("client", choices=["claude", "vscode"])
    args = parser.parse_args(argv)
    path = args.config.expanduser() if args.config else None
    try:
        if args.command in {"configure", "login"}:
            if not sys.stdin.isatty():
                raise ConfigError("Use an interactive terminal; refusing visible credential input.")
            warnings.filterwarnings("error", category=getpass.GetPassWarning)
        if args.command == "client-config":
            print(json.dumps(configuration(args.client, path), indent=2))
            return 0
        if args.command == "configure":
            user_id = getpass.getpass("Jainam user ID (hidden): ").strip()
            session = getpass.getpass("Jainam user session (hidden): ").strip()
            destination = save(Credentials(user_id, session), path)
            print(f"Saved locally to {destination}. No credentials were printed.")
            print("Restart your MCP client after renewing a session.")
            return 0
        if args.command == "login":
            app_code = getpass.getpass("Your developer appCode (hidden): ").strip()
            print("Opening Jainam sign-in. Complete it using your registered callback URL.")
            if not webbrowser.open(build_login_url(app_code)):
                raise ConfigError(
                    "Browser could not open. Use your developer app's login URL, then configure."
                )
            user_id = getpass.getpass("userId from your callback (hidden): ").strip()
            auth_code = getpass.getpass("Fresh authCode from your callback (hidden): ").strip()
            api_secret = getpass.getpass("Your apiSecret (hidden, not saved): ").strip()
            with LoginSession() as transport:
                response = Client(session=transport).exchange_auth_code(user_id, auth_code, api_secret)
            destination = save(Credentials(user_id, extract_session(response)), path)
            print(f"Session saved locally to {destination}. Restart your MCP client.")
            return 0
        service = Service(load(path))
        if args.command == "doctor":
            report = service.status()
            report["credentials_file_present"] = (path or default_path()).exists()
            if args.online:
                result = service.account("funds")
                report["online_ok"] = result["ok"]
                if not result["ok"]:
                    report["error"] = result.get("error")
            print(json.dumps(report, indent=2))
            return 0 if report["credentials_configured"] and report.get("online_ok", True) else 1
        from jainam_mcp.server import create_server

        create_server(service).run(transport="stdio")
        return 0
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (EOFError, KeyboardInterrupt):
        print("Cancelled; no credentials were printed.", file=sys.stderr)
        return 130
    except Exception:
        print(
            "Operation failed. See docs/TROUBLESHOOTING.md. No raw broker errors are printed.",
            file=sys.stderr,
        )
        return 1
