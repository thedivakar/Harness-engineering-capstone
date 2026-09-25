# Exercise 3 — Crash Recovery with an Incremental Manifest (starter)

Your shift pipeline works end-to-end. Now you make it crash-resilient. A long shift can die mid-analysis (SIGKILL, OOM, host reboot) — without a durable manifest, you lose every finding from that shift. With one, the next invocation can decide whether to resume the partial run or start fresh with what was captured so far.

## What's here (additions to Exercise 2's solution)

- `shift_monitor/manifest.py` — `Step` / `ManifestState` / `Manifest.append_step` / `Manifest.load`. Fill in the `TODO:` blocks.
- `shift_monitor/recovery.py` — `STALE_RESUME_THRESHOLD_MINUTES` + `decide(state, now)`. Fill in the `TODO:` blocks.
- `tests/test_us03_crash_recovery.py` — the 14 new tests for this exercise.

## Install

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Verify

```bash
.venv/bin/pytest tests/test_us01_tiered_state.py tests/test_us02_invocation_pipeline.py tests/test_us03_crash_recovery.py -v
```

Goal: 29 passed.

Two foot-guns are called out in the TODO comments: text mode silently weakening fsync on `append_step`, and the off-by-one second at the 30-minute boundary in `decide`. Read those before you fill in the bodies.
