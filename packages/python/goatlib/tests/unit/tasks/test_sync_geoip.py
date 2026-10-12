"""Refresh semantics of the geo database sync: skip, fall back, replace."""

from __future__ import annotations

import re
import urllib.error
from pathlib import Path
from typing import Any

import pytest
from goatlib.tasks import sync_geoip
from goatlib.tasks.sync_geoip import (
    GEOIP_FILENAME,
    SyncGeoipParams,
    _month_start,
    _sync,
)


@pytest.fixture
def dest(tmp_path: Path) -> Path:
    return tmp_path


def _fake_download(
    monkeypatch: pytest.MonkeyPatch,
    *,
    available: set[str],
    urls: list[str] | None = None,
) -> None:
    """Stand in for the network: write a file for a published month, 404 otherwise."""

    def download(url: str, target: Path) -> None:
        if urls is not None:
            urls.append(url)
        found = re.search(r"\d{4}-\d{2}", url)
        month = found.group(0) if found else ""
        if month not in available:
            raise urllib.error.HTTPError(url, 403, "Forbidden", None, None)  # type: ignore[arg-type]
        target.write_bytes(month.encode() + b"\x00" * 1024)

    monkeypatch.setattr(sync_geoip, "_download_and_unpack", download)
    # These fixtures are not real databases, so the two things the task reads
    # out of one — that it is valid, and when it was built — are stood in for
    # here; what is under test is the refresh logic around them. The stand-in
    # build date is taken from the month written into the file, exactly as the
    # real `build_epoch` would report it.
    monkeypatch.setattr(sync_geoip, "_validate", lambda path: path.stat().st_size)

    def build_epoch(path: Path) -> int | None:
        if not path.is_file():
            return None
        found = re.match(rb"\d{4}-\d{2}", path.read_bytes())
        return _month_start(found.group(0).decode()) if found else None

    monkeypatch.setattr(sync_geoip, "_build_epoch", build_epoch)


def _seed(dest: Path, version: str, trailer: bytes = b"") -> None:
    """A database already in place, built for `version` — the month leads the
    file so the stand-in metadata reader can report it back."""
    (dest / GEOIP_FILENAME).write_bytes(version.encode() + trailer)


def _run(dest: Path, **kwargs: Any) -> dict[str, Any]:
    return _sync(SyncGeoipParams(dest_dir=str(dest), **kwargs))


def test_downloads_when_nothing_is_there(
    dest: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sync_geoip, "_candidate_months", lambda m: ["2026-09"])
    _fake_download(monkeypatch, available={"2026-09"})

    result = _run(dest)

    assert result["changed"] is True
    assert result["version"] == "2026-09"
    assert (dest / GEOIP_FILENAME).read_bytes().startswith(b"2026-09")


def test_does_not_download_the_release_it_already_holds(
    dest: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sync_geoip, "_candidate_months", lambda m: ["2026-09"])
    urls: list[str] = []
    _fake_download(monkeypatch, available={"2026-09"}, urls=urls)
    _seed(dest, "2026-09")

    result = _run(dest)

    assert result["changed"] is False
    assert urls == []


