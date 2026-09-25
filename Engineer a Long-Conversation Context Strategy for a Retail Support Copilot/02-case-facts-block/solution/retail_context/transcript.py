"""Transcript loader, segmentation, and baseline token accounting."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from retail_context.tokens import count

IssueId = Literal["refund", "subscription", "payment_update"]
Role = Literal["customer", "agent"]


@dataclass(frozen=True)
class Turn:
    turn: int
    role: Role
    text: str
    issue_id: IssueId

    def render(self) -> str:
        return f"Turn {self.turn} ({self.role}): {self.text}"


@dataclass
class Segment:
    issue_id: IssueId
    turns: list[Turn]
    status: Literal["resolved", "active"]

    @property
    def text(self) -> str:
        return "\n\n".join(t.render() for t in self.turns)

    @property
    def turn_range(self) -> tuple[int, int]:
        return self.turns[0].turn, self.turns[-1].turn


@dataclass
class Transcript:
    turns: list[Turn]
    segments: list[Segment]
    _token_count: int | None = field(default=None, repr=False)

    @property
    def token_count(self) -> int:
        if self._token_count is None:
            self._token_count = count(self.full_text)
        return self._token_count

    @property
    def full_text(self) -> str:
        return "\n\n".join(t.render() for t in self.turns)

    @property
    def active_turns(self) -> list[Turn]:
        for s in self.segments:
            if s.status == "active":
                return s.turns
        raise RuntimeError("No active segment in transcript")

    def segment(self, issue_id: IssueId) -> Segment:
        for s in self.segments:
            if s.issue_id == issue_id:
                return s
        raise KeyError(issue_id)


def load(path: str | Path) -> Transcript:
    data = json.loads(Path(path).read_text())
    raw_turns = data["turns"]

    turns = [
        Turn(
            turn=int(t["turn"]),
            role=t["role"],
            text=t["text"],
            issue_id=t["issue_id"],
        )
        for t in raw_turns
    ]

    # Partition into segments preserving order of first appearance.
    by_issue: dict[IssueId, list[Turn]] = {}
    order: list[IssueId] = []
    for t in turns:
        if t.issue_id not in by_issue:
            by_issue[t.issue_id] = []
            order.append(t.issue_id)
        by_issue[t.issue_id].append(t)

    status_map: dict[IssueId, Literal["resolved", "active"]] = {
        sid: ("active" if sid == data["active_issue_id"] else "resolved") for sid in order
    }
    segments = [Segment(issue_id=sid, turns=by_issue[sid], status=status_map[sid]) for sid in order]
    return Transcript(turns=turns, segments=segments)
