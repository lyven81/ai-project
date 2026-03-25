"""Simple in-memory cache for pre-generated demo books."""

class BookCache:
    def __init__(self):
        self._store: dict = {}

    def get(self, key: str):
        return self._store.get(key)

    def set(self, key: str, value: dict):
        self._store[key] = value

    def has(self, key: str) -> bool:
        return key in self._store

    def clear(self):
        self._store.clear()

    def keys(self):
        return list(self._store.keys())
