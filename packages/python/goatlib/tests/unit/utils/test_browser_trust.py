from pathlib import Path
from unittest import mock

import pytest
from goatlib.utils import browser_trust

PEM = (
    "-----BEGIN CERTIFICATE-----\nAAA\n-----END CERTIFICATE-----\n"
    "junk between\n"
    "-----BEGIN CERTIFICATE-----\nBBB\n-----END CERTIFICATE-----\n"
)


def test_split_pem_returns_each_certificate() -> None:
    certs = browser_trust.split_pem(PEM)
    assert len(certs) == 2
    assert "AAA" in certs[0] and "BBB" in certs[1]
    assert all(c.startswith("-----BEGIN") for c in certs)


def test_no_bundle_configured_does_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GOAT_CA_BUNDLE", raising=False)
    with mock.patch.object(browser_trust.subprocess, "run") as run:
        assert browser_trust.ensure_extra_ca_trusted() == 0
    run.assert_not_called()


def test_empty_bundle_setting_does_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOAT_CA_BUNDLE", "")
    with mock.patch.object(browser_trust.subprocess, "run") as run:
        assert browser_trust.ensure_extra_ca_trusted() == 0
    run.assert_not_called()


def test_missing_bundle_file_is_skipped(tmp_path: Path) -> None:
    with mock.patch.object(browser_trust.subprocess, "run") as run:
        assert browser_trust.ensure_extra_ca_trusted(str(tmp_path / "nope.pem")) == 0
    run.assert_not_called()


def test_each_certificate_is_added_to_a_new_nss_db(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = tmp_path / "ca.pem"
    bundle.write_text(PEM)
    monkeypatch.setenv("HOME", str(tmp_path))
    with (
        mock.patch.object(
            browser_trust.shutil, "which", return_value="/usr/bin/certutil"
        ),
        mock.patch.object(browser_trust.subprocess, "run") as run,
    ):
        assert browser_trust.ensure_extra_ca_trusted(str(bundle)) == 2

    commands = [call.args[0] for call in run.call_args_list]
    assert commands[0][:2] == ["/usr/bin/certutil", "-N"]
    added = [c for c in commands if c[1] == "-A"]
    assert [c[c.index("-n") + 1] for c in added] == ["goat-ca-0", "goat-ca-1"]
    assert all(c[c.index("-d") + 1] == f"sql:{tmp_path}/.pki/nssdb" for c in added)


def test_without_certutil_nothing_runs(tmp_path: Path) -> None:
    bundle = tmp_path / "ca.pem"
    bundle.write_text(PEM)
    with (
        mock.patch.object(browser_trust.shutil, "which", return_value=None),
        mock.patch.object(browser_trust.subprocess, "run") as run,
    ):
        assert browser_trust.ensure_extra_ca_trusted(str(bundle)) == 0
    run.assert_not_called()
