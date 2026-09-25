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
    # TODO: Return an Invocation with shape="thin" and the prompt unchanged.
    # The thin shape is for one-shot calls that don't need any project state.
    raise NotImplementedError


def rich(
    role: str, hot_state: HotState, new_defects: Sequence[Mapping[str, Any]]
) -> Invocation:
    # TODO: Build a rich prompt that includes:
    #   - A one-line role framing ("You are the on-call {role} for Northridge Plant 3.")
    #   - A "## Current hot state" section listing recent_defect_hashes,
    #     current_shift_summary, active_alerts, threshold_statuses.
    #   - A "## New defects since last shift" section enumerating each new defect
    #     (id / ts / shift / component / severity / description).
    #   - A trailing instruction asking for: Summary, Findings, Recommended
    #     actions, and an Updated hot state proposal as a JSON block.
    # Return an Invocation with shape="rich" and the rendered prompt.
    raise NotImplementedError


def resumed(
    session_id: str,
    summary: str,
    latest_message: str,
    prior_steps: Sequence[Mapping[str, Any]],
    new_defects: Sequence[Mapping[str, Any]],
) -> Invocation:
    # TODO: Build a resumed prompt with three required sections:
    #   - "## Prior partial findings" — one line per prior step, showing its
    #     `name` and a truncated representation of its `payload`.
    #   - "## Prior summary" — the supplied summary string.
    #   - "## New defects since last partial step" — enumerate new_defects
    #     (id / ts / component / severity / description), or "- (none)" if empty.
    # Close with the latest_message under "## Latest instruction".
    # Return an Invocation with shape="resumed".
    raise NotImplementedError
