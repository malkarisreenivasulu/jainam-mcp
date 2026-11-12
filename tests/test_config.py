import json
import os
import stat

import pytest

from jainam_mcp.config import ConfigError, Credentials, load, save


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    monkeypatch.delenv("JAINAM_USER_ID", raising=False)
    monkeypatch.delenv("JAINAM_USER_SESSION", raising=False)


def test_missing_is_unconfigured(tmp_path):
    assert load(tmp_path / "absent") is None


def test_save_load_and_private_mode(tmp_path):
    path = tmp_path / "private" / "credentials.json"
    expected = Credentials("synthetic-user", "synthetic-session-not-real")
    assert save(expected, path) == path
    assert load(path) == expected
    assert "synthetic" not in repr(expected)
    if os.name == "posix":
        assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_env_pair_overrides_file_and_partial_fails(tmp_path, monkeypatch):
    path = tmp_path / "credentials.json"
    save(Credentials("file-user", "file-session-not-real"), path)
    monkeypatch.setenv("JAINAM_USER_ID", "environment-user")
    with pytest.raises(ConfigError):
        load(path)
    monkeypatch.setenv("JAINAM_USER_SESSION", "environment-session-not-real")
    assert load(path).user_id == "environment-user"


@pytest.mark.parametrize(
    "value", [{}, [], {"user_id": "x", "user_session": 3}, {"user_id": "", "user_session": "x"}]
)
def test_bad_file_is_safe_error(tmp_path, value):
    path = tmp_path / "credentials.json"
    path.write_text(json.dumps(value))
    path.chmod(0o600)
    with pytest.raises(ConfigError):
        load(path)


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission semantics")
def test_world_readable_rejected(tmp_path):
    path = save(Credentials("synthetic-user", "synthetic-session-not-real"), tmp_path / "credentials.json")
    path.chmod(0o644)
    with pytest.raises(ConfigError, match="private"):
        load(path)


@pytest.mark.skipif(os.name != "posix", reason="Windows symlink privileges vary")
def test_symlink_write_rejected(tmp_path):
    target = tmp_path / "target"
    target.write_text("unchanged")
    link = tmp_path / "link"
    link.symlink_to(target)
    with pytest.raises(ConfigError):
        save(Credentials("synthetic-user", "synthetic-session-not-real"), link)
    assert target.read_text() == "unchanged"


@pytest.mark.parametrize(
    "values", [("", "session"), ("id", ""), ("id\nheader", "session"), ("id", "session\rheader")]
)
def test_invalid_credentials(values):
    with pytest.raises(ConfigError):
        Credentials(*values)
