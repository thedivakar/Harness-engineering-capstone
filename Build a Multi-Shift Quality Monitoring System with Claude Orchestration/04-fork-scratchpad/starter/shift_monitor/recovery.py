"""Resume-vs-fresh decision logic for crash recovery.

The 30-minute threshold is ~1/16 of an 8-hour shift cycle: a resume inside this
window is still operating on the same shift's working set; anything older is
treated as a stale partial that should be re-started from scratch with whatever
findings the manifest already captured injected as a summary.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Literal

from .manifest import ManifestState

STALE_RESUME_THRESHOLD_MINUTES = 30

Decision = Literal["resume", "fresh"]


def decide(state: ManifestState, now: datetime) -> Decision:
    if not state.steps:
        return "fresh"
    if state.complete:
        return "fresh"
    last_step = state.steps[-1]
    if now - last_step.ts <= timedelta(minutes=STALE_RESUME_THRESHOLD_MINUTES):
        return "resume"
    return "fresh"
