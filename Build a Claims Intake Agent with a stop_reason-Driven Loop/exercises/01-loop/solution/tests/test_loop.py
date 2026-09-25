from typing import Any

import pytest

from claims_intake.budget import Budget, BudgetExceeded
from claims_intake.loop import UnexpectedStopReason, run
from claims_intake.tracer import NullTracer
from tests.fakes import FakeBlock, FakeClient, FakeMessages, FakeResponse, FakeUsage


def _budget() -> Budget:
    return Budget(max_input_tokens=1_000_000, max_wall_clock_s=60.0)


def _noop_executor(name: str, inp: dict[str, Any]) -> str:
    return '{"ok": true}'


def test_loop_terminates_on_end_turn() -> None:
    """A response with stop_reason=='end_turn' returns immediately."""
    scripted = [
        FakeResponse(
            content=[FakeBlock(type="text", text="done")],
            stop_reason="end_turn",
            usage=FakeUsage(input_tokens=10, output_tokens=5),
        ),
    ]
    client = FakeClient(messages=FakeMessages(scripted=scripted))
    tracer = NullTracer()

    state = run(
        client=client,
        model="fake-model",
        system="sys",
        tools=[],
        messages=[{"role": "user", "content": "hi"}],
        tool_executor=_noop_executor,
        budget=_budget(),
        tracer=tracer,
    )

    assert state.turn_count == 1
    assert state.total_input_tokens == 10
    assert state.total_output_tokens == 5
    assert tracer.events[0]["stop_reason"] == "end_turn"


def test_loop_continues_on_tool_use() -> None:
    """A response with stop_reason=='tool_use' triggers executor and another turn."""
    scripted = [
        FakeResponse(
            content=[
                FakeBlock(type="tool_use", id="tu_1", name="lookup_policy", input={"policy_id": "P1"}),
            ],
            stop_reason="tool_use",
            usage=FakeUsage(input_tokens=20, output_tokens=10),
        ),
        FakeResponse(
            content=[FakeBlock(type="text", text="all done")],
            stop_reason="end_turn",
            usage=FakeUsage(input_tokens=30, output_tokens=5),
        ),
    ]
    client = FakeClient(messages=FakeMessages(scripted=scripted))
    tracer = NullTracer()
    executed: list[tuple[str, dict[str, Any]]] = []

    def executor(name: str, inp: dict[str, Any]) -> str:
        executed.append((name, inp))
        return '{"coverage": "full"}'

    state = run(
        client=client,
        model="fake-model",
        system="sys",
        tools=[],
        messages=[{"role": "user", "content": "claim"}],
        tool_executor=executor,
        budget=_budget(),
        tracer=tracer,
    )

    assert state.turn_count == 2
    assert state.total_input_tokens == 50
    assert executed == [("lookup_policy", {"policy_id": "P1"})]
    assert [e["stop_reason"] for e in tracer.events] == ["tool_use", "end_turn"]
    assert tracer.events[0]["tool_calls"][0]["name"] == "lookup_policy"


def test_loop_handles_multiple_tool_use_blocks_in_one_turn() -> None:
    """All tool_use blocks in a single assistant turn execute and return in ONE user turn."""
    scripted = [
        FakeResponse(
            content=[
                FakeBlock(type="tool_use", id="tu_1", name="lookup_policy", input={"policy_id": "P1"}),
                FakeBlock(type="tool_use", id="tu_2", name="record_claim_fact", input={"field": "x", "value": "y"}),
            ],
            stop_reason="tool_use",
            usage=FakeUsage(input_tokens=20, output_tokens=10),
        ),
        FakeResponse(
            content=[FakeBlock(type="text", text="ok")],
            stop_reason="end_turn",
            usage=FakeUsage(input_tokens=15, output_tokens=5),
        ),
    ]
    client = FakeClient(messages=FakeMessages(scripted=scripted))

    run(
        client=client,
        model="fake-model",
        system="sys",
        tools=[],
        messages=[{"role": "user", "content": "x"}],
        tool_executor=_noop_executor,
        budget=_budget(),
        tracer=NullTracer(),
    )

    # The second create() call should have received the assistant turn plus ONE user turn
    # containing two tool_result blocks (not two separate user turns).
    second_call_messages = client.messages.calls[1]["messages"]
    # original user + assistant + new user (with tool_results)
    assert len(second_call_messages) == 3
    last_user = second_call_messages[-1]
    assert last_user["role"] == "user"
    tool_results = last_user["content"]
    assert len(tool_results) == 2
    assert {tr["tool_use_id"] for tr in tool_results} == {"tu_1", "tu_2"}


def test_loop_raises_on_unexpected_stop_reason() -> None:
    """Any stop_reason other than tool_use / end_turn raises — no silent retry."""
    scripted = [
        FakeResponse(
            content=[],
            stop_reason="max_tokens",
            usage=FakeUsage(input_tokens=10, output_tokens=4096),
        ),
    ]
    client = FakeClient(messages=FakeMessages(scripted=scripted))

    with pytest.raises(UnexpectedStopReason):
        run(
            client=client,
            model="fake-model",
            system="sys",
            tools=[],
            messages=[{"role": "user", "content": "x"}],
            tool_executor=_noop_executor,
            budget=_budget(),
            tracer=NullTracer(),
        )


def test_budget_raises_when_token_cap_exceeded() -> None:
    """Budget enforcement is the safety net, and it raises rather than truncating."""
    scripted = [
        FakeResponse(
            content=[FakeBlock(type="tool_use", id="tu_1", name="x", input={})],
            stop_reason="tool_use",
            usage=FakeUsage(input_tokens=500, output_tokens=10),
        ),
        FakeResponse(
            content=[FakeBlock(type="tool_use", id="tu_2", name="x", input={})],
            stop_reason="tool_use",
            usage=FakeUsage(input_tokens=600, output_tokens=10),
        ),
        FakeResponse(
            content=[FakeBlock(type="text", text="done")],
            stop_reason="end_turn",
            usage=FakeUsage(input_tokens=10, output_tokens=5),
        ),
    ]
    client = FakeClient(messages=FakeMessages(scripted=scripted))
    tight_budget = Budget(max_input_tokens=1000, max_wall_clock_s=60.0)

    with pytest.raises(BudgetExceeded):
        run(
            client=client,
            model="fake-model",
            system="sys",
            tools=[],
            messages=[{"role": "user", "content": "x"}],
            tool_executor=_noop_executor,
            budget=tight_budget,
            tracer=NullTracer(),
        )
