"""Windmill bootstrap reuses a stored token that still works.

Re-running the bootstrap on an existing install must not mint a new token
each time; it mints only when the stored one is missing or rejected, and
keeps the token file in step.
"""

import stat
from email.message import Message
from pathlib import Path
from typing import Any
from urllib.error import HTTPError

import pytest
from goatlib import windmill_init

pytestmark = pytest.mark.unit

MINTED = "tok-new"
SESSION = "session-1"


class FakeWindmill:
    """Stands in for the module's HTTP helper and records every call."""

    def __init__(self, valid_tokens: set[str]) -> None:
        self.valid_tokens = valid_tokens
        self.calls: list[tuple[str, str, Any, str | None]] = []

    def __call__(
        self,
        base: str,
        path: str,
        method: str = "GET",
        body: Any = None,
        token: str | None = None,
        json_resp: bool = True,
        timeout: int = 30,
    ) -> Any:
        self.calls.append((method, path, body, token))
        if path == "/version":
            return "1.0.0"
        if path.endswith("/users/whoami"):
            if token in self.valid_tokens:
                return {"email": "admin@windmill.dev"}
            raise HTTPError(f"{base}/api{path}", 401, "Unauthorized", Message(), None)
        if path == "/auth/login":
            return SESSION
        if path == "/users/tokens/create":
            return MINTED
        return ""

    def paths(self) -> list[str]:
        return [path for _, path, _, _ in self.calls]


@pytest.fixture()
def env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    token_file = tmp_path / "windmill" / ".token"
    monkeypatch.setenv("WINDMILL_URL", "http://windmill")
    monkeypatch.setenv("WINDMILL_WORKSPACE", "goat")
    monkeypatch.setenv("WINDMILL_ADMIN_EMAIL", "admin@windmill.dev")
    monkeypatch.setenv("WINDMILL_ADMIN_PASSWORD", "secret")
    monkeypatch.setenv("WINDMILL_TOKEN_FILE", str(token_file))
    return token_file


def _install(monkeypatch: pytest.MonkeyPatch, fake: FakeWindmill) -> None:
    monkeypatch.setattr(windmill_init, "_api", fake)


def test_valid_stored_token_is_reused(
    monkeypatch: pytest.MonkeyPatch, env: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    env.parent.mkdir(parents=True)
    env.write_text("tok-old\n")
    before = env.stat().st_mtime_ns
    fake = FakeWindmill(valid_tokens={"tok-old"})
    _install(monkeypatch, fake)

    windmill_init.main()

    assert "/users/tokens/create" not in fake.paths()
    assert "/auth/login" not in fake.paths()
    assert env.read_text() == "tok-old\n"
    assert env.stat().st_mtime_ns == before
    assert capsys.readouterr().out.strip().splitlines()[-1] == "tok-old"


def test_stale_stored_token_is_replaced(
    monkeypatch: pytest.MonkeyPatch, env: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    env.parent.mkdir(parents=True)
    env.write_text("tok-old")
    fake = FakeWindmill(valid_tokens=set())
    _install(monkeypatch, fake)

    windmill_init.main()

    assert "/users/tokens/create" in fake.paths()
    assert env.read_text() == MINTED
    assert capsys.readouterr().out.strip().splitlines()[-1] == MINTED


def test_no_token_file_mints_and_writes_private_file(
    monkeypatch: pytest.MonkeyPatch, env: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    fake = FakeWindmill(valid_tokens=set())
    _install(monkeypatch, fake)

    windmill_init.main()

    assert "/users/tokens/create" in fake.paths()
    assert env.read_text() == MINTED
    assert stat.S_IMODE(env.stat().st_mode) == 0o600
    assert [p.name for p in env.parent.iterdir()] == [".token"]
    assert capsys.readouterr().out.strip().splitlines()[-1] == MINTED


def test_empty_token_file_is_treated_as_missing(
    monkeypatch: pytest.MonkeyPatch, env: Path
) -> None:
    env.parent.mkdir(parents=True)
    env.write_text("")
    fake = FakeWindmill(valid_tokens=set())
    _install(monkeypatch, fake)

    windmill_init.main()

    assert not any(p.endswith("/users/whoami") for p in fake.paths())
    assert env.read_text() == MINTED


def test_goat_folder_is_ensured(monkeypatch: pytest.MonkeyPatch, env: Path) -> None:
    fake = FakeWindmill(valid_tokens=set())
    _install(monkeypatch, fake)

    windmill_init.main()

    assert ("POST", "/w/goat/folders/create", {"name": "goat"}, SESSION) in fake.calls


def test_existing_folder_is_not_an_error(
    monkeypatch: pytest.MonkeyPatch, env: Path
) -> None:
    fake = FakeWindmill(valid_tokens=set())

    def _folder_exists(*args: Any, **kwargs: Any) -> Any:
        path = args[1]
        if path.endswith("/folders/create"):
            raise HTTPError(path, 400, "Folder already exists", Message(), None)
        return fake(*args, **kwargs)

    monkeypatch.setattr(windmill_init, "_api", _folder_exists)

    windmill_init.main()

    assert env.read_text() == MINTED


def test_bootstrap_without_token_file(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeWindmill(valid_tokens={"tok-old"})
    _install(monkeypatch, fake)

    assert (
        windmill_init.bootstrap(
            url="http://windmill",
            workspace="goat",
            admin_email="admin@windmill.dev",
            desired_password="secret",
            existing_token="tok-old",
        )
        == "tok-old"
    )
    assert (
        windmill_init.bootstrap(
            url="http://windmill",
            workspace="goat",
            admin_email="admin@windmill.dev",
            desired_password="secret",
        )
        == MINTED
    )


def test_waits_through_connections_reset_while_windmill_starts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A proxy in front of a starting server (Docker's published port, a
    Kubernetes service) accepts the connection and resets it."""
    fake = FakeWindmill(valid_tokens={"tok-old"})
    resets = [ConnectionResetError(104, "Connection reset by peer")] * 2

    def _starting(base: str, path: str, **kwargs: Any) -> Any:
        if path == "/version" and resets:
            raise resets.pop()
        return fake(base, path, **kwargs)

    monkeypatch.setattr(windmill_init, "_api", _starting)
    monkeypatch.setattr(windmill_init.time, "sleep", lambda _seconds: None)

    assert (
        windmill_init.bootstrap(
            url="http://windmill",
            workspace="goat",
            admin_email="admin@windmill.dev",
            desired_password="secret",
            existing_token="tok-old",
        )
        == "tok-old"
    )
    assert not resets
