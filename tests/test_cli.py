import json
from unittest.mock import Mock

import pytest

from jainam_mcp import cli
from jainam_mcp.config import ConfigError, load


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    monkeypatch.delenv("JAINAM_USER_ID", raising=False)
    monkeypatch.delenv("JAINAM_USER_SESSION", raising=False)
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True)


def test_configure_prompts_locally_without_printing_secrets(tmp_path, monkeypatch, capsys):
    answers = iter(["synthetic-user", "synthetic-session-not-real"])
    monkeypatch.setattr(cli.getpass, "getpass", lambda *a: next(answers))
    path = tmp_path / "credentials.json"
    assert cli.main(["--config", str(path), "configure"]) == 0
    output = capsys.readouterr()
    assert "synthetic-session-not-real" not in output.out + output.err
    assert load(path).user_id == "synthetic-user"


@pytest.mark.parametrize("client,key", [("claude", "mcpServers"), ("vscode", "servers")])
def test_generated_config_is_secret_free(tmp_path, capsys, client, key):
    path = tmp_path / "private.json"
    assert cli.main(["--config", str(path), "client-config", client]) == 0
    config = json.loads(capsys.readouterr().out)[key]["jainam"]
    assert config["args"] == ["-m", "jainam_mcp", "--config", str(path.resolve()), "serve"]
    assert "env" not in config
    if client == "vscode":
        assert config["type"] == "stdio"


def test_missing_config_doctor_is_offline(tmp_path, capsys, monkeypatch):
    network = Mock()
    monkeypatch.setattr(cli.Service, "account", network)
    assert cli.main(["--config", str(tmp_path / "absent"), "doctor"]) == 1
    assert json.loads(capsys.readouterr().out)["connection_tested"] is False
    network.assert_not_called()


@pytest.mark.parametrize(
    "data",
    [
        {"data": {"userSession": "synthetic-session-not-real"}},
        {"result": [{"user_session": "synthetic-session-not-real"}]},
    ],
)
def test_extract_session_named_field(data):
    assert cli.extract_session(data) == "synthetic-session-not-real"


@pytest.mark.parametrize(
    "data", [{}, {"token": "unknown"}, {"a": {"userSession": "one"}, "b": {"userSession": "two"}}]
)
def test_unknown_or_ambiguous_login_shape_fails(data):
    with pytest.raises(ConfigError):
        cli.extract_session(data)


def test_login_never_saves_secret_or_auth_code(tmp_path, monkeypatch, capsys):
    answers = iter(["synthetic-app", "synthetic-user", "synthetic-auth-code", "synthetic-api-secret"])
    monkeypatch.setattr(cli.getpass, "getpass", lambda *a: next(answers))
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: True)
    client = Mock()
    client.exchange_auth_code.return_value = {"data": {"userSession": "synthetic-session-not-real"}}
    monkeypatch.setattr(cli, "Client", lambda **kw: client)
    path = tmp_path / "credentials.json"
    assert cli.main(["--config", str(path), "login"]) == 0
    saved = path.read_text()
    assert "synthetic-api-secret" not in saved and "synthetic-auth-code" not in saved
    assert "synthetic-session-not-real" not in capsys.readouterr().out
    client.exchange_auth_code.assert_called_once_with(
        "synthetic-user", "synthetic-auth-code", "synthetic-api-secret"
    )


def test_login_errors_do_not_echo_broker_payload(tmp_path, monkeypatch, capsys):
    answers = iter(["synthetic-app", "synthetic-user", "synthetic-auth-code", "synthetic-api-secret"])
    monkeypatch.setattr(cli.getpass, "getpass", lambda *a: next(answers))
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: True)
    client = Mock()
    client.exchange_auth_code.side_effect = RuntimeError("synthetic-api-secret")
    monkeypatch.setattr(cli, "Client", lambda **kw: client)
    path = tmp_path / "credentials.json"
    assert cli.main(["--config", str(path), "login"]) == 1
    assert not path.exists()
    output = capsys.readouterr()
    assert "synthetic-api-secret" not in output.out + output.err


def test_noninteractive_setup_refuses_unsafe_input(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: False)
    prompt = Mock()
    monkeypatch.setattr(cli.getpass, "getpass", prompt)
    assert cli.main(["--config", str(tmp_path / "credentials.json"), "configure"]) == 1
    prompt.assert_not_called()
    assert "interactive terminal" in capsys.readouterr().err
