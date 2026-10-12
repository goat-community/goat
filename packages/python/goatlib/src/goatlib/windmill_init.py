"""Idempotent windmill workspace + token + password bootstrap.

Pure stdlib (urllib + json). Returns an API token to the caller; the caller
decides what to do with it (file, K8s Secret, vault, etc.). A token the
caller already holds is reused while windmill still accepts it.

Usage as a library:
    from goatlib.windmill_init import bootstrap
    token = bootstrap(
        url="http://windmill-server",
        workspace="goat",
        admin_email="admin@windmill.dev",
        desired_password="...",
        existing_token=stored_token,  # optional
    )

Usage as a CLI (prints the token as the last line of stdout, and keeps
WINDMILL_TOKEN_FILE in step when it is set):
    python -m goatlib.windmill_init

This module is the canonical place for windmill bootstrap logic; consumers
(the compose bundle's windmill-bootstrap service, the plan4better/charts
windmill bootstrap hook, add-ons) call into it rather than re-implementing
the same login/workspace/token-mint flow.

Placed at the top level of goatlib (rather than under auth/ or services/)
because windmill is its own domain — neither auth-the-way-Keycloak-is
nor an external object-storage service. Parallel to
goatlib.storage.ducklake_init.
"""

from __future__ import annotations

import contextlib
import json
import os
import sys
import tempfile
import time
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

_DEFAULT_TIMEOUT_SECONDS = 30
_DEFAULT_WAIT_MAX_SECONDS = 120
_DEFAULT_WAIT_INTERVAL_SECONDS = 2

# Tool scripts live under f/goat/..., which needs the folder to exist.
_TOOLS_FOLDER = "goat"


