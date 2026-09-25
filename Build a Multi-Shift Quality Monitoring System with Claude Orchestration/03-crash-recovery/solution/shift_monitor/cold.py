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
        self.cold_dir.mkdir(parents=True, exist_ok=True)
        total = self.store.count_for_month(year, month)
        top = self.store.top_components_for_month(year, month, n=3)

        lines: list[str] = [
            f"# {year:04d}-{month:02d}",
            "",
            f"Total defects: {total}",
            "",
            "## Top components",
            "",
        ]
        if not top:
            lines.append("- (none)")
        else:
            for component, count in top:
                lines.append(f"- `{component}` — {count} defect(s)")

        target = self.cold_dir / f"{year:04d}-{month:02d}.md"
        target.write_text("\n".join(lines) + "\n")
        return target
