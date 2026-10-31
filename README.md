# adhd-brain-dump

A gentle, local-first Python CLI for capturing ADHD brain dumps, sorting them by
energy level and urgency, and exporting a simple printable next-action list.

Everything stays on your machine in a single JSON file — no accounts, no network,
no secrets. Built for the days when a long raw list feels overwhelming and you
just need to know the one small thing to do next.

Made by [Asdale Dynamics, LLC](https://dylanasdale.github.io), Dylan Asdale's
Indiana LLC (formed October 2026). Dylan is a registered nurse turned AI author
whose book *The Massive AI Manual* and hub site explain AI "like a friend would":
plain English, step by step, never condescending. This tool is part of the LLC's
accessible life-admin and low-energy productivity work.

## What it does

1. **Capture** a thought as it comes to you, with energy, urgency, tags, and notes.
2. **Sort** your items by urgency (high first), then energy (high first), so the
   most pressing, doable thing floats to the top.
3. **Next action** — see just the top few items that match the energy you have
   right now, including a dedicated low-energy mode.
4. **Export** a printable checkbox sheet (plain text or Markdown) you can tape to
   the wall or print for a low-distraction day.

## Install

No third-party dependencies — Python standard library only (Python 3.9+).

```bash
git clone <this repo>
cd adhd-brain-dump-cli
pip install -e .
```

Or run without installing:

```bash
python3 -m adhd_dump --help
```

## Quick start

Capture a few thoughts:

```bash
adhd-dump capture "call mom" --energy low --urgency high --tags family
adhd-dump capture "email the client" --energy medium --urgency medium --tags work
adhd-dump capture "review the contract" --energy high --urgency high --tags work
```

See what's next, sorted by urgency then energy:

```bash
adhd-dump next
```

Having a low-energy day? Show only the things you can do when you're tired:

```bash
adhd-dump next --low-energy
```

List everything you've captured:

```bash
adhd-dump list
```

Mark something done (use the first 8 characters of the id shown in `list`):

```bash
adhd-dump done c916758a
```

Export a printable next-action sheet:

```bash
adhd-dump export --out next-actions.txt
adhd-dump export --format md --out next-actions.md --low-energy --undone
```

The store defaults to `brain_dump.json` in the current folder. Change it with
`ADHD_DUMP_DATA_FILE=/path/to/store.json`.

## Commands

| Command | What it does |
|---------|--------------|
| `capture TITLE` | Add a new brain-dump item |
| `list` | Show captured items (open ones by default) |
| `sort` | Print items sorted by urgency, then energy |
| `next` | Top next-action items (default: 5) |
| `done ID` | Mark an item done (full id or first 8 chars) |
| `rm ID` | Remove an item (full id or first 8 chars) |
| `export` | Printable next-action sheet (`text` or `md`) |

Common options: `--energy low, medium, high`, `--urgency low, medium, high`,
`--tags a,b,c`, `--notes "..."`, `--undone`, `--low-energy`, `--limit N`,
`--format text, md`, `--out FILE`.

## Sorting

Items are ordered by urgency (high → medium → low), then energy level
(high → medium → low), then oldest first. Done items are hidden by default so
your list stays short and useful.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

24 tests cover capture, storage, sorting, export, and marking/removing items.

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.

## About Asdale Dynamics, LLC

Asdale Dynamics, LLC is Dylan Asdale's Indiana LLC, formed October 2026. Dylan
is a registered nurse turned AI author and founder. His book *The Massive AI
Manual* and hub site dylanasdale.github.io explain AI "like a friend would":
plain English, step by step, never condescending. The LLC publishes beginner
manuals, open-source tools, and small-business helpers — including accessible
life-admin tools like this one.
