"""Tests for capture and sort logic of the ADHD brain dump CLI."""

from __future__ import annotations

import json
import os
import tempfile
import unittest

from adhd_dump.cli import build_sheet, cmd_capture, run
from adhd_dump.models import Item, ENERGY_RANK, URGENCY_RANK
from adhd_dump.storage import JSONStore, StorageError


class ItemModelTests(unittest.TestCase):
    def test_defaults(self):
        item = Item(id="1", title="buy milk")
        self.assertEqual(item.energy, "medium")
        self.assertEqual(item.urgency, "medium")
        self.assertEqual(item.tags, [])
        self.assertFalse(item.done)
        self.assertIsNone(item.done_at)

    def test_from_dict_round_trip(self):
        item = Item(id="1", title="x", energy="high", urgency="low", tags=["a"], notes="n")
        copy = Item.from_dict(item.to_dict())
        self.assertEqual(copy, item)

    def test_priority_key_orders_urgency_first(self):
        low_low = Item(id="a", title="a", energy="low", urgency="low")
        high_low = Item(id="b", title="b", energy="high", urgency="low")
        low_high = Item(id="c", title="c", energy="low", urgency="high")
        keys = sorted([low_low.priority_key(), high_low.priority_key(), low_high.priority_key()])
        self.assertEqual(keys[0], low_high.priority_key())
        self.assertEqual(keys[1], high_low.priority_key())
        self.assertEqual(keys[2], low_low.priority_key())

    def test_ranks(self):
        self.assertEqual(ENERGY_RANK["low"], 1)
        self.assertEqual(URGENCY_RANK["high"], 3)