def test_picks_up_a_new_release_while_holding_the_previous_one(
    dest: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Having fetched last month's file because this month's was not published
    yet, a later run this month must still upgrade — not treat the older
    release as good enough because it is one of the candidates."""
    monkeypatch.setattr(
        sync_geoip, "_candidate_months", lambda m: ["2026-09", "2026-08"]
    )
    _fake_download(monkeypatch, available={"2026-09", "2026-08"})
    _seed(dest, "2026-08")

    result = _run(dest)

    assert result["changed"] is True
    assert result["version"] == "2026-09"
    assert (dest / GEOIP_FILENAME).read_bytes().startswith(b"2026-09")


def test_falls_back_to_the_previous_release_before_one_is_published(
    dest: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        sync_geoip, "_candidate_months", lambda m: ["2026-09", "2026-08"]
    )
    _fake_download(monkeypatch, available={"2026-08"})

    result = _run(dest)

    assert result["changed"] is True
    assert result["version"] == "2026-08"


def test_the_fallback_does_not_re_download_what_is_already_held(
    dest: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """This month is not out and last month is what we have: nothing to do."""
    monkeypatch.setattr(
        sync_geoip, "_candidate_months", lambda m: ["2026-09", "2026-08"]
    )
    urls: list[str] = []
    _fake_download(monkeypatch, available={"2026-08"}, urls=urls)
    _seed(dest, "2026-08")

    result = _run(dest)

    assert result["changed"] is False
    assert result["version"] == "2026-08"
    # One attempt at the newer release, and no re-fetch of the one we hold.
    assert len(urls) == 1 and "2026-09" in urls[0]


def test_replaces_the_file_in_place_rather_than_accumulating(
    dest: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sync_geoip, "_candidate_months", lambda m: ["2026-09"])
    _fake_download(monkeypatch, available={"2026-09"})
    _seed(dest, "2026-08", trailer=b" previous release")

    _run(dest)

    databases = sorted(p.name for p in dest.glob("*.mmdb*"))
    assert databases == [GEOIP_FILENAME]
    assert (dest / GEOIP_FILENAME).read_bytes().startswith(b"2026-09")


def test_force_refetches_the_same_release(
    dest: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sync_geoip, "_candidate_months", lambda m: ["2026-09"])
    urls: list[str] = []
    _fake_download(monkeypatch, available={"2026-09"}, urls=urls)
    _seed(dest, "2026-09")

    result = _run(dest, force=True)

    assert result["changed"] is True
    assert len(urls) == 1


def test_a_custom_url_template_is_used(
    dest: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An operator can point the task at an internal mirror from the UI."""
    monkeypatch.setattr(sync_geoip, "_candidate_months", lambda m: ["2026-09"])
    urls: list[str] = []
    _fake_download(monkeypatch, available={"2026-09"}, urls=urls)

    _run(dest, url_template="https://mirror.internal/geoip-{month}.mmdb.gz")

    assert urls == ["https://mirror.internal/geoip-2026-09.mmdb.gz"]


def test_a_failed_run_leaves_the_current_database_untouched(
    dest: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        sync_geoip, "_candidate_months", lambda m: ["2026-09", "2026-08"]
    )
    _fake_download(monkeypatch, available=set())
    _seed(dest, "2026-07", trailer=b" still good")

    with pytest.raises(RuntimeError, match="no usable DB-IP release"):
        _run(dest)

    assert (dest / GEOIP_FILENAME).read_bytes() == b"2026-07 still good"
    assert not list(dest.glob("*.tmp"))


def test_a_release_built_just_before_its_month_is_not_refetched_for_ever(
    dest: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """DB-IP built the observed September file at 01:38 on the 1st. Were one
    ever finished late on the 31st, reading its build date as the previous
    month would re-download 60 MB on every run, permanently — so a release
    built shortly before its month still counts as that month's."""
    monkeypatch.setattr(sync_geoip, "_candidate_months", lambda m: ["2026-09"])
    urls: list[str] = []
    _fake_download(monkeypatch, available={"2026-09"}, urls=urls)
    (dest / GEOIP_FILENAME).write_bytes(b"built-early")
    monkeypatch.setattr(
        sync_geoip, "_build_epoch", lambda path: _month_start("2026-09") - 3600
    )

    result = _run(dest)

    assert result["changed"] is False
    assert urls == []


def test_the_previous_release_is_still_too_old_to_count(
    dest: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The grace window must not be wide enough to accept last month's file."""
    monkeypatch.setattr(sync_geoip, "_candidate_months", lambda m: ["2026-09"])
    _fake_download(monkeypatch, available={"2026-09"})
    (dest / GEOIP_FILENAME).write_bytes(b"august")
    monkeypatch.setattr(
        sync_geoip, "_build_epoch", lambda path: _month_start("2026-08") + 3600
    )

    assert _run(dest)["changed"] is True


class TestRegistration:
    """How the task reaches Windmill."""

    def _definition(self) -> Any:
        from goatlib.tasks.registry import TASK_REGISTRY

        return next(t for t in TASK_REGISTRY if t.name == "sync_geoip")

    def test_the_schedule_is_created_switched_off(self) -> None:
        """It is only useful where core mounts the geo database, so a sync must
        not start it running on every deployment."""
        assert self._definition().enabled is False

    def test_other_tasks_are_unaffected(self) -> None:
        from goatlib.tasks.registry import TASK_REGISTRY

        # sync_base_data is off by design too: its data sets, region and
        # source are per-deployment choices.
        off_by_design = {"sync_geoip", "sync_base_data"}
        assert all(t.enabled for t in TASK_REGISTRY if t.name not in off_by_design)
