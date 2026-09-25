# Exercise 1 — Tiered State Foundation (solution)

Reference implementation for Exercise 1. After this stage:

- `shift_monitor/state.py` defines `HotState` with the four required fields, `to_json_bytes` / `from_json_bytes` / `from_path`, and a `write_atomic` that uses `tempfile` + `os.fsync` + `os.replace` and enforces the 5_120-byte budget.
- `shift_monitor/warm.py` creates the `defects` table + `(shift, ts)` index, exposes `defects_since` (indexed `WHERE ts > ?` with `ORDER BY ts DESC LIMIT ?`), and the `EXPLAIN QUERY PLAN` accessor used to assert the index is used.
- `shift_monitor/cold.py` writes the monthly Markdown rollup using `count_for_month` + `top_components_for_month`.

## Verify

```bash
.venv/bin/pytest tests/test_us01_tiered_state.py -v
```

Expected: 9 passed.
