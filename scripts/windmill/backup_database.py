# py311
# requirements:
# boto3
# wmill

# Standalone Windmill script: Back up PostgreSQL databases and upload to S3.
#
# Databases:
#   - goat: Only specified schemas (public, ducklake, customer)
#   - keycloak: Full database
#   - windmill: Full database
#
# pg_dump is auto-downloaded on first run and cached in DATA_DIR/pg_tools/.
# S3 credentials are loaded from Windmill variables (f/goat/*) or env vars.

import gzip
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Configuration ────────────────────────────────────────────────────

DEFAULT_GOAT_SCHEMAS = ["public", "ducklake", "customer"]
PG_CLIENT_MAJOR = "17"
PG_TOOLS_DIR = "pg_tools"
PGDG_REPO_BASE = "https://apt.postgresql.org/pub/repos/apt"

# ── Logging ──────────────────────────────────────────────────────────

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
for _h in root_logger.handlers[:]:
    root_logger.removeHandler(_h)
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(logging.Formatter("%(name)s - %(levelname)s - %(message)s"))
root_logger.addHandler(_handler)

log = logging.getLogger("backup_database")


# ── Helpers: secrets, S3, formatting ─────────────────────────────────


def _get_secret(name: str, default: str = "") -> str:
    """Get a value from Windmill variables (f/goat/{name}) or env var."""
    try:
        import wmill

        value = wmill.get_variable(f"f/goat/{name}")
        if value:
            return value
    except Exception:
        pass
    return os.environ.get(name, default)


def _get_s3_client(
    s3_access_key: str = "", s3_secret_key: str = "", s3_endpoint_url: str = ""
) -> Any:
    """Create boto3 S3 client with provider-specific config."""
    import boto3
    from botocore.client import Config

    endpoint_url = s3_endpoint_url or _get_secret("S3_ENDPOINT_URL")
    provider = _get_secret("S3_PROVIDER", "hetzner").lower()

    extra_kwargs = {}
    if endpoint_url:
        extra_kwargs["endpoint_url"] = endpoint_url

    if provider == "hetzner":
        extra_kwargs["config"] = Config(
            signature_version="s3v4",
            s3={"payload_signing_enabled": False, "addressing_style": "virtual"},
        )
    elif provider == "minio":
        extra_kwargs["config"] = Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
        )

    return boto3.client(
        "s3",
        aws_access_key_id=s3_access_key or _get_secret("S3_ACCESS_KEY_ID"),
        aws_secret_access_key=s3_secret_key or _get_secret("S3_SECRET_ACCESS_KEY"),
        region_name=_get_secret("S3_REGION_NAME")
        or _get_secret("S3_REGION", "us-east-1"),
        **extra_kwargs,
    )


def _format_bytes(size: int | float) -> str:
    fsize = float(size)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if fsize < 1024:
            return f"{fsize:.2f} {unit}"
        fsize /= 1024
    return f"{fsize:.2f} PB"


# ── pg_dump provisioning ─────────────────────────────────────────────


def _find_package_filename(packages_file: Path, package_name: str) -> str | None:
    """Parse a Debian Packages index to find the .deb Filename for a package."""
    content = packages_file.read_text()
    for block in content.split("\n\n"):
        if not block.strip():
            continue
        name_match = re.search(r"^Package:\s*(.+)$", block, re.MULTILINE)
        if name_match and name_match.group(1).strip() == package_name:
            filename_match = re.search(r"^Filename:\s*(.+)$", block, re.MULTILINE)
            if filename_match:
                return filename_match.group(1).strip()
    return None


def _download_and_extract_deb(
    packages_file: Path, package_name: str, extract_dir: Path
) -> Path:
    """Download a .deb from PGDG repo and extract it. Returns extract_dir."""
    deb_filename = _find_package_filename(packages_file, package_name)
    if not deb_filename:
        raise RuntimeError(f"{package_name} not found in PGDG repo index")

    deb_url = f"{PGDG_REPO_BASE}/{deb_filename}"
    deb_path = extract_dir.parent / f"{package_name}.deb"
    log.info(f"Downloading {deb_url}")
    subprocess.run(
        ["curl", "-fsSL", "-o", str(deb_path), deb_url],
        check=True,
        capture_output=True,
        timeout=120,
    )
    subprocess.run(
        ["dpkg", "-x", str(deb_path), str(extract_dir)],
        check=True,
        capture_output=True,
        timeout=30,
    )
    return extract_dir


