"""Per-claim runtime state."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ClaimSession:
    """Holds the live state for one claim while the loop runs.

    `case_facts` accumulates structured facts via record_claim_fact.
    `classification` and `severity` are set by their respective tools.
    Exactly one of `routing` or `escalation` is set when the loop terminates.
    """

    claim_id: str
    policy_id: str
    run_dir: Path
    policies: dict[str, dict[str, Any]] = field(default_factory=dict)
    clarification_responses: dict[str, str] = field(default_factory=dict)

    case_facts: dict[str, str] = field(default_factory=dict)
    classification: dict[str, Any] | None = None
    severity: dict[str, Any] | None = None
    clarifications_asked: list[dict[str, Any]] = field(default_factory=list)
    routing: dict[str, Any] | None = None
    escalation: dict[str, Any] | None = None

    @property
    def terminal_called(self) -> bool:
        return self.routing is not None or self.escalation is not None

    @property
    def outcome(self) -> str:
        if self.routing is not None:
            return "routed"
        if self.escalation is not None:
            return "escalated"
        return "incomplete"
