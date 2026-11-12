"""Fail on common credential patterns in tracked source; never print matched values."""

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(rb"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(rb"\bAKIA[A-Z0-9]{16}\b"),
    re.compile(rb"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    re.compile(rb"\b[0-9]{8,12}:[A-Za-z0-9_-]{30,}\b"),
    re.compile(rb"/Users/[a-z][a-z0-9_-]*/|(?:192\.168|172\.(?:1[6-9]|2[0-9]|3[01]))\.[0-9]+\.[0-9]+"),
]


def main():
    files = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).split(b"\0")
    failures = []
    for name in files:
        if not name:
            continue
        path = ROOT / name.decode()
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if (
            path.name == ".env"
            or path.name.startswith(".env.")
            and path.name != ".env.example"
            or relative.startswith((".venv/", "dist/", "build/"))
            or "credentials.json" in path.name
            or "session.json" in path.name
        ):
            failures.append(relative + ": forbidden file")
        data = path.read_bytes()
        if any(pattern.search(data) for pattern in PATTERNS):
            failures.append(relative + ": possible secret/private configuration pattern")
    if failures:
        print("\n".join(failures))
        return 1
    print(
        f"Tracked-source scan passed ({sum(bool(f) for f in files)} files). "
        "Pattern scan is not a security guarantee."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
