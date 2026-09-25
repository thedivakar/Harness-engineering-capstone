"""Shape and consistency tests for the canonical token counter.

These are unit-level checks that pass with or without ANTHROPIC_API_KEY set —
the SDK path is exercised under the live `--build` run, not here.
"""
from __future__ import annotations

from retail_context.tokens import count, methodology


def test_count_zero_for_empty_string():
    assert count("") == 0


def test_count_returns_positive_int_for_nonempty_text():
    n = count("the quick brown fox")
    assert isinstance(n, int)
    assert n >= 1


def test_count_grows_with_length():
    assert count("hello world" * 100) > count("hello world")


def test_methodology_returns_descriptive_string():
    m = methodology()
    assert isinstance(m, str)
    assert len(m) > 0
    # The methodology line is what `budget.json` records so reviewers can
    # interpret the numbers. It must mention an algorithm.
    assert any(token in m.lower() for token in ("heuristic", "count_tokens", "endpoint"))
