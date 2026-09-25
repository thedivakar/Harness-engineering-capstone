"""Fake Anthropic Messages client for testing the loop without API calls."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FakeBlock:
    type: str
    text: str = ""
    id: str = ""
    name: str = ""
    input: dict[str, Any] = field(default_factory=dict)


@dataclass
class FakeUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class FakeResponse:
    content: list[FakeBlock]
    stop_reason: str
    usage: FakeUsage


@dataclass
class FakeMessages:
    """Returns scripted responses in order."""

    scripted: list[FakeResponse]
    calls: list[dict[str, Any]] = field(default_factory=list)

    def create(self, **kwargs: Any) -> FakeResponse:
        snapshot = dict(kwargs)
        if "messages" in snapshot:
            snapshot["messages"] = list(snapshot["messages"])
        self.calls.append(snapshot)
        if not self.scripted:
            raise AssertionError("FakeMessages: out of scripted responses")
        return self.scripted.pop(0)


@dataclass
class FakeClient:
    messages: FakeMessages
