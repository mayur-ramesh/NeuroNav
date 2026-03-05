import time
from typing import Any, Optional

class SimpleCache:
    """A very basic in-memory cache with TTL."""
    def __init__(self):
        self._store = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._store:
            entry = self._store[key]
            if time.time() < entry['expiry']:
                return entry['value']
            else:
                del self._store[key]
        return None

    def set(self, key: str, value: Any, ttl: int):
        self._store[key] = {
            'value': value,
            'expiry': time.time() + ttl
        }

# Global instances for different domains
route_cache = SimpleCache()
signal_cache = SimpleCache()
geocode_cache = SimpleCache()
