"""Shape and guard tests for the resolved-segment compressor.

The `summarize_segment` LLM call itself is exercised under the live `--build`
run; here we check the dataclass shapes, the resolved-only guard (which raises
before any Claude call), and the prompt-template loader.
"""
from __future__ import annotations

import pytest

from retail_context.compressor import (
    Compressed,
    Summary,
    _load_prompt,
    summarize_segment,
)
from retail_context.transcript import Segment, Turn


def test_summary_dataclass_carries_token_counts():
    s = Summary(issue_id="refund", text="...", input_tokens=10, output_tokens=200)
    assert s.input_tokens == 10
    assert s.output_tokens == 200


def test_compressed_dataclass_carries_active_text_and_id():
    c = Compressed(summaries={}, active_text="raw turns", active_issue_id="payment_update")
    assert c.active_issue_id == "payment_update"


def test_summarize_segment_refuses_to_compress_the_active_segment():
    """The active segment must be preserved byte-exact — never summarized."""
    active = Segment(
        issue_id="payment_update",
        turns=[Turn(turn=29, role="customer", text="hi", issue_id="payment_update")],
        status="active",
    )
    with pytest.raises(ValueError, match="resolved"):
        summarize_segment(active)


def test_compression_prompt_is_committed_and_nontrivial():
    body = _load_prompt()
    # The prompt template is reviewed for intent. It must be present
    # and substantive; an empty file would fail the audit.
    assert len(body) > 100
    # The 3-part structure must be implied somewhere in the prompt — at
    # minimum an "Outcome", "facts/bullets", and "Resolution" beat.
    lowered = body.lower()
    assert "outcome" in lowered
    assert "resolution" in lowered or "resolved" in lowered
