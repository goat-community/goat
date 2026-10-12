import pytest
from core.support.throttle import RateLimiter, TTLCache

pytestmark = pytest.mark.unit


class Clock:
    def __init__(self) -> None:
        self.t = 1000.0

    def __call__(self) -> float:
        return self.t


def test_cache_expires_and_invalidates_by_prefix() -> None:
    clock = Clock()
    cache = TTLCache(now=clock)
    cache.set(("u1", "list", "mine"), [1], ttl=30)
    cache.set(("u1", "summary"), {"n": 1}, ttl=60)
    cache.set(("u2", "summary"), {"n": 2}, ttl=60)
    assert cache.get(("u1", "list", "mine")) == [1]
    clock.t += 31
    assert cache.get(("u1", "list", "mine")) is None
    cache.invalidate(("u1",))
    assert cache.get(("u1", "summary")) is None
    assert cache.get(("u2", "summary")) == {"n": 2}


def test_rate_limiter_sliding_window() -> None:
    clock = Clock()
    limiter = RateLimiter(limit=2, window=3600, now=clock)
    assert limiter.hit(("u1", "ticket"))
    assert limiter.hit(("u1", "ticket"))
    assert not limiter.hit(("u1", "ticket"))
    assert limiter.hit(("u2", "ticket"))
    clock.t += 3601
    assert limiter.hit(("u1", "ticket"))


def test_cache_sweeps_expired_entries_on_write() -> None:
    clock = Clock()
    cache = TTLCache(now=clock)
    for i in range(10):
        cache.set(("old", i), i, ttl=10)
    clock.t += 11
    # never read again: only a sweep can drop them
    for i in range(TTLCache.SWEEP_EVERY):
        cache.set(("new", i), i, ttl=60)
    assert cache.size() == TTLCache.SWEEP_EVERY
    assert cache.get(("new", 0)) == 0


def test_cache_evicts_the_oldest_writes_beyond_its_size() -> None:
    clock = Clock()
    cache = TTLCache(now=clock, max_size=3)
    for key in ("a", "b", "c"):
        cache.set((key,), key, ttl=60)
    cache.set(("a",), "a2", ttl=60)  # rewritten: now the newest
    cache.set(("d",), "d", ttl=60)
    assert cache.size() == 3
    assert cache.get(("b",)) is None
    assert [cache.get((k,)) for k in ("a", "c", "d")] == ["a2", "c", "d"]


def test_cache_drops_expired_entries_before_evicting_live_ones() -> None:
    clock = Clock()
    cache = TTLCache(now=clock, max_size=2)
    cache.set(("live",), 1, ttl=60)
    cache.set(("short",), 2, ttl=5)
    clock.t += 6
    cache.set(("new",), 3, ttl=60)
    assert cache.get(("live",)) == 1 and cache.get(("new",)) == 3


def test_invalidate_still_works_after_sweeps() -> None:
    clock = Clock()
    cache = TTLCache(now=clock, max_size=5)
    for i in range(20):
        cache.set(("u1", i), i, ttl=60)
    cache.set(("u2", 0), 0, ttl=60)
    cache.invalidate(("u1",))
    assert cache.size() == 1 and cache.get(("u2", 0)) == 0
