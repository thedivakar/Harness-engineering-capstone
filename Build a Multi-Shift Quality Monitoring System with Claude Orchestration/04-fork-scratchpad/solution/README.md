# Exercise 4 — Fork State for Hypothesis Exploration (solution)

Reference implementation for Exercise 4. After this stage you have the **full project** — this solution is byte-identical to the reference repo.

- `shift_monitor/fork.fork_for_hypothesis` creates `data/forks/<hypothesis_id>/`, copies the base hot state in via `shutil.copyfile`, and leaves the base file untouched.
- `shift_monitor/fork.merge_findings` reads each fork's scratchpad via `Scratchpad(...).read()` and re-appends every entry through `Scratchpad(main_scratchpad).append`, keeping fsync semantics uniform.

## Verify

```bash
.venv/bin/pytest tests/ -v
```

Expected: 33 passed.
