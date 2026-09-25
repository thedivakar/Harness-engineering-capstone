# Exercise 3 — Crash Recovery with an Incremental Manifest (solution)

Reference implementation for Exercise 3. After this stage:

- `shift_monitor/manifest.py` defines `Step` + `ManifestState`, an `append_step` that opens the file in binary append mode and `fsync`s before returning, and a `load` that reads partial lines without crashing and reports `complete` correctly (last step's `name == "complete"`).
- `shift_monitor/recovery.py` exposes `STALE_RESUME_THRESHOLD_MINUTES = 30` with the shift-cycle rationale, and `decide(state, now)` implements the three-branch rule: empty → fresh, complete → fresh, incomplete-and-recent → resume (with `<=` at the boundary so the 30-minute mark goes to resume).

## Verify

```bash
.venv/bin/pytest tests/test_us01_tiered_state.py tests/test_us02_invocation_pipeline.py tests/test_us03_crash_recovery.py -v
```

Expected: 29 passed.