def _download_pg_client(bin_dir: Path) -> None:
    """Download pg_dump + libpq from PGDG apt repo and extract to bin_dir."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    lib_dir = bin_dir / "lib"
    lib_dir.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Fetch package index
        packages_url = (
            f"{PGDG_REPO_BASE}/dists/bookworm-pgdg/main/binary-amd64/Packages"
        )
        packages_file = tmppath / "Packages"
        log.info(f"Fetching package index from {packages_url}")
        subprocess.run(
            ["curl", "-fsSL", "-o", str(packages_file), packages_url],
            check=True,
            capture_output=True,
            timeout=60,
        )

        # 1. Download and extract postgresql-client (pg_dump, pg_isready, etc.)
        client_dir = tmppath / "client"
        _download_and_extract_deb(
            packages_file, f"postgresql-client-{PG_CLIENT_MAJOR}", client_dir
        )

        pg_bin = client_dir / "usr" / "lib" / "postgresql" / PG_CLIENT_MAJOR / "bin"
        copied = []
        for tool in ["pg_dump", "pg_isready", "pg_dumpall", "pg_restore"]:
            src = pg_bin / tool
            if src.exists():
                dst = bin_dir / tool
                shutil.copy2(str(src), str(dst))
                os.chmod(str(dst), 0o755)
                copied.append(tool)

        if "pg_dump" not in copied:
            raise RuntimeError(f"pg_dump not found in extracted package at {pg_bin}")

        # 2. Download and extract libpq5 (shared library needed by pg_dump)
        libpq_dir = tmppath / "libpq"
        _download_and_extract_deb(packages_file, "libpq5", libpq_dir)

        # Copy all .so files from libpq
        libpq_src = libpq_dir / "usr" / "lib" / "x86_64-linux-gnu"
        libs_copied = []
        if libpq_src.exists():
            for so_file in libpq_src.glob("libpq*"):
                dst = lib_dir / so_file.name
                shutil.copy2(str(so_file), str(dst))
                libs_copied.append(so_file.name)

        log.info(
            f"Cached to {bin_dir}: "
            f"bins=[{', '.join(copied)}] libs=[{', '.join(libs_copied)}]"
        )


def _ensure_pg_tools() -> tuple:
    """Return (pg_dump_path, pg_isready_path), downloading if needed."""
    # 1. System PATH
    if shutil.which("pg_dump"):
        return "pg_dump", "pg_isready"

    # 2. Cached in DATA_DIR (validate both pg_dump and libpq exist)
    data_dir = os.environ.get("DATA_DIR", "/app/data")
    cache_dir = Path(data_dir) / PG_TOOLS_DIR
    cached = cache_dir / "pg_dump"
    lib_dir = cache_dir / "lib"
    has_libpq = any(lib_dir.glob("libpq*")) if lib_dir.exists() else False
    if cached.exists() and os.access(str(cached), os.X_OK) and has_libpq:
        log.info(f"Using cached pg_dump from {cache_dir}")
        return str(cached), str(cache_dir / "pg_isready")
    elif cached.exists() and not has_libpq:
        log.info("Stale cache detected (missing libpq). Re-downloading...")
        shutil.rmtree(str(cache_dir), ignore_errors=True)

    # 3. Download
    log.info(f"pg_dump not found. Downloading PostgreSQL {PG_CLIENT_MAJOR} client...")
    _download_pg_client(cache_dir)
    return str(cache_dir / "pg_dump"), str(cache_dir / "pg_isready")


# ── Core backup ──────────────────────────────────────────────────────


def _pg_env(pg_password: str = "") -> dict:
    """Build env dict with PGPASSWORD and LD_LIBRARY_PATH for downloaded libs."""
    env = os.environ.copy()
    env["PGPASSWORD"] = pg_password or _get_secret("POSTGRES_PASSWORD", "postgres")

    # Point to downloaded libpq if we're using cached pg tools
    data_dir = os.environ.get("DATA_DIR", "/app/data")
    lib_dir = Path(data_dir) / PG_TOOLS_DIR / "lib"
    if lib_dir.exists():
        existing = env.get("LD_LIBRARY_PATH", "")
        env["LD_LIBRARY_PATH"] = f"{lib_dir}:{existing}" if existing else str(lib_dir)

    return env


def _run_pg_dump(
    pg_dump_path: str,
    database: str,
    output_path: Path,
    schemas: list | None = None,
    pg_server: str = "",
    pg_user: str = "",
    pg_password: str = "",
) -> None:
    """Run pg_dump and write gzipped output."""
    pg_server = pg_server or _get_secret("POSTGRES_SERVER", "db")
    pg_port = _get_secret("POSTGRES_PORT", "5432")
    pg_user = pg_user or _get_secret("POSTGRES_USER", "goat")

    cmd = [
        pg_dump_path,
        "-h",
        pg_server,
        "-p",
        pg_port,
        "-U",
        pg_user,
        "-d",
        database,
        "--no-owner",
        "--no-privileges",
        "--format=plain",
    ]
    if schemas:
        for s in schemas:
            cmd.extend(["--schema", s])

    schema_str = " --schema ".join(schemas) if schemas else "(full)"
    log.info(f"Running: pg_dump -d {database} {schema_str}")

    proc = subprocess.run(
        cmd, capture_output=True, env=_pg_env(pg_password), timeout=600
    )

    if proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(
            f"pg_dump failed for {database} (exit {proc.returncode}): {stderr}"
        )

    raw_size = len(proc.stdout)
    with gzip.open(output_path, "wb", compresslevel=6) as f:
        f.write(proc.stdout)

    compressed_size = output_path.stat().st_size
    ratio = (1 - compressed_size / raw_size) * 100 if raw_size > 0 else 0
    log.info(
        f"Dump: {_format_bytes(raw_size)} -> "
        f"{_format_bytes(compressed_size)} ({ratio:.1f}% reduction)"
    )


def _check_db(
    pg_isready_path: str,
    database: str,
    pg_server: str = "",
    pg_user: str = "",
    pg_password: str = "",
) -> bool:
    """Check database connectivity with pg_isready."""
    try:
        result = subprocess.run(
            [
                pg_isready_path,
                "-h",
                pg_server or _get_secret("POSTGRES_SERVER", "db"),
                "-p",
                _get_secret("POSTGRES_PORT", "5432"),
                "-U",
                pg_user or _get_secret("POSTGRES_USER", "rds"),
                "-d",
                database,
            ],
            capture_output=True,
            env=_pg_env(pg_password),
            timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


# ── Windmill entry point ─────────────────────────────────────────────


def main(
    bucket: str = "",
    prefix: str = "backups/db",
    goat_db: str = "goat",
    goat_schemas: list = DEFAULT_GOAT_SCHEMAS,
    backup_goat: bool = True,
    backup_keycloak: bool = True,
    keycloak_db: str = "keycloak",
    backup_windmill: bool = True,
    windmill_db: str = "windmill",
    pg_server: str = "",
    # Per-database credentials (fall back to POSTGRES_USER / POSTGRES_PASSWORD env vars)
    goat_pg_user: str = "",
    goat_pg_password: str = "",
    keycloak_pg_user: str = "",
    keycloak_pg_password: str = "",
    windmill_pg_user: str = "",
    windmill_pg_password: str = "",
    s3_access_key: str = "",
    s3_secret_key: str = "",
    s3_endpoint_url: str = "",
    dry_run: bool = False,
) -> dict:
    """Back up PostgreSQL databases (goat, keycloak, windmill) and upload dumps to S3.

    pg_dump is auto-provisioned on first run (cached in DATA_DIR/pg_tools/).
    Each database can have its own pg user/password. Falls back to
    POSTGRES_USER / POSTGRES_PASSWORD env vars if not specified.
    """
    start_time = time.time()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # Resolve bucket
    effective_bucket = bucket or _get_secret("S3_BUCKET_NAME") or "backups"
    prefix = prefix.rstrip("/")

    results = {
        "timestamp": timestamp,
        "bucket": effective_bucket,
        "prefix": prefix,
        "databases": {},
    }

    # Ensure pg_dump is available
    pg_dump_path, pg_isready_path = _ensure_pg_tools()

    # Log pg_dump version
    try:
        ver = subprocess.run(
            [pg_dump_path, "--version"],
            capture_output=True,
            env=_pg_env(),
            timeout=10,
        )
        if ver.returncode == 0:
            log.info(ver.stdout.decode().strip())
    except Exception:
        pass

    if dry_run:
        log.info("=== DRY RUN MODE ===")

    # Build database list: (name, schemas_or_None, user, password)
    default_user = _get_secret("POSTGRES_USER", "goat")
    default_password = _get_secret("POSTGRES_PASSWORD", "postgres")
    databases = []
    if backup_goat:
        databases.append(
            (
                goat_db,
                goat_schemas,
                goat_pg_user or default_user,
                goat_pg_password or default_password,
            )
        )
    if backup_keycloak:
        databases.append(
            (
                keycloak_db,
                None,
                keycloak_pg_user or default_user,
                keycloak_pg_password or default_password,
            )
        )
    if backup_windmill:
        databases.append(
            (
                windmill_db,
                None,
                windmill_pg_user or default_user,
                windmill_pg_password or default_password,
            )
        )

    if not databases:
        log.warning("No databases selected for backup")
        results["status"] = "skipped"
        return results

    s3_client = (
        None
        if dry_run
        else _get_s3_client(s3_access_key, s3_secret_key, s3_endpoint_url)
    )

    for db_name, schemas, db_user, db_password in databases:
        db_result = {"database": db_name, "schemas": schemas or "all"}

        # Connectivity check
        if _check_db(pg_isready_path, db_name, pg_server, db_user, db_password):
            log.info(f"Connection to {db_name}: OK")
        else:
            log.warning(f"Connection to {db_name}: FAILED")
            if dry_run:
                db_result["status"] = "connection_failed"
                results["databases"][db_name] = db_result
                continue

        if dry_run:
            schema_desc = ", ".join(schemas) if schemas else "all"
            s3_key = f"{prefix}/{timestamp}_{db_name}.sql.gz"
            log.info(
                f"Would back up {db_name} (schemas: {schema_desc}) "
                f"-> s3://{effective_bucket}/{s3_key}"
            )
            db_result["status"] = "dry_run"
            db_result["s3_key"] = s3_key
            results["databases"][db_name] = db_result
            continue

        # Perform backup
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                dump_file = Path(tmpdir) / f"{db_name}.sql.gz"

                dump_start = time.time()
                _run_pg_dump(
                    pg_dump_path,
                    db_name,
                    dump_file,
                    schemas,
                    pg_server,
                    db_user,
                    db_password,
                )
                dump_duration = time.time() - dump_start

                s3_key = f"{prefix}/{timestamp}_{db_name}.sql.gz"
                file_size = dump_file.stat().st_size

                log.info(
                    f"Uploading {_format_bytes(file_size)} to "
                    f"s3://{effective_bucket}/{s3_key}"
                )
                upload_start = time.time()
                s3_client.upload_file(
                    str(dump_file),
                    effective_bucket,
                    s3_key,
                    ExtraArgs={"ContentType": "application/gzip"},
                )
                upload_duration = time.time() - upload_start

                db_result["status"] = "success"
                db_result["s3_key"] = s3_key
                db_result["size_bytes"] = file_size
                db_result["size_human"] = _format_bytes(file_size)
                db_result["dump_seconds"] = round(dump_duration, 1)
                db_result["upload_seconds"] = round(upload_duration, 1)

                log.info(
                    f"Backup of {db_name}: {_format_bytes(file_size)} "
                    f"(dump {dump_duration:.1f}s, upload {upload_duration:.1f}s)"
                )

        except Exception as e:
            log.error(f"Backup of {db_name} failed: {e}")
            db_result["status"] = "failed"
            db_result["error"] = str(e)

        results["databases"][db_name] = db_result

    # Summary
    total_duration = time.time() - start_time
    results["total_seconds"] = round(total_duration, 1)

    ok = sum(1 for d in results["databases"].values() if d.get("status") == "success")
    fail = sum(1 for d in results["databases"].values() if d.get("status") == "failed")

    log.info("=" * 60)
    log.info(f"Backup completed in {total_duration:.1f}s")
    log.info(f"  Successful: {ok}")
    log.info(f"  Failed:     {fail}")
    for name, r in results["databases"].items():
        log.info(
            f"  {name}: {r.get('status')} {r.get('size_human', '')} -> {r.get('s3_key', '')}"
        )

    results["status"] = "success" if fail == 0 else "partial_failure"
    return results
