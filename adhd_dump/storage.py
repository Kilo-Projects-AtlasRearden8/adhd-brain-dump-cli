"""Local JSON storage for brain dump items."""

from __future__ import annotations

import json
import os
from typing import Iterable

from .models import Item


class StorageError(Exception):
    """Raised when the JSON store cannot be read or written."""


class JSONStore:
    """Append-only JSON store backed by a single local file."""

    def __init__(self, path: str):
        self.path = path
        self._items: list[Item] = []
        self._loaded = False

    def load(self) -> list[Item]:
        if self._loaded:
            return self._items
        if not os.path.exists(self.path):
            self._items = []
            self._loaded = True
            return self._items
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(f"cannot read {self.path}: {exc}") from exc
        raw_items = data.get("items", []) if isinstance(data, dict) else []
        items: list[Item] = []
        for entry in raw_items:
            if not isinstance(entry, dict):
                continue
            try:
                items.append(Item.from_dict(entry))
            except Exception:
                continue
        self._items = items
        self._loaded = True
        return self._items

    def save(self, items: Iterable[Item]) -> None:
        self._items = list(items)
        self._loaded = True
        directory = os.path.dirname(os.path.abspath(self.path))
        if directory:
            os.makedirs(directory, exist_ok=True)
        payload = {"version": 1, "items": [it.to_dict() for it in self._items]}
        tmp_path = self.path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(tmp_path, self.path)

    def add(self, item: Item) -> None:
        self.load()
        self._items.append(item)
        self.save(self._items)

    def all_items(self) -> list[Item]:
        return list(self.load())

    def find(self, item_id: str) -> Item | None:
        for item in self.load():
            if item.id == item_id:
                return item
        return None

    def mark_done(self, item_id: str) -> bool:
        from datetime import datetime, timezone

        self.load()
        for item in self._items:
            if item.id == item_id and not item.done:
                item.done = True
                item.done_at = datetime.now(timezone.utc).isoformat()
                self.save(self._items)
                return True
        return False

    def remove(self, item_id: str) -> bool:
        self.load()
        for index, item in enumerate(self._items):
            if item.id == item_id:
                del self._items[index]
                self.save(self._items)
                return True
        return False
