"""The service window a GTFS timetable is built for.

A timetable holds at most a year, so the window follows today: six months
either side while the feed is in service, otherwise the year at the end of the
feed's span nearest today. Each case pins `today`, since that is what the rule
turns on.
"""

import zipfile
from datetime import date, timedelta
from pathlib import Path

import pytest
from goatlib.bundles.artifacts.gtfs import _MAX_DAYS, GtfsArtifactBuilder

TODAY = date(2026, 10, 8)


def window(*dates: str, today: date = TODAY) -> tuple[str, int]:
    return GtfsArtifactBuilder._window_from_dates(list(dates), today)


def test_a_feed_in_service_today_keeps_six_months_either_side() -> None:
    """Years of stated service, one long-running service from long ago next to
    the current ones (TfGM): the year from the first date would hold that old
    service alone."""
    assert window("20240902", "20311128") == ("2026-04-09", _MAX_DAYS)


def test_the_window_is_clamped_to_the_start_of_a_feed_in_service() -> None:
    assert window("20261006", "20270602") == ("2026-10-06", 185)


def test_a_feed_shorter_than_the_window_is_kept_whole() -> None:
    assert window("20261004", "20261105") == ("2026-10-04", 33)


def test_a_feed_starting_after_today_keeps_the_year_from_its_first_date() -> None:
    assert window("20270101", "20290101") == ("2027-01-01", _MAX_DAYS)


def test_a_feed_that_ended_keeps_the_year_up_to_its_last_date() -> None:
    assert window("20200101", "20251231") == ("2025-01-01", _MAX_DAYS)


def test_a_short_feed_that_ended_is_kept_whole() -> None:
    assert window("20260301", "20260628") == ("2026-03-01", 120)


@pytest.mark.parametrize(
    "dates",
    [
        (),
        ("", "not-a-date", "2026101"),
        ("20261332", "20270101"),  # month 13: unparseable
    ],
)
def test_without_usable_dates_the_year_from_today(dates: tuple[str, ...]) -> None:
    assert window(*dates) == (TODAY.isoformat(), _MAX_DAYS)


@pytest.mark.parametrize(
    "first, last",
    [
        ("20240101", "20301231"),
        ("20261008", "20261008"),
        ("20200101", "20261008"),
        ("20261008", "20330101"),
        ("20100101", "20120101"),
        ("20400101", "20500101"),
    ],
)
def test_the_window_stays_within_a_year_and_within_the_feed(
    first: str, last: str
) -> None:
    start, days = window(first, last)
    begin = date.fromisoformat(start)
    end = begin + timedelta(days=days - 1)
    assert 1 <= days <= _MAX_DAYS
    assert date(int(first[:4]), int(first[4:6]), int(first[6:])) <= begin
    assert end <= date(int(last[:4]), int(last[4:6]), int(last[6:]))


def test_calendar_dates_count_towards_the_span() -> None:
    """Dates from calendar_dates.txt widen the span like calendar.txt's."""
    assert window("20260101", "20260601", "20261201") == ("2026-04-09", 237)


def test_the_archive_is_read_by_the_same_rule(tmp_path: Path) -> None:
    feed = tmp_path / "gtfs.zip"
    with zipfile.ZipFile(feed, "w") as zf:
        zf.writestr(
            "calendar.txt", "service_id,start_date,end_date\ns1,20240902,20311128\n"
        )
        zf.writestr(
            "calendar_dates.txt", "service_id,date,exception_type\ns1,20230101,1\n"
        )

    assert GtfsArtifactBuilder._date_window(str(feed), TODAY) == (
        "2026-04-09",
        _MAX_DAYS,
    )
