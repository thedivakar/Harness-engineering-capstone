"""Three invocation shapes.

thin     — prompt only.
rich     — hot state + new defects.
resumed  — prior partial findings + new defects since the last manifest step.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from .state import HotState

InvocationShape = Literal["thin", "rich", "resumed"]


@dataclass(frozen=True)
class Invocation:
    shape: InvocationShape
    prompt: str


def thin(prompt: str) -> Invocation:
    return Invocation(shape="thin", prompt=prompt)


def rich(
    role: str, hot_state: HotState, new_defects: Sequence[Mapping[str, Any]]
) -> Invocation:
    lines: list[str] = [
        f"You are the on-call {role} for Northridge Plant 3.",
        "",
        "## Current hot state",
        f"- Recent defect hashes (last {len(hot_state.recent_defect_hashes)}): "
        f"{', '.join(hot_state.recent_defect_hashes)}",
        f"- Current shift summary: {hot_state.current_shift_summary}",
        f"- Active alerts: {hot_state.active_alerts}",
        f"- Threshold statuses: {hot_state.threshold_statuses}",
        "",
        "## New defects since last shift",
    ]
    for d in new_defects:
        lines.append(
            f"- {d['id']} / {d['ts']} / {d['shift']} / {d['component']} / "
            f"{d['severity']} / {d['description']}"
        )
    lines.extend(
        [
            "",
            "Produce a shift report: Summary, Findings, Recommended actions, "
            "and an Updated hot state proposal as a JSON block.",
        ]
    )
    return Invocation(shape="rich", prompt="\n".join(lines))


def resumed(
    session_id: str,
    summary: str,
    latest_message: str,
    prior_steps: Sequence[Mapping[str, Any]],
    new_defects: Sequence[Mapping[str, Any]],
) -> Invocation:
    lines: list[str] = [
        f"Resuming session {session_id}.",
        "",
        "## Prior partial findings",
    ]
    for step in prior_steps:
        payload_str = str(step.get("payload", {}))[:120]
        lines.append(f"- {step['name']}: {payload_str}")
    lines.extend(
        [
            "",
            "## Prior summary",
            summary,
            "",
            "## New defects since last partial step",
        ]
    )
    if not new_defects:
        lines.append("- (none)")
    else:
        for d in new_defects:
            lines.append(
                f"- {d['id']} / {d['ts']} / {d['component']} / "
                f"{d['severity']} / {d['description']}"
            )
    lines.extend(["", "## Latest instruction", latest_message])
    return Invocation(shape="resumed", prompt="\n".join(lines))
