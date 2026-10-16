"""Postgres credentials for DuckDB, and credentials in text.

`postgres_attach_target` hands DuckDB a Postgres connection string without
its password and puts the password into the DuckDB database's Postgres
secret, which every Postgres ATTACH on it uses (`ATTACH ... (TYPE postgres)`
and DuckLake's catalog alike), so connection strings carry no secret wherever
they are shown. One DuckDB database, with all its cursors, therefore holds
one Postgres password. `redact_credentials` removes credentials from text a
job or a service hands on.

Standard library only.
"""

import re
from typing import TYPE_CHECKING
from urllib.parse import parse_qsl, unquote, urlsplit

if TYPE_CHECKING:
    import duckdb

# `password=...` in a libpq connection string, quoted or not.
_LIBPQ_PASSWORD = re.compile(r"(?:^|\s+)password\s*=\s*('(?:[^'\\]|\\.)*'|[^\s']\S*)")
# The password of `scheme://user:password@host` in any text.
_URL_PASSWORD = re.compile(r"(\b[a-z][a-z0-9+.-]*://[^:@/\s'\"]*:)[^@\s'\"/]+@", re.I)
# The value after a key ending in `password` (`password=`, `PGPASSWORD=`,
# `'password': `, SQL's `PASSWORD '...'`) in any text.
_KEY_PASSWORD = re.compile(
    r"(\b\w*password['\"]?(?:\s*[=:]\s*|\s+(?=')))"
    r"('(?:[^'\\]|\\.)*'|\"[^\"]*\"|[^\s'\",;)}\]]+)",
    re.I,
)


def _libpq_value(value: str) -> str:
    """A libpq value, quoted when it is empty or holds a space, a quote or a
    backslash."""
    if value and not re.search(r"[\s'\\]", value):
        return value
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def without_password(dsn: str) -> tuple[str, str | None]:
    """A Postgres URI or libpq connection string without its password, and
    the password (None when it has none).

    A URI that loses its password comes back as a libpq string: DuckDB merges
    its Postgres secret into a libpq string only.
    """
    if "://" in dsn:
        url = urlsplit(dsn)
        if url.password is None:
            return dsn, None
        params = {
            "host": url.hostname,
            "port": str(url.port) if url.port else None,
            "user": unquote(url.username) if url.username else None,
            "dbname": unquote(url.path.lstrip("/")) or None,
            **dict(parse_qsl(url.query)),
        }
        target = " ".join(
            f"{key}={_libpq_value(value)}" for key, value in params.items() if value
        )
        return target, unquote(url.password)
    found = _LIBPQ_PASSWORD.search(dsn)
    if found is None:
        return dsn, None
    value = found.group(1)
    if value.startswith("'"):
        value = re.sub(r"\\(.)", r"\1", value[1:-1])
    target = (dsn[: found.start()] + dsn[found.end() :]).strip()
    return target, value


def postgres_attach_target(con: "duckdb.DuckDBPyConnection", dsn: str) -> str:
    """`dsn` for the string literal of an ATTACH (quotes doubled), without its
    password; the password goes into `con`'s Postgres secret, replacing one
    set before. Call it on a connection you own or under its owner's lock:
    two cursors replacing the secret at once conflict."""
    target, password = without_password(dsn)
    if password is not None:
        con.execute("CREATE OR REPLACE SECRET (TYPE postgres, PASSWORD ?)", [password])
    return target.replace("'", "''")


def redact_credentials(text: str) -> str:
    """`text` with every password it holds replaced by `***`."""
    text = _URL_PASSWORD.sub(r"\1***@", text)
    return _KEY_PASSWORD.sub(r"\1***", text)
