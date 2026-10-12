"""Make the print browser trust the deployment's own certificate authority.

Chromium on Linux reads trusted CAs from the user's NSS database
(``~/.pki/nssdb``), not from the system bundle. A deployment whose public URL
carries a certificate from a private CA (``GOAT_CA_BUNDLE``) therefore has to
be added there, or every page the print worker renders fails to load its data.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

_PEM_BEGIN = "-----BEGIN CERTIFICATE-----"
_PEM_END = "-----END CERTIFICATE-----"
_NICKNAME = "goat-ca"


def split_pem(bundle: str) -> list[str]:
    """The PEM certificates in ``bundle``, one string each."""
    certs = []
    for block in bundle.split(_PEM_END):
        start = block.find(_PEM_BEGIN)
        if start != -1:
            certs.append(block[start:] + _PEM_END + "\n")
    return certs


def ensure_extra_ca_trusted(bundle_path: str | None = None) -> int:
    """Add every certificate in ``GOAT_CA_BUNDLE`` to the NSS database.

    Returns the number of certificates added. Does nothing (returns 0) when no
    bundle is configured; logs and returns 0 when the bundle is missing or
    ``certutil`` is not installed, so printing still works for public URLs.
    """
    path = bundle_path if bundle_path is not None else os.environ.get("GOAT_CA_BUNDLE")
    if not path:
        return 0
    bundle = Path(path)
    if not bundle.is_file():
        logger.warning("GOAT_CA_BUNDLE %s does not exist; not trusting it", path)
        return 0
    certutil = shutil.which("certutil")
    if certutil is None:
        logger.warning("certutil is not installed; cannot trust GOAT_CA_BUNDLE")
        return 0

    db_dir = Path.home() / ".pki" / "nssdb"
    db = f"sql:{db_dir}"
    if not (db_dir / "cert9.db").exists():
        db_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [certutil, "-N", "-d", db, "--empty-password"],
            check=True,
            capture_output=True,
        )

    certs = split_pem(bundle.read_text())
    for index, cert in enumerate(certs):
        with tempfile.NamedTemporaryFile("w", suffix=".pem", delete=False) as tmp:
            tmp.write(cert)
        try:
            # The same nickname on every run: adding it again replaces the entry.
            subprocess.run(
                [
                    certutil,
                    "-A",
                    "-d",
                    db,
                    "-t",
                    "C,,",
                    "-n",
                    f"{_NICKNAME}-{index}",
                    "-i",
                    tmp.name,
                ],
                check=True,
                capture_output=True,
            )
        finally:
            os.unlink(tmp.name)
    logger.info("print browser trusts %d certificate(s) from %s", len(certs), path)
    return len(certs)
