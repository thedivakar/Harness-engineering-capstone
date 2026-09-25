# Exercise 2 — Push-Work-Down Invocation Pipeline (starter)

You have a working data layer from Exercise 1. Now you wire up the orchestration loop: SQL-filter the new defects, build a prompt shape that fits the situation, call Claude exactly once, and write the updated hot state atomically.

## What's here (additions to Exercise 1's solution)

- `shift_monitor/invocation.py` — `thin` / `rich` / `resumed` builders. Fill in the `TODO:` blocks.
- `shift_monitor/pipeline.py` — `gather_new_defects`, `build_rich_prompt`, `run_shift`. Fill in the `TODO:` blocks.
- `shift_monitor/client.py` — `ClaudeClient` Protocol + `RecordedClaudeClient` + `AnthropicClaudeClient`. Provided as scaffolding.
- `shift_monitor/scratchpad.py` — typed append-only finding store. Provided as scaffolding; you'll use it again in Exercise 4 to isolate per-fork findings.
- `shift_monitor/__main__.py` — argparse CLI plumbing. Provided as scaffolding.
- `tests/test_us02_invocation_pipeline.py` — the 6 new tests for this exercise.

## Install

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Verify

```bash
.venv/bin/pytest tests/test_us01_tiered_state.py tests/test_us02_invocation_pipeline.py -v
```

Goal: 15 passed.

End-to-end smoke (once the tests pass):

```bash
.venv/bin/python -c "
import json
from pathlib import Path
from shift_monitor.warm import WarmStore
w = WarmStore(Path('data/warm.sqlite')); w.initialize()
w.insert_many(json.load(open('fixtures/defects.json')))
"
.venv/bin/shift-monitor run-shift \
  --shift C \
  --warm-db data/warm.sqlite \
  --since 2026-04-29T22:00:00Z \
  --recorded-response fixtures/recorded_responses/shift_C_2026-04-30.json
```

You should see one Claude call's worth of output: a printed summary line, `data/hot_state.json` rewritten atomically, and one entry appended to `data/shift_scratchpad.jsonl`.
