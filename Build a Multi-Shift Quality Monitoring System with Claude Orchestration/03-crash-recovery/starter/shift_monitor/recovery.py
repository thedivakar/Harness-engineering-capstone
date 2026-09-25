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

# TODO: Name the staleness threshold as a module-level constant
# STALE_RESUME_THRESHOLD_MINUTES = 30. The number is not arbitrary — it's about
# one-sixteenth of an 8-hour shift; resumes within this window are still on the
# same shift's working set. Document the rationale in a comment.
STALE_RESUME_THRESHOLD_MINUTES = 30  # TODO: confirm and document

Decision = Literal["resume", "fresh"]


def decide(state: ManifestState, now: datetime) -> Decision:
    # TODO: Return "resume" or "fresh" based on three cases.
    #
    #   1. If the manifest has no steps at all, return "fresh".
    #      (An empty manifest is a special case that is easy to forget alongside
    #       the complete-vs-incomplete path.)
    #   2. If the manifest is complete (last step name == "complete"), return "fresh".
    #   3. Otherwise the manifest is incomplete. Compare `now` to the last step's
    #      `ts`: if the gap is <= STALE_RESUME_THRESHOLD_MINUTES, return "resume";
    #      otherwise return "fresh".
    #
    # Boundary note: at exactly 30 minutes, "resume" wins. Use `<=`, not `<`.
    raise NotImplementedError
