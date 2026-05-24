"""Unified cache for all data collectors — one TTL policy, one directory, one way.

Every data collector (EDGAR, Crunchbase, Wikipedia, Knowledge Graph, hiring signal,
market data) uses this CacheManager instead of implementing its own cache logic.

Cache structure:
  ~/.cit/cache/<namespace>/<key>.json
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


DEFAULT_CACHE_DIR = Path.home() / ".cit" / "cache"


class CacheManager:
    """Simple file-based cache with TTL expiry and JSON serialization.

    Thread-safe for CLI use (not designed for concurrent writes).
    """

    def __init__(self, namespace: str, ttl_seconds: int = 86400) -> None:
        """Initialize cache for a namespace.

        Args:
            namespace: Subdirectory name (e.g., 'edgar', 'crunchbase', 'wikipedia').
            ttl_seconds: How long cached entries are valid. Default 24h.
        """
        self._dir = DEFAULT_CACHE_DIR / namespace
        self._dir.mkdir(parents=True, exist_ok=True)
        self._ttl = ttl_seconds

    def _path(self, key: str) -> Path:
        """Get the file path for a cache key (safe filename)."""
        safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in key)
        return self._dir / f"{safe}.json"

    def get(self, key: str) -> dict[str, Any] | None:
        """Retrieve cached data. Returns None if missing or expired."""
        path = self._path(key)
        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text())
            cached_at = data.get("_cached_at", 0)
            if time.time() - cached_at > self._ttl:
                path.unlink(missing_ok=True)
                return None
            return data
        except (json.JSONDecodeError, OSError):
            path.unlink(missing_ok=True)
            return None

    def set(self, key: str, data: dict[str, Any]) -> None:
        """Store data in cache with current timestamp."""
        data["_cached_at"] = time.time()
        try:
            self._path(key).write_text(json.dumps(data, indent=2, default=str))
        except OSError:
            pass  # Non-critical — cache miss is better than a crash

    def clear(self, key: str | None = None) -> None:
        """Clear a specific key or the entire namespace."""
        if key:
            self._path(key).unlink(missing_ok=True)
        else:
            for f in self._dir.glob("*.json"):
                f.unlink(missing_ok=True)

    def age(self, key: str) -> float | None:
        """Return the age of a cached entry in seconds, or None if missing."""
        data = self.get(key)
        if data is None:
            return None
        return time.time() - data.get("_cached_at", 0)
