import os
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request


class RateLimiter:
    """Sliding-window limiter, in memory (single process, like the document store)."""

    def __init__(self):
        self._hits: dict[str, deque] = defaultdict(deque)

    def allow(self, key: str, limit: int, window: float = 60.0, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now
        q = self._hits[key]
        while q and now - q[0] >= window:
            q.popleft()
        if len(q) >= limit:
            return False
        q.append(now)
        return True

    def reset(self) -> None:
        self._hits.clear()


limiter = RateLimiter()


def rate_limit(request: Request) -> None:
    """FastAPI dependency. Limit is read per request so tests (and ops) can change it via env."""
    limit = int(os.environ.get("RATE_LIMIT_PER_MIN", "30"))
    if limit <= 0:
        return
    key = request.client.host if request.client else "unknown"
    if not limiter.allow(key, limit):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Try again in a minute.",
            headers={"Retry-After": "60"},
        )