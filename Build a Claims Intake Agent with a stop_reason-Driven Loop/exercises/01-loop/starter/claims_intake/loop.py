"""The agentic loop.

The defining contract:
- Control flow is driven by `response.stop_reason`.
- Loop continues iff stop_reason == "tool_use".
- Loop returns iff stop_reason == "end_turn".
- Any other stop_reason raises UnexpectedStopReason.

No string-membership tests against assistant text drive control flow here.
No integer-literal iteration cap is the primary stopping mechanism.
A Budget (token + wall-clock, sourced from config) is the safety net and raises
BudgetExceeded if hit — it never silently truncates.
"""

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol

from claims_intake.budget import Budget
from claims_intake.tracer import Tracer


class UnexpectedStopReason(Exception):
    pass


ToolExecutor = Callable[[str, dict[str, Any]], str]
"""Takes (tool_name, tool_input) and returns the tool_result content as a string.
Errors are returned as a serialized JSON string with is_error=true; never raised."""


class MessagesClient(Protocol):
    def create(self, **kwargs: Any) -> Any: ...


@dataclass
class FinalState:
    messages: list[dict[str, Any]]
    total_input_tokens: int
    total_output_tokens: int
    turn_count: int
    final_content: list[Any] = field(default_factory=list)


def run(
    *,
    client: Any,
    model: str,
    system: str,
    tools: list[dict[str, Any]],
    messages: list[dict[str, Any]],
    tool_executor: ToolExecutor,
    budget: Budget,
    tracer: Tracer,
    max_tokens: int = 4096,
) -> FinalState:
    """Run the agentic loop until the model returns stop_reason == "end_turn".

    The loop condition is `response.stop_reason == "tool_use"` — nothing else.
    There is no `while turn < N` cap. The Budget object is the safety mechanism.
    """
    working_messages = list(messages)
    turn = 0
    total_input = 0
    total_output = 0

    while True:
        turn += 1
        budget.check()
        t0 = time.monotonic()
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            tools=tools,
            messages=working_messages,
        )
        latency_ms = (time.monotonic() - t0) * 1000.0

        input_tokens = int(response.usage.input_tokens)
        output_tokens = int(response.usage.output_tokens)
        total_input += input_tokens
        total_output += output_tokens
        budget.record_input_tokens(input_tokens)

        # TODO:Build a trace record for this turn and write it.
        # The record is a dict with these keys:
        #     turn:           the turn counter
        #     stop_reason:    response.stop_reason
        #     tool_calls:     a list of {id, name, input} dicts, one per tool_use block
        #                     in response.content (skip non-tool_use blocks)
        #     latency_ms:     round(latency_ms, 1)
        #     input_tokens:   input_tokens
        #     output_tokens:  output_tokens
        # Call `tracer.write(record)`.

        # TODO:Triage on response.stop_reason. The whole point of the
        # agentic loop is that THIS is what drives control flow — not the message text,
        # not a turn count, not the presence of a magic string.
        #
        # Case 1: response.stop_reason == "end_turn"
        #   Append the assistant turn to working_messages:
        #       {"role": "assistant", "content": response.content}
        #   Return a FinalState carrying working_messages, the running token totals,
        #   the turn count, and the final assistant content.
        #
        # Case 2: response.stop_reason == "tool_use"
        #   Append the assistant turn to working_messages (same shape as Case 1).
        #   For every tool_use block in response.content, call
        #       tool_executor(block.name, dict(block.input))
        #   and collect the result into a tool_result block:
        #       {"type": "tool_result", "tool_use_id": block.id, "content": <result>}
        #   ALL of these tool_result blocks go into ONE user turn together — not one
        #   user turn per tool. Append that single user turn to working_messages and
        #   `continue` the loop.
        #
        # Case 3: anything else
        #   Raise UnexpectedStopReason naming the turn and the offending stop_reason.
        #   Do NOT silently retry, do NOT guess, do NOT treat max_tokens as success.
        raise NotImplementedError("Exercise 1: implement the stop_reason triage")
