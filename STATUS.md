# STATUS

## What was built

`adhd-brain-dump-cli` — a local-first Python CLI for ADHD brain dumps:

- **Capture**: `adhd-dump capture TITLE [--energy low|medium|high] [--urgency low|medium|high] [--tags a,b] [--notes "..."]`
- **List**: `adhd-dump list` with `--energy`, `--urgency`, `--undone`, `--all` filters
- **Sort / next action**: `adhd-dump sort` / `adhd-dump next` — items sorted by urgency (high→low), then energy (high→low), then oldest first; done items hidden by default; `--low-energy` filter for low-energy days
- **Done / remove**: `adhd-dump done ID`, `adhd-dump rm ID` — accept full id or an unambiguous id prefix (first 8 chars)
- **Export / printable sheets**: `adhd-dump export [--format text|md] [--out FILE] [--low-energy] [--undone]`, checkbox sheets with energy/urgency tags and notes
- **Storage**: single local JSON file (`brain_dump.json` by default; overridable with `ADHD_DUMP_DATA_FILE`), atomic writes via temp file + `os.replace`, corrupt/missing file handling, parent directory auto-creation
- **Tests**: 24 unit tests (unittest, stdlib only) covering capture defaults/tags/validation, storage round-trip/dir creation/missing/corrupt file, sort ordering/limit/low-energy filter/done exclusion, export formats, and done/rm by prefix/already-done/not-found/ambiguous-prefix
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

- `python3 -m unittest discover -s tests -v`: **24/24 OK**
- Imports and `pyproject.toml` parse: OK
- Manual CLI smoke test: capture ×3, list, next, next --low-energy, export (text + md), done by prefix, rm by prefix — all correct
- Sort order verified: urgent/high-energy first; `--low-energy` returns only low-energy items; done items hidden by default
- Prefix matching verified: `done`/`rm` accept first 8 chars; ambiguous prefixes rejected
- No third-party dependencies; Python 3.13.5 used for verification

## Known gaps

- No GUI, sync, reminders, or due dates — by design (local-first, minimal)
- Ambiguous id prefixes (matching multiple items) are rejected with an error
- No `.github/workflows` files (intentionally omitted)