def _api(
    base: str,
    path: str,
    method: str = "GET",
    body: Any = None,
    token: str | None = None,
    json_resp: bool = True,
    timeout: int = _DEFAULT_TIMEOUT_SECONDS,
) -> Any:
    """Call ``{base}/api{path}``; JSON bodies are decoded, plain text stripped.

    Raises:
        HTTPError: On an HTTP 4xx/5xx answer.
        URLError: On a network error (DNS, connection refused).
    """
    req = Request(f"{base}/api{path}", method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    data = json.dumps(body).encode() if body is not None else None
    with urlopen(req, data=data, timeout=timeout) as r:
        raw = r.read().decode()
    if not raw:
        return {} if json_resp else ""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw.strip()


def _token_is_valid(base: str, workspace: str, token: str, timeout: int) -> bool:
    """Whether windmill accepts ``token`` in ``workspace``."""
    try:
        _api(base, f"/w/{workspace}/users/whoami", token=token, timeout=timeout)
    except HTTPError:
        return False
    return True


def _ensure_folder(
    base: str, workspace: str, name: str, token: str, timeout: int
) -> None:
    """Create a workspace folder; an existing folder is not an error."""
    try:
        _api(
            base,
            f"/w/{workspace}/folders/create",
            method="POST",
            body={"name": name},
            token=token,
            json_resp=False,
            timeout=timeout,
        )
    except HTTPError as e:
        body = e.read().decode(errors="replace") if e.fp else ""
        detail = f"{e.reason} {body}".strip()
        if "already exists" not in detail.lower():
            print(
                f"WARNING: creating folder {name!r} failed: HTTP {e.code} {detail}",
                file=sys.stderr,
            )


def bootstrap(
    url: str,
    workspace: str,
    admin_email: str,
    desired_password: str,
    default_password: str = "changeme",
    token_label: str = "goatlib-bootstrap",
    existing_token: str | None = None,
    timeout_seconds: int = _DEFAULT_TIMEOUT_SECONDS,
    wait_max_seconds: int = _DEFAULT_WAIT_MAX_SECONDS,
    wait_interval_seconds: int = _DEFAULT_WAIT_INTERVAL_SECONDS,
) -> str:
    """Bootstrap a windmill workspace and return an API token.

    Idempotent at the workspace, folder and password level. When
    ``existing_token`` is given and windmill accepts it in ``workspace``, it is
    returned as is and no login, password change or mint happens. Otherwise a
    new token row is minted; older tokens remain valid until revoked
    separately.

    Steps:
        1. Wait for `{url}/api/version` to return 200 (up to wait_max_seconds)
        2. If `/w/{workspace}/users/whoami` accepts existing_token, ensure the
           tools folder and return existing_token
        3. Try login with desired_password
        4. If that fails, try default_password; if it succeeds, rotate the
           password to desired_password and re-login
        5. Create the workspace if missing (swallow "already exists" errors)
        6. Create the `goat` folder the tool scripts live in, if missing
        7. Mint a non-expiring API token with the given label

    Args:
        url: Windmill base URL (e.g. "http://windmill-server").
        workspace: Workspace ID to ensure exists.
        admin_email: Superadmin login email.
        desired_password: Password to set / log in with.
        default_password: Windmill's first-boot superadmin password.
        token_label: Human-readable label for a minted token.
        existing_token: A previously issued token to reuse if still valid.
        timeout_seconds: Per-request HTTP timeout.
        wait_max_seconds: Max time to wait for windmill API to come up.
        wait_interval_seconds: Poll interval while waiting.

    Returns:
        The reused or minted API token string.

    Raises:
        RuntimeError: If windmill never becomes ready, both passwords fail
            to log in, password rotation re-login fails, or the token mint
            API doesn't return a token.
    """
    base = url.rstrip("/")

    def _call(
        path: str,
        method: str = "GET",
        body: Any = None,
        token: str | None = None,
        json_resp: bool = True,
    ) -> Any:
        return _api(
            base,
            path,
            method=method,
            body=body,
            token=token,
            json_resp=json_resp,
            timeout=timeout_seconds,
        )

    def _try_login(email: str, password: str) -> str | None:
        try:
            res = _call(
                "/auth/login",
                method="POST",
                body={"email": email, "password": password},
                json_resp=False,
            )
            return res if isinstance(res, str) and res else None
        except HTTPError:
            return None

    # 1. Wait for server. urlopen treats HTTP 4xx/5xx as HTTPError and
    # failures to connect as URLError (DNS, connection refused); a proxy in
    # front of a server that is still starting accepts and then resets the
    # connection, which surfaces as a bare OSError. All three mean "not yet".
    waited = 0
    ready = False
    while waited < wait_max_seconds:
        try:
            _call("/version", json_resp=False)
            ready = True
            break
        except OSError:
            time.sleep(wait_interval_seconds)
            waited += wait_interval_seconds
    if not ready:
        raise RuntimeError(
            f"windmill at {base} did not become ready in {wait_max_seconds}s"
        )

    # 2. Reuse a token that still works, so whoever holds it keeps working
    # and no new token row is created.
    if existing_token and _token_is_valid(
        base, workspace, existing_token, timeout_seconds
    ):
        _ensure_folder(base, workspace, _TOOLS_FOLDER, existing_token, timeout_seconds)
        return existing_token

    # 3/4. Login. Prefer the desired password (idempotent re-run case) and
    # fall back to the default (first install). If we got in with the
    # default, rotate immediately so subsequent runs find a non-default
    # password and the workspace's actual superadmin password stays
    # consistent with whatever the caller stored alongside the token.
    session = _try_login(admin_email, desired_password)
    if not session:
        session = _try_login(admin_email, default_password)
        if not session:
            raise RuntimeError(
                f"cannot log in as {admin_email} with desired OR default password"
            )
        if desired_password != default_password:
            _call(
                "/users/setpassword",
                method="POST",
                body={"password": desired_password},
                token=session,
                json_resp=False,
            )
            session = _try_login(admin_email, desired_password)
            if not session:
                raise RuntimeError("password rotation succeeded but re-login failed")

    # 5. Workspace (idempotent: swallow any failure — token mint below
    # surfaces a genuinely missing workspace via /api/w/<ws>/* 401s).
    # Windmill returns HTTP 400 with body "Workspace already exists" on a
    # second create; we don't try to parse that.
    try:
        _call(
            "/workspaces/create",
            method="POST",
            body={"id": workspace, "name": workspace},
            token=session,
            json_resp=False,
        )
    except Exception:
        pass

    # 6. Folder for the tool scripts.
    _ensure_folder(base, workspace, _TOOLS_FOLDER, session, timeout_seconds)

    # 7. Mint a non-expiring API token.
    token: object = _call(
        "/users/tokens/create",
        method="POST",
        body={"label": token_label, "expiration": None},
        token=session,
        json_resp=False,
    )
    if not token or not isinstance(token, str):
        raise RuntimeError(f"token mint failed: {token!r}")

    return token


def _read_token_file(path: str) -> str | None:
    """The token stored at ``path``, or None when missing or empty."""
    try:
        with open(path) as f:
            token = f.read().strip()
    except FileNotFoundError:
        return None
    return token or None


def _write_token_file(path: str, token: str) -> None:
    """Replace ``path`` atomically with a file only its owner can read."""
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)
    # mkstemp creates the file with mode 0600 next to the target, so the
    # rename below stays on one filesystem.
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".token.")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(token)
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except BaseException:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp)
        raise


