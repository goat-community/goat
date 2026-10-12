"""Per-process cache and rate limit for the support API.

Core runs several pods and has no Redis; both live in process memory. A pod
sees a change made through another pod once its cached lists expire, and the
effective rate limit is N× on N pods.
"""

import time
from collections import deque
from collections.abc import Callable
from typing import Any

Key = tuple[Any, ...]


class TTLCache:
    """Values with a time to live, bounded in size.

    Expired entries are dropped when read, and in a sweep every SWEEP_EVERY
    writes or whenever the cache grows past `max_size`; if it is still too big
    after dropping what expired, the oldest writes go first.
    """

    SWEEP_EVERY = 256

    def __init__(
        self, now: Callable[[], float] = time.monotonic, *, max_size: int = 10_000
    ) -> None:
        self._now = now
        self._max_size = max_size
        self._items: dict[Key, tuple[float, Any]] = {}
        self._writes = 0

    def now(self) -> float:
        """The cache's clock (monotonic seconds), for callers that age entries."""
        return self._now()

    def size(self) -> int:
        """Entries held, expired ones not swept yet included.

        Not `__len__`: an empty cache must not be falsy (`cache or TTLCache()`).
        """
        return len(self._items)

    def get(self, key: Key) -> Any | None:
        item = self._items.get(key)
        if item is None:
            return None
        expires, value = item
        if expires <= self._now():
            del self._items[key]
            return None
        return value

    def set(self, key: Key, value: Any, ttl: float) -> None:
        # Re-inserted, so the dict's order stays the order of the last writes.
        self._items.pop(key, None)
        self._items[key] = (self._now() + ttl, value)
        self._writes += 1
        if self._writes >= self.SWEEP_EVERY or len(self._items) > self._max_size:
            self._sweep()

    def _sweep(self) -> None:
        self._writes = 0
        now = self._now()
        for key in [k for k, (expires, _) in self._items.items() if expires <= now]:
            del self._items[key]
        excess = len(self._items) - self._max_size
        if excess > 0:
            for key in list(self._items)[:excess]:
                del self._items[key]

    def invalidate(self, prefix: Key) -> None:
        for key in [k for k in self._items if k[: len(prefix)] == prefix]:
            del self._items[key]


class RateLimiter:
    def __init__(
        self, limit: int, window: float, now: Callable[[], float] = time.monotonic
    ) -> None:
        self._limit = limit
        self._window = window
        self._now = now
        self._hits: dict[Key, deque[float]] = {}

    def hit(self, key: Key) -> bool:
        """Record one event; False (and nothing recorded) when over the limit."""
        now = self._now()
        hits = self._hits.setdefault(key, deque())
        while hits and hits[0] <= now - self._window:
            hits.popleft()
        if len(hits) >= self._limit:
            return False
        hits.append(now)
        return True
