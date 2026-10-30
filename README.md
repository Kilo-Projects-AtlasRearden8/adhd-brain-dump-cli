# adhd-brain-dump

Local-first Python CLI to capture ADHD brain dumps, sort items by energy level
and urgency, and export a simple printable next-action list. Everything is
stored in a local JSON file — no accounts, no network, no secrets.

Built and maintained by [Asdale Dynamics, LLC](https://dylanasdale.github.io),
Dylan Asdale's Indiana LLC (formed October 2026). Beginner-friendly, local-first
tools for accessible life-admin and low-energy productivity.

## Why this exists

Brain dumps get everything out of your head, but a long raw list is overwhelming
when your energy is low. This tool captures items as they come to you, then sorts
them by **urgency first, then energy level**, so you can pick the next action that
matches what you actually have the energy for right now. Includes a low-energy
mode and printable sheets you can tape to the wall.

## Install

```bash
git clone <this repo>
cd adhd-brain-dump-cli
pip install -e .
```

No third-party dependencies — Python standard library only (Python 3.9+).

Or run without installing:

```bash
python -m adhd_dump --help
```

## Quick start

Capture a thought:

```bash
adhd-dump capture "call mom" --energy low --urgency high --tags family
adhd-dump capture "deploy the site" --energy high --urgency medium
```

See what's next, sorted by urgency then energy:

```bash
adhd-dump next
```

Low-energy day? Only show things you can do when tired:

```bash
adhd-dump next --low-energy
```

List everything:

```bash
adhd-dump list
```

Mark an item done (use the first 8 chars of the id):

```bash
adhd-dump done <id>
```

Export a printable sheet:

```bash
adhd-dump export --out next-actions.txt
adhd-dump export --format md --out next-actions.md --low-energy --undone
```

Store location defaults to `brain_dump.json` in the current folder. Override with
`ADHD_DUMP_DATA_FILE=/path/to/store.json`.

## Commands

| Command | Purpose |
|---------|---------|
| `capture TITLE` | Add a brain-dump item |
| `list` | List items (open by default) |
| `sort` | Print items sorted by urgency, then energy |
| `next` | Top next-action items (default limit: 5) |
| `done ID` | Mark an item done |
| `rm ID` | Remove an item |
| `export` | Printable next-action sheet (`text` or `md`) |

Options: `--energy low\|medium\|high`, `--urgency low\|medium\|high`,
`--tags a,b,c`, `--notes "..."`, `--undone`, `--low-energy`, `--limit N`,
`--format text\|md`, `--out FILE`.

## Sorting

Items are ordered by urgency (high → medium → low), then energy level
(high → medium → low), then oldest first. Done items are hidden by default.

## Tests

```bash
python -m unittest discover -s tests -v
```

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.

## About Asdale Dynamics, LLC

Asdale Dynamics, LLC is Dylan Asdale's Indiana LLC, formed October 2026. Dylan
is a registered nurse turned AI author and founder. His book *The Massive AI
Manual* and hub site dylanasdale.github.io explain AI "like a friend would":
plain English, step by step, never condescending. The LLC publishes beginner
manuals, open-source tools, and small-business helpers — including accessible
life-admin tools like this one.
