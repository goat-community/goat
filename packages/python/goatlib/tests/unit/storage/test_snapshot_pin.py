"""Unit tests for SnapshotPin (no DuckDB, no PG - injected callables)."""

import threading
import time

from goatlib.storage.snapshot_pin import SnapshotPin


class Harness:
    def __init__(self, latest: int = 1) -> None:
        self.latest = latest
        self.applied: list[int] = []
        self.fetch_calls = 0
        self.apply_delay = 0.0
        self.fetch_error: Exception | None = None
        self.apply_error: Exception | None = None

    def fetch(self) -> int:
        self.fetch_calls += 1
        if self.fetch_error:
            raise self.fetch_error
        return self.latest

    def apply(self, snapshot_id: int) -> None:
        if self.apply_delay:
            time.sleep(self.apply_delay)
        if self.apply_error:
            raise self.apply_error
        self.applied.append(snapshot_id)


def make_pin(h: Harness, gap: float = 1.0) -> SnapshotPin:
    # refresh_interval irrelevant here: poll thread is not started in unit tests
    pin = SnapshotPin(h.fetch, h.apply, refresh_interval=999.0, min_refresh_gap=gap)
    pin._current = 1  # simulate start() without spawning the thread
    return pin


def test_poll_once_noop_when_unchanged() -> None:
    h = Harness(latest=1)
    pin = make_pin(h)
    assert pin.poll_once() is False
    assert h.applied == []


def test_poll_once_applies_new_snapshot() -> None:
    h = Harness(latest=5)
    pin = make_pin(h)
    assert pin.poll_once() is True
    assert h.applied == [5]
    assert pin.current == 5


def test_poll_once_ignores_rate_limit() -> None:
    h = Harness(latest=2)
    pin = make_pin(h, gap=999.0)
    pin._last_refresh_at = time.monotonic()  # just refreshed
    assert pin.poll_once() is True  # poll path is never rate-limited
    assert h.applied == [2]


def test_force_refresh_applies_and_reports_true() -> None:
    h = Harness(latest=3)
    pin = make_pin(h, gap=0.0)
    assert pin.force_refresh() is True
    assert h.applied == [3]
    assert pin.current == 3


def test_force_refresh_true_when_already_latest() -> None:
    h = Harness(latest=1)
    pin = make_pin(h, gap=0.0)
    assert pin.force_refresh() is True  # already fresh: caller may retry safely
    assert h.applied == []


def test_force_refresh_rate_limited_waits_then_rebuilds() -> None:
    h = Harness(latest=9)
    pin = make_pin(h, gap=0.3)
    pin._last_refresh_at = time.monotonic()
    t0 = time.monotonic()
    assert pin.force_refresh() is True
    elapsed = time.monotonic() - t0
    assert elapsed >= 0.25  # waited out the remaining gap instead of refusing
    assert h.applied == [9]
    assert pin.current == 9


def test_force_refresh_single_flight_piggyback() -> None:
    """Concurrent force_refresh callers coalesce: one rebuild, both True."""
    h = Harness(latest=4)
    h.apply_delay = 0.3
    pin = make_pin(h, gap=0.0)
    results: list[bool] = []

    def call() -> None:
        results.append(pin.force_refresh())

    t1 = threading.Thread(target=call)
    t2 = threading.Thread(target=call)
    t1.start()
    time.sleep(0.05)  # ensure t1 holds the refresh lock first
    t2.start()
    t1.join()
    t2.join()
    assert results == [True, True]
    assert h.applied == [4]  # exactly one rebuild


def test_force_refresh_piggyback_during_gap_sleep() -> None:
    """A caller arriving while another sleeps out the gap piggybacks.

    Guards the sleep-inside-the-lock design: if the sleep ever moved outside
    _refresh_lock, the second caller would trigger a second rebuild.
    """
    h = Harness(latest=9)
    pin = make_pin(h, gap=0.3)
    pin._last_refresh_at = time.monotonic()  # gap armed: first caller sleeps
    results: list[bool] = []

    def call() -> None:
        results.append(pin.force_refresh())

    t0 = time.monotonic()
    t1 = threading.Thread(target=call)
    t2 = threading.Thread(target=call)
    t1.start()
    time.sleep(0.05)  # second caller arrives mid-sleep
    t2.start()
    t1.join()
    t2.join()
    assert results == [True, True]
    assert h.applied == [9]  # exactly one rebuild despite two callers
    assert time.monotonic() - t0 >= 0.25  # the gap was actually waited out


def test_fetch_failure_keeps_stale_and_returns_false() -> None:
    h = Harness(latest=7)
    h.fetch_error = ConnectionError("pg down")
    pin = make_pin(h, gap=0.0)
    assert pin.force_refresh() is False
    assert pin.poll_once() is False
    assert pin.current == 1  # stale but serving


def test_apply_failure_keeps_current_and_arms_rate_limit() -> None:
    h = Harness(latest=6)
    h.apply_error = RuntimeError("rebuild failed")
    pin = make_pin(h, gap=0.3)
    assert pin.force_refresh() is False
    assert pin.current == 1
    # a failed rebuild arms the rate limit: the next force_refresh must wait
    # out the gap before retrying, so miss-storms cannot hot-loop rebuilds.
    # Measured from when the failure armed it, not from a later stopwatch: a
    # busy runner spends part of the gap between the two calls.
    armed_at = pin._last_refresh_at
    h.apply_error = None
    assert pin.force_refresh() is True
    assert time.monotonic() - armed_at >= 0.3 - 1e-3
    assert pin.current == 6


def test_start_stop_runs_poll_thread() -> None:
    h = Harness(latest=1)
    pin = SnapshotPin(h.fetch, h.apply, refresh_interval=0.05, min_refresh_gap=0.0)
    pin.start(initial=1)
    try:
        h.latest = 2
        deadline = time.monotonic() + 2.0
        while pin.current != 2 and time.monotonic() < deadline:
            time.sleep(0.02)
        assert pin.current == 2
    finally:
        pin.stop()
    assert pin._thread is not None
    assert not pin._thread.is_alive()


def test_maintain_called_each_tick() -> None:
    calls: list[int] = []
    h = Harness(latest=1)
    pin = SnapshotPin(
        h.fetch,
        h.apply,
        refresh_interval=0.05,
        min_refresh_gap=0.0,
        maintain=lambda: calls.append(1),
    )
    pin.start(initial=1)
    try:
        deadline = time.monotonic() + 2.0
        while len(calls) < 2 and time.monotonic() < deadline:
            time.sleep(0.02)
    finally:
        pin.stop()
    assert len(calls) >= 2
