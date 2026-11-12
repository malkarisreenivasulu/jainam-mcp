"""Local credentials; never searched for in a project or exposed as MCP arguments."""

from __future__ import annotations

import json
import os
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path


class ConfigError(ValueError):
    """A safe-to-display configuration error (contains no credential values)."""


def default_path() -> Path:
    root = (
        Path(os.environ["APPDATA"])
        if os.name == "nt" and os.environ.get("APPDATA")
        else Path.home() / ".config"
    )
    return root / "jainam-mcp" / "credentials.json"


@dataclass(frozen=True, repr=False)
class Credentials:
    user_id: str
    user_session: str

    def __post_init__(self):
        if any(not isinstance(v, str) or not v.strip() for v in (self.user_id, self.user_session)):
            raise ConfigError("Both user ID and user session must be nonempty strings.")
        if any("\n" in v or "\r" in v for v in (self.user_id, self.user_session)):
            raise ConfigError("Credentials cannot contain line breaks.")


def load(path: Path | None = None) -> Credentials | None:
    user_id, session = os.environ.get("JAINAM_USER_ID"), os.environ.get("JAINAM_USER_SESSION")
    if user_id is not None or session is not None:
        if not user_id or not session:
            raise ConfigError("Set both JAINAM_USER_ID and JAINAM_USER_SESSION, or unset both.")
        return Credentials(user_id, session)
    path = path or default_path()
    if not path.exists():
        return None
    if os.name == "posix" and stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise ConfigError("Credentials file must be private. Run chmod 600 on your credentials file.")
    try:
        if path.stat().st_size > 65536:
            raise ValueError
        data = json.loads(path.read_text(encoding="utf-8"))
        return Credentials(data["user_id"], data["user_session"])
    except (KeyError, TypeError, ValueError, UnicodeError) as exc:
        raise ConfigError("Invalid credentials file. Run jainam-mcp configure again.") from exc


def save(credentials: Credentials, path: Path | None = None) -> Path:
    path = path or default_path()
    if path.is_symlink():
        raise ConfigError("Refusing to replace a symbolic-link credentials file.")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".credentials-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            os.chmod(temporary, 0o600)
            json.dump({"user_id": credentials.user_id, "user_session": credentials.user_session}, out)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return path
