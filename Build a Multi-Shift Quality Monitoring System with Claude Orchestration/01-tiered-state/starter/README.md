# Exercise 1 — Tiered State Foundation (starter)

You're building the data layer of a Layer 3 Claude orchestration system that runs once per 8-hour shift at a manufacturing facility. This exercise gets the three storage tiers in place so every shift session can stay tiny.

## What's here

- `shift_monitor/state.py` — `HotState` Pydantic model + `write_atomic`. Fill in the `TODO:` blocks.
- `shift_monitor/warm.py` — `WarmStore` SQLite wrapper + `defects_since` indexed query. Fill in the `TODO:` blocks.
- `shift_monitor/cold.py` — `ColdStore.write_monthly_summary`. Fill in the `TODO:` block.
- `tests/test_us01_tiered_state.py` — the 9 tests for this exercise.
- `fixtures/defects.json` — 40 sub-agent-generated defect rows used by the tests.

## Install

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Verify

```bash
.venv/bin/pytest tests/test_us01_tiered_state.py -v
```

Goal: 9 passed.

The TODOs in `state.py` call out two foot-guns (Pydantic v2's `max_length` rename and `os.replace` vs `os.rename`). Read them before you start typing.