def main() -> None:
    """CLI entrypoint.

    Reads config from env vars and prints the token as the LAST line of
    stdout so callers can capture it with `tail -1`. Progress and
    informational output goes to stderr.

    Required env vars:
        WINDMILL_URL                 e.g. "http://windmill-server"
        WINDMILL_ADMIN_EMAIL         e.g. "admin@windmill.dev"
        WINDMILL_ADMIN_PASSWORD      desired password (the password the
                                     caller will use afterwards)

    Optional env vars (with defaults):
        WINDMILL_WORKSPACE           default: "goat"
        WINDMILL_DEFAULT_PASSWORD    default: "changeme"  (windmill's
                                                          first-boot pwd)
        WINDMILL_TOKEN_LABEL         default: "goatlib-bootstrap"
        WINDMILL_TOKEN_FILE          unset: no file. Set: a non-empty file
                                     there is reused while windmill accepts
                                     it; otherwise the new token replaces it
                                     (atomically, mode 0600).
    """
    try:
        url = os.environ["WINDMILL_URL"]
        admin_email = os.environ["WINDMILL_ADMIN_EMAIL"]
        desired_password = os.environ["WINDMILL_ADMIN_PASSWORD"]
    except KeyError as missing:
        print(
            f"ERROR: required env var missing: {missing.args[0]}",
            file=sys.stderr,
        )
        sys.exit(1)

    workspace = os.environ.get("WINDMILL_WORKSPACE") or "goat"
    default_password = os.environ.get("WINDMILL_DEFAULT_PASSWORD", "changeme")
    token_label = os.environ.get("WINDMILL_TOKEN_LABEL", "goatlib-bootstrap")
    token_file = os.environ.get("WINDMILL_TOKEN_FILE") or None
    existing_token = _read_token_file(token_file) if token_file else None

    print(f"Bootstrapping windmill workspace at {url}", file=sys.stderr)
    token = bootstrap(
        url=url,
        workspace=workspace,
        admin_email=admin_email,
        desired_password=desired_password,
        default_password=default_password,
        token_label=token_label,
        existing_token=existing_token,
    )
    if token == existing_token:
        print(f"Reusing the stored token from {token_file}", file=sys.stderr)
    else:
        print(
            f"Token minted (label={token_label}, length={len(token)} chars)",
            file=sys.stderr,
        )
        if token_file:
            _write_token_file(token_file, token)
            print(f"Token written to {token_file}", file=sys.stderr)
    # Token last on stdout for easy capture by callers (e.g. `... | tail -1`).
    print(token)


if __name__ == "__main__":
    main()
