# Exercise 4 — Fork State for Hypothesis Exploration (starter)

You have a crash-resilient shift orchestrator. Now you add a side-channel for investigators: spawn isolated working copies of the current state, let them chase competing hypotheses about a defect cluster in parallel, and merge their findings back without contaminating the main shift stream.

## What's here (additions to Exercise 3's solution)

- `shift_monitor/fork.py` — `fork_for_hypothesis` and `merge_findings`. Fill in the `TODO:` blocks.
- `tests/test_us04_fork_scratchpad.py` — the 4 new tests for this exercise.

## Install

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Verify

```bash
.venv/bin/pytest tests/ -v
```

Goal: 33 passed — full project.

The TODO in `merge_findings` calls out the foot-gun directly: don't reach for raw `open(..., "a")`. Route every appended entry through `Scratchpad.append` so fsync semantics stay uniform across the system.
