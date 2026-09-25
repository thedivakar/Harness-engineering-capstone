"""Transcript loader and baseline token accounting."""
from __future__ import annotations

from pathlib import Path

import pytest

from retail_context import transcript
from retail_context.tokens import count

FIXTURE = Path(__file__).resolve().parent.parent / "data" / "transcript_48turns.json"


@pytest.fixture(scope="module")
def t():
    return transcript.load(FIXTURE)


def test_transcript_loader_turn_count(t):
    assert len(t.turns) == 48
    assert [turn.turn for turn in t.turns] == list(range(1, 49))


def test_transcript_loader_partition_boundaries(t):
    refund = t.segment("refund")
    subscription = t.segment("subscription")
    payment = t.segment("payment_update")
    assert refund.turn_range == (1, 14)
    assert subscription.turn_range == (15, 28)
    assert payment.turn_range == (29, 48)
    assert refund.status == "resolved"
    assert subscription.status == "resolved"
    assert payment.status == "active"


def test_transcript_loader_token_count_in_engineered_range(t):
    # Baseline is a large conversation that must be reduced by >=50%. The exact
    # count varies by tokenizer/model (heuristic ~47k; API haiku/sonnet ~38.7k;
    # API opus ~52.3k), so this window is deliberately wide.
    assert 35000 <= t.token_count <= 55000, (
        f"baseline token_count {t.token_count} outside expected range "
        f"[35000, 55000] (varies by tokenizer/model)"
    )


def test_active_turns_accessor(t):
    active = t.active_turns
    assert len(active) == 20
    assert active[0].turn == 29
    assert active[-1].turn == 48


def test_canonical_token_function_is_used_everywhere(t):
    # Spot check: count(full_text) equals .token_count
    assert count(t.full_text) == t.token_count
