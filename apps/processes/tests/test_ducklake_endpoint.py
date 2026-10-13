"""processes attaches DuckLake through the database itself when told to.

Behind a transaction pooler, DUCKLAKE_POSTGRES_SERVER and
DUCKLAKE_POSTGRES_PORT name the database, whose port often differs from the
pooler's. The settings read them at import, so each case runs in a fresh
interpreter.
"""

import os
import subprocess
import sys

BASE_ENV = {
    "AUTH": "false",
    "POSTGRES_SERVER": "pooler",
    "POSTGRES_PORT": "6432",
}


def _uris(**env: str) -> tuple[str, str]:
    environ = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("DUCKLAKE_POSTGRES_", "POSTGRES_"))
    }
    out = subprocess.run(
        [
            sys.executable,
            "-c",
            "from processes.config import Settings; s = Settings(_env_file=None); "
            "print(s.POSTGRES_DATABASE_URI); print(s.DUCKLAKE_POSTGRES_DATABASE_URI)",
        ],
        env={**environ, **BASE_ENV, **env},
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    return out[0], out[1]


def test_unset_uses_the_apps_own_host_and_port() -> None:
    app, ducklake = _uris()
    assert "@pooler:6432/" in app
    assert "@pooler:6432/" in ducklake


def test_the_direct_host_and_port_are_used_when_set() -> None:
    app, ducklake = _uris(
        DUCKLAKE_POSTGRES_SERVER="primary", DUCKLAKE_POSTGRES_PORT="5432"
    )
    assert "@pooler:6432/" in app
    assert "@primary:5432/" in ducklake


def test_the_port_follows_the_resolved_postgres_port(monkeypatch) -> None:
    """Unset, DuckLake follows POSTGRES_PORT as the settings resolve it (a
    .env file, a prefixed variable), not as the process environment had it."""
    from processes.config import Settings

    monkeypatch.setenv("AUTH", "false")
    settings = Settings(
        _env_file=None,
        POSTGRES_SERVER="pooler",
        POSTGRES_PORT=6543,
        DUCKLAKE_POSTGRES_SERVER="primary",
        DUCKLAKE_POSTGRES_PORT="",
    )

    assert "@pooler:6543/" in settings.POSTGRES_DATABASE_URI
    assert "@primary:6543/" in settings.DUCKLAKE_POSTGRES_DATABASE_URI