class CaptureTests(unittest.TestCase):
    def test_capture_creates_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            store = JSONStore(path)
            out = cmd_capture(
                type("A", (), {"title": "call mom", "energy": "low", "urgency": "high",
                               "tags": "", "notes": ""})(),
                store,
            )
        self.assertIn("captured", out)
        items = store.all_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "call mom")
        self.assertEqual(items[0].energy, "low")
        self.assertEqual(items[0].urgency, "high")
        self.assertFalse(items[0].done)

    def test_capture_tags_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            store = JSONStore(path)
            cmd_capture(
                type("A", (), {"title": "t", "energy": "medium", "urgency": "medium",
                               "tags": "a, b, ,c", "notes": "n"})(),
                store,
            )
        self.assertEqual(store.all_items()[0].tags, ["a", "b", "c"])

    def test_capture_empty_title_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            store = JSONStore(path)
            out = cmd_capture(
                type("A", (), {"title": "   ", "energy": "medium", "urgency": "medium",
                               "tags": "", "notes": ""})(),
                store,
            )
        self.assertEqual(out, "Error: title is required")
        self.assertEqual(store.all_items(), [])

    def test_storage_creates_parent_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "deep", "nested", "store.json")
            store = JSONStore(path)
            store.add(Item(id="1", title="x"))
            self.assertTrue(os.path.exists(path))

    def test_missing_file_loads_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = JSONStore(os.path.join(tmp, "missing.json"))
            self.assertEqual(store.all_items(), [])

    def test_corrupt_file_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad.json")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("{not json")
            store = JSONStore(path)
            with self.assertRaises(StorageError):
                store.all_items()


class SortTests(unittest.TestCase):
    def _store_with_items(self, tmp):
        path = os.path.join(tmp, "store.json")
        store = JSONStore(path)
        items = [
            Item(id="1", title="low energy low urgency", energy="low", urgency="low"),
            Item(id="2", title="high energy high urgency", energy="high", urgency="high"),
            Item(id="3", title="low energy high urgency", energy="low", urgency="high"),
            Item(id="4", title="high energy low urgency", energy="high", urgency="low"),
        ]
        for it in items:
            store.add(it)
        return store

    def test_sort_urgency_then_energy(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = self._store_with_items(tmp)
            out = run(["--data-file", store.path, "sort", "--limit", "10"], store=store)
        order = [line.split("]  ")[-1] for line in out.splitlines() if line.startswith(("1.", "2.", "3.", "4."))]
        self.assertEqual(order[0], "high energy high urgency")
        self.assertEqual(order[1], "low energy high urgency")
        self.assertEqual(order[2], "high energy low urgency")
        self.assertEqual(order[3], "low energy low urgency")

    def test_sort_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = self._store_with_items(tmp)
            out = run(["--data-file", store.path, "sort", "--limit", "2"], store=store)
        lines = [l for l in out.splitlines() if l[0].isdigit()]
        self.assertEqual(len(lines), 2)

    def test_sort_low_energy_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = self._store_with_items(tmp)
            out = run(["--data-file", store.path, "sort", "--low-energy"], store=store)
        lines = [l for l in out.splitlines() if l[0].isdigit()]
        self.assertTrue(all("[low]" in l for l in lines))
        self.assertEqual(len(lines), 2)

    def test_sort_done_items_excluded_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            store = JSONStore(path)
            open_item = Item(id="1", title="open", energy="high", urgency="high")
            done_item = Item(id="2", title="done", energy="high", urgency="high")
            done_item.done = True
            store.add(open_item)
            store.add(done_item)
            out = run(["--data-file", store.path, "sort"], store=store)
        self.assertIn("open", out)
        self.assertNotIn("done", out)


class LifecycleTests(unittest.TestCase):
    def _make_store(self, tmp):
        path = os.path.join(tmp, "store.json")
        return JSONStore(path)

    def test_mark_done_by_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = self._make_store(tmp)
            store.add(Item(id="abc123456789", title="one", energy="high", urgency="high"))
            store.add(Item(id="def987654321", title="two", energy="low", urgency="low"))
            out = run(["--data-file", store.path, "done", "abc12345"], store=store)
        self.assertIn("marked", out)
        self.assertTrue(store.find("abc123456789").done)
        self.assertFalse(store.find("def987654321").done)

    def test_mark_done_already_done(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = self._make_store(tmp)
            item = Item(id="abc123456789", title="one", energy="high", urgency="high")
            item.done = True
            store.add(item)
            out = run(["--data-file", store.path, "done", "abc12345"], store=store)
        self.assertIn("already done", out)

    def test_mark_done_not_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = self._make_store(tmp)
            store.add(Item(id="abc123456789", title="one", energy="high", urgency="high"))
            out = run(["--data-file", store.path, "done", "nope"], store=store)
        self.assertIn("not found", out)

    def test_mark_done_ambiguous_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = self._make_store(tmp)
            store.add(Item(id="abc1111", title="one", energy="high", urgency="high"))
            store.add(Item(id="abc2222", title="two", energy="low", urgency="low"))
            out = run(["--data-file", store.path, "done", "abc"], store=store)
        self.assertIn("ambiguous", out)

    def test_remove_by_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = self._make_store(tmp)
            store.add(Item(id="abc123456789", title="one", energy="high", urgency="high"))
            out = run(["--data-file", store.path, "rm", "abc12345"], store=store)
        self.assertIn("removed", out)
        self.assertIsNone(store.find("abc123456789"))

    def test_remove_not_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = self._make_store(tmp)
            out = run(["--data-file", store.path, "rm", "nope"], store=store)
        self.assertIn("not found", out)


class ExportTests(unittest.TestCase):
    def test_export_contains_items(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            store = JSONStore(path)
            store.add(Item(id="1", title="task one", energy="low", urgency="high"))
            sheet = build_sheet(store.all_items(), low_energy=False, fmt="text")
        self.assertIn("ADHD BRAIN DUMP", sheet)
        self.assertIn("[ ]", sheet)
        self.assertIn("task one", sheet)

    def test_export_md_format(self):
        sheet = build_sheet([Item(id="1", title="x", energy="low", urgency="low")], fmt="md")
        self.assertIn("- [ ]", sheet)

    def test_export_empty(self):
        sheet = build_sheet([], fmt="text")
        self.assertIn("No items", sheet)

    def test_export_writes_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            out = os.path.join(tmp, "sheet.txt")
            store = JSONStore(path)
            store.add(Item(id="1", title="task one", energy="low", urgency="high"))
            result = run(["--data-file", store.path, "export", "--out", out], store=store)
            self.assertTrue(os.path.exists(out))
            self.assertIn("exported", result)


if __name__ == "__main__":
    unittest.main()
