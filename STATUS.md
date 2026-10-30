# STATUS

## What was built

`adhd-brain-dump-cli` — a local-first Python CLI for ADHD brain dumps:

- **Capture**: `adhd-dump capture TITLE [--energy low|medium|high] [--urgency low|medium|high] [--tags a,b] [--notes "..."]`
- **List**: `adhd-dump list` with `--energy`, `--urgency`, `--undone` filters
- **Sort / next action**: `adhd-dump sort` / `adhd-dump next` — items sorted by urgency (high→low), then energy (high→low), then oldest first; done items hidden by default; `--low-energy` filter for low-energy days
- **Done / remove**: `adhd-dump done ID`, `adhd-dump rm ID`
- **Export / printable sheets**: `adhd-dump export [--format text|md] [--out FILE] [--low-energy] [--undone]`, checkbox sheets with energy/urgency tags and notes
- **Storage**: single local JSON file (`brain_dump.json` by default in the current folder; overridable with `ADHD_DUMP_DATA_FILE`), atomic writes via temp file + `os.replace`, corrupt/missing file handling
- **Tests**: 18 unit tests (unittest, stdlib only) covering capture defaults/tags/validation, storage round-trip/dir creation/missing/corrupt file, sort ordering/limit/low-energy filter/done exclusion, export formats
- **Packaging**: `pyproject.toml` with `adhd-dump` console script, stdlib-only (Python 3.9+)
- **License**: MIT, `Copyright (c) 2026 Asdale Dynamics, LLC`; README credits Asdale Dynamics, LLC

## How to run

```bash
cd /workspace/kilo-lab/adhd-brain-dump-cli
python3 -m adhd_dump --help
python3 -m adhd_dump capture "call mom" --energy low --urgency high
python3 -m adhd_dump next
python3 -m adhd_dump export --out next-actions.txt
pip install -e .          # optional: installs the `adhd-dump` command
ADHD_DUMP_DATA_FILE=/path/to/store.json adhd-dump list
python3 -m unittest discover -s tests -v
```

## Verification results

- `python3 -m unittest discover -s tests -v`: **18/18 OK**
- Manual CLI smoke test (capture ×3, list, next, next --low-energy, export --format md to file): all commands ran and produced correct output
- Sort order verified: urgent/high-energy items first; `--low-energy` returns only low-energy items
- No third-party dependencies; Python 3.13.5 used for verification

## Known gaps

- No `done`/`rm` unit tests (covered manually only)
- IDs are displayed truncated to 8 chars; `done`/`rm` accept the full id or the 8-char prefix
- No GUI, sync, reminders, or due dates — by design (local-first, minimal)
- No `.github/workflows` files (intentionally omitted)
