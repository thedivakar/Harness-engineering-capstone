"""Cold tier: monthly Markdown summaries derived deterministically from the warm tier."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .warm import WarmStore


@dataclass
class ColdStore:
    store: WarmStore
    cold_dir: Path

    def write_monthly_summary(self, year: int, month: int) -> Path:
        # TODO: Produce a Markdown file at `self.cold_dir / "YYYY-MM.md"` with:
        #   - A heading `# YYYY-MM`
        #   - A `Total defects: N` line (from WarmStore.count_for_month)
        #   - A "## Top components" section listing the top-3 components by
        #     count (from WarmStore.top_components_for_month), one per bullet
        # An empty month should still produce a valid file with `Total defects: 0`.
        # Return the path to the written file.
        raise NotImplementedError
