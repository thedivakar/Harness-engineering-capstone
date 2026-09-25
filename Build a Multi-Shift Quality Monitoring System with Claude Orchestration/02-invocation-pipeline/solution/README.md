# Exercise 2 — Push-Work-Down Invocation Pipeline (solution)

Reference implementation for Exercise 2. After this stage:

- `shift_monitor/invocation.py` exposes `thin` / `rich` / `resumed` as three structurally distinct prompt builders, each returning an `Invocation(shape, prompt)` value object.
- `shift_monitor/pipeline.gather_new_defects` is a pure pass-through to `WarmStore.defects_since` — no Python-side filtering.
- `shift_monitor/pipeline.build_rich_prompt` keeps the rendered prompt under the 4_000-character ceiling for the fixture batch.
- `shift_monitor/pipeline.run_shift` runs the full loop: read hot state → SQL-filter new defects → build rich prompt → one `client.complete` call → parse JSON-fenced state update → atomic hot-state write → one `ScratchpadEntry` appended.

## Verify

```bash
.venv/bin/pytest tests/test_us01_tiered_state.py tests/test_us02_invocation_pipeline.py -v
```

Expected: 15 passed.

End-to-end smoke (recorded client, offline):

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
