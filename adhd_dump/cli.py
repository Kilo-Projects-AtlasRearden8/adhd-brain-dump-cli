"""Command line interface for the ADHD brain dump CLI."""

from __future__ import annotations

import argparse
import os
import sys
import uuid
from contextlib import redirect_stdout
from io import StringIO

from .models import Item, VALID_ENERGY, VALID_URGENCY
from .storage import JSONStore, StorageError

DEFAULT_PATH = "brain_dump.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="adhd-dump",
        description=(
            "Capture ADHD brain dumps, sort items by energy level and urgency, "
            "and export a simple next-action list. Local JSON storage only."
        ),
    )
    parser.add_argument(
        "--data-file",
        default=os_env_data_file(),
        help="Path to the local JSON storage file (default: brain_dump.json, "
        "or $ADHD_DUMP_DATA_FILE)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    cap = sub.add_parser("capture", help="Capture a new brain-dump item")
    cap.add_argument("title", help="Item title")
    cap.add_argument("--energy", choices=VALID_ENERGY, default="medium",
                     help="Energy level required (default: medium)")
    cap.add_argument("--urgency", choices=VALID_URGENCY, default="medium",
                     help="Urgency level (default: medium)")
    cap.add_argument("--tags", default="", help="Comma-separated tags")
    cap.add_argument("--notes", default="", help="Notes")
    cap.set_defaults(func=cmd_capture)

    lst = sub.add_parser("list", help="List captured items")
    lst.add_argument("--energy", choices=VALID_ENERGY, default=None)
    lst.add_argument("--urgency", choices=VALID_URGENCY, default=None)
    lst.add_argument("--undone", action="store_true", help="Show undone items only")
    lst.add_argument("--all", action="store_true", help="Show done items too")
    lst.set_defaults(func=cmd_list)

    sort = sub.add_parser("sort", help="Print items sorted by urgency then energy")
    sort.add_argument("--limit", type=int, default=10, help="Max items to show (default: 10)")
    sort.add_argument("--low-energy", action="store_true", help="Low-energy items only")
    sort.add_argument("--undone", action="store_true", help="Undone items only")
    sort.set_defaults(func=cmd_sort)

    nxt = sub.add_parser("next", help="Print the top next-action items (alias for sort)")
    nxt.add_argument("--limit", type=int, default=5, help="Max items to show (default: 5)")
    nxt.add_argument("--low-energy", action="store_true", help="Low-energy items only")
    nxt.add_argument("--undone", action="store_true", help="Undone items only")
    nxt.set_defaults(func=cmd_next)

    don = sub.add_parser("done", help="Mark an item done")
    don.add_argument("id", help="Item id")
    don.set_defaults(func=cmd_done)

    rm = sub.add_parser("rm", help="Remove an item")
    rm.add_argument("id", help="Item id")
    rm.set_defaults(func=cmd_rm)

    exp = sub.add_parser("export", help="Export a printable next-action sheet")
    exp.add_argument("--format", choices=("text", "md"), default="text",
                     help="Output format (default: text)")
    exp.add_argument("--out", default=None, help="Write to file instead of stdout")
    exp.add_argument("--low-energy", action="store_true", help="Low-energy items only")
    exp.add_argument("--undone", action="store_true", help="Undone items only")
    exp.set_defaults(func=cmd_export)

    return parser


def os_env_data_file() -> str:
    import os

    return os.environ.get("ADHD_DUMP_DATA_FILE", DEFAULT_PATH)


def _store(args) -> JSONStore:
    return JSONStore(args.data_file)


def cmd_capture(args, store: JSONStore) -> str:
    if not args.title or not args.title.strip():
        return "Error: title is required"
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
    item = Item(
        id=str(uuid.uuid4()),
        title=args.title.strip(),
        energy=args.energy,
        urgency=args.urgency,
        tags=tags,
        notes=args.notes,
    )
    store.add(item)
    return f"captured {item.id[:8]}  [{args.energy}] [{args.urgency}]  {item.title}"


def _filtered(items, args):
    result = list(items)
    if getattr(args, "undone", False):
        result = [i for i in result if not i.done]
    if not getattr(args, "all", False):
        result = [i for i in result if not i.done]
    if getattr(args, "energy", None):
        result = [i for i in result if i.energy == args.energy]
    if getattr(args, "urgency", None):
        result = [i for i in result if i.urgency == args.urgency]
    if getattr(args, "low_energy", False):
        result = [i for i in result if i.energy == "low"]
    return result


def cmd_list(args, store: JSONStore) -> str:
    items = _filtered(store.all_items(), args)
    if not items:
        return "no items"
    lines = []
    for it in items:
        tag = ",".join(it.tags)
        lines.append(
            f"{it.id[:8]}  [{it.energy}] [{it.urgency}]  {'done' if it.done else 'open'}  {it.title}" +
            (f"  #{tag}" if tag else "")
        )
    return "\n".join(lines)


def cmd_sort(args, store: JSONStore) -> str:
    items = sorted(_filtered(store.all_items(), args), key=lambda i: i.priority_key())
    limit = args.limit if args.limit and args.limit > 0 else len(items)
    items = items[:limit]
    if not items:
        return "no items"
    lines = ["next actions (sorted by urgency, then energy):"]
    for rank, it in enumerate(items, 1):
        lines.append(
            f"{rank}. [{it.energy}] [{it.urgency}]  {it.title}" +
            (f"  #{','.join(it.tags)}" if it.tags else "")
        )
    return "\n".join(lines)


def cmd_next(args, store: JSONStore) -> str:
    return cmd_sort(args, store)


def cmd_done(args, store: JSONStore) -> str:
    if store.mark_done(args.id):
        return f"marked {args.id[:8]} done"
    return f"error: item {args.id[:8]} not found or already done"


def cmd_rm(args, store: JSONStore) -> str:
    if store.remove(args.id):
        return f"removed {args.id[:8]}"
    return f"error: item {args.id[:8]} not found"


def _sheet_title(low_energy: bool) -> str:
    from datetime import datetime, timezone

    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    mode = "  (low-energy mode)" if low_energy else ""
    return f"ADHD BRAIN DUMP — NEXT ACTION SHEET  {day}{mode}"


def build_sheet(items, low_energy: bool = False, fmt: str = "text") -> str:
    lines = [_sheet_title(low_energy), "", "Tick each box when done. One small step at a time.", ""]
    if not items:
        lines.append("No items. Rest is productive too.")
    else:
        for it in items:
            tag = f"  #{','.join(it.tags)}" if it.tags else ""
            if fmt == "md":
                lines.append(f"- [ ] [{it.energy}] [{it.urgency}]  {it.title}{tag}")
            else:
                lines.append(f"[ ]  [{it.energy}] [{it.urgency}]  {it.title}{tag}")
                if it.notes:
                    lines.append(f"     notes: {it.notes}")
    lines.append("")
    lines.append("— Asdale Dynamics, LLC — beginner-friendly, local-first tools.")
    return "\n".join(lines)


def cmd_export(args, store: JSONStore) -> str:
    items = sorted(_filtered(store.all_items(), args), key=lambda i: i.priority_key())
    sheet = build_sheet(items, low_energy=getattr(args, "low_energy", False), fmt=args.format)
    if args.out:
        directory = os.path.dirname(os.path.abspath(args.out))
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(sheet)
            handle.write("\n")
        return f"exported {len(items)} items to {args.out}"
    return sheet


def run(argv: list[str] | None = None, store: JSONStore | None = None) -> str:
    parser = build_parser()
    args = parser.parse_args(argv)
    target_store = store if store is not None else _store(args)
    return args.func(args, target_store)


def main(argv: list[str] | None = None) -> int:
    try:
        output = run(argv)
    except StorageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(output)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
