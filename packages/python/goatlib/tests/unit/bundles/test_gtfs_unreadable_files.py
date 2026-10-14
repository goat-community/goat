"""Which unreadable files fail a GTFS import, and which are skipped.

Only the files a feed cannot do without — the spec's required files and the
calendar group — fail the import. An optional GTFS file that cannot be read is
skipped on its own, and so is a file that is not a GTFS table at all.
"""

import zipfile
from pathlib import Path

import pytest
from goatlib.bundles.importers.pt_network.gtfs import GtfsImporter

FEED = {
    "agency.txt": "agency_id,agency_name,agency_url,agency_timezone\nA,Agency,https://a.example,Europe/Berlin\n",
    "stops.txt": "stop_id,stop_name,stop_lat,stop_lon\nS1,First,48.1,11.5\nS2,Second,48.2,11.6\n",
    "routes.txt": "route_id,agency_id,route_short_name,route_type\nR1,A,1,3\n",
    "trips.txt": "route_id,service_id,trip_id\nR1,WK,T1\n",
    "stop_times.txt": (
        "trip_id,arrival_time,departure_time,stop_id,stop_sequence\n"
        "T1,08:00:00,08:00:00,S1,1\nT1,08:05:00,08:05:00,S2,2\n"
    ),
    "calendar_dates.txt": "service_id,date,exception_type\nWK,20260105,1\n",
    "route_directions.txt": "route_id,direction_id,direction_name\nR1,0,Northbound\n",
}


def _zip(tmp_path: Path, **changes: str | None) -> str:
    """The feed with files added, replaced or (with None) removed."""
    files = {**FEED, **changes}
    path = tmp_path / "gtfs.zip"
    with zipfile.ZipFile(path, "w") as zf:
        for name, text in files.items():
            if text is not None:
                zf.writestr(name, text)
    return str(path)


def _roles(feed: str, tmp_path: Path) -> set[str]:
    work = tmp_path / "work"
    work.mkdir()
    return {layer.role for layer in GtfsImporter().extract_layers(feed, str(work))}


def test_a_file_that_is_not_a_gtfs_table_is_skipped(tmp_path: Path) -> None:
    """Release notes shipped in the archive are no table; the feed imports
    without them, and an extension table next to them is still kept."""
    feed = _zip(
        tmp_path,
        **{
            "Release Notes.txt": "Changes in this release:\n\n- new timetable\n",
            "vehicle_categories.txt": "vehicle_category_id\nVC1\n",
        },
    )

    assert GtfsImporter().validate(feed).valid
    roles = _roles(feed, tmp_path)
    assert "Release Notes.txt" not in roles
    assert "route_directions.txt" in roles
    assert "vehicle_categories.txt" in roles  # one column, still a table
    assert {"stops", "stop_times", "trips"} <= roles


def test_an_optional_file_missing_a_column_it_requires_is_skipped(
    tmp_path: Path,
) -> None:
    """An older variant of an optional file (here a rider_categories.txt
    without rider_category_name) is skipped, not a reason to refuse the feed."""
    feed = _zip(
        tmp_path,
        **{
            "rider_categories.txt": "rider_category_id,rider_category_description\n5,Youth\n"
        },
    )

    result = GtfsImporter().validate(feed)
    assert result.valid, result.errors
    assert "rider_categories" not in _roles(feed, tmp_path)


def test_an_optional_file_that_does_not_convert_is_skipped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    feed = _zip(
        tmp_path,
        **{"transfers.txt": "from_stop_id,to_stop_id,transfer_type\nS1,S2,0\n"},
    )
    convert = GtfsImporter._txt_to_parquet

    def failing(txt_path: str, out_path: str, point: bool = False) -> str:
        if txt_path.endswith("transfers.txt"):
            raise RuntimeError("unreadable")
        return convert(txt_path, out_path, point=point)

    monkeypatch.setattr(GtfsImporter, "_txt_to_parquet", staticmethod(failing))
    roles = _roles(feed, tmp_path)
    assert "transfers" not in roles
    assert "stop_times" in roles


def test_an_essential_file_that_does_not_convert_fails_the_import(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    feed = _zip(tmp_path)
    convert = GtfsImporter._txt_to_parquet

    def failing(txt_path: str, out_path: str, point: bool = False) -> str:
        if txt_path.endswith("stop_times.txt"):
            raise RuntimeError("unreadable")
        return convert(txt_path, out_path, point=point)

    monkeypatch.setattr(GtfsImporter, "_txt_to_parquet", staticmethod(failing))
    with pytest.raises(ValueError, match="stop_times.txt could not be read"):
        _roles(feed, tmp_path)


def test_an_essential_file_missing_a_column_still_fails_validation(
    tmp_path: Path,
) -> None:
    feed = _zip(
        tmp_path,
        **{
            "stop_times.txt": "trip_id,arrival_time,departure_time,stop_sequence\nT1,08:00:00,08:00:00,1\n"
        },
    )

    result = GtfsImporter().validate(feed)
    assert not result.valid
    assert any(
        "stop_times.txt is missing column(s): stop_id" in e for e in result.errors
    )


def test_rows_wider_than_the_header_fail_validation_for_an_essential_file(
    tmp_path: Path,
) -> None:
    """Read as CSV, such a file loses its header and every column would be
    named after the first row; the feed is refused with the reason instead."""
    feed = _zip(
        tmp_path,
        **{
            "stop_times.txt": (
                "trip_id,arrival_time,departure_time,stop_id,stop_sequence\n"
                "T1,08:00:00,08:00:00,S1,1,0\n"
            )
        },
    )

    result = GtfsImporter().validate(feed)
    assert not result.valid
    assert any(
        "stop_times.txt has rows with 6 values but a header naming 5 columns" in e
        for e in result.errors
    )
