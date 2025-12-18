import time
from typing import Any, Dict, Optional, Tuple


class ResponseCache:
    """
    Lightweight in-memory cache with TTL to avoid redundant upstream calls.
    Safe for single-process usage in this demo setup.
    """

    def __init__(self, ttl_seconds: int = 900, max_entries: int = 256):
        self.ttl = ttl_seconds
        self.max_entries = max_entries
        self._store: Dict[str, Tuple[float, Any]] = {}

    def _evict_if_needed(self) -> None:
        if len(self._store) <= self.max_entries:
            return
        # drop oldest entry
        oldest_key = min(self._store.items(), key=lambda kv: kv[1][0])[0]
        self._store.pop(oldest_key, None)

    def get(self, key: str) -> Optional[Any]:
        record = self._store.get(key)
        if not record:
            return None
        expires_at, value = record
        if expires_at < time.time():
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        expires_at = time.time() + self.ttl
        self._store[key] = (expires_at, value)
        self._evict_if_needed()
