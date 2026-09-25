"""Canonical token counting for the retail_context project.

Methodology — two paths planned:

1. **SDK path (preferred)** — Anthropic `messages.count_tokens` endpoint
   (model-authoritative). Active when `ANTHROPIC_API_KEY` is set.
2. **Heuristic path (fallback)** — `len(text) / 3.8` (a documented Claude
   tokenizer approximation, ~3.8 characters per token in English). Active when
   no API key is available (e.g., local development against the Claude Code
   subscription, where the count_tokens endpoint is not exposed via the CLI).

Tokenization specifics are out of scope, so the choice of algorithm does not
matter here. What matters is that *every* measurement in this
project flows through this single function. The active methodology is recorded
in `runs/<run_id>/budget.json` so the reviewer can interpret the numbers.

The current build only implements the heuristic path. Exercise 3 expands it.
"""
from __future__ import annotations

import os
from functools import lru_cache

from retail_context.client import get_client, get_model

_CHARS_PER_TOKEN = 3.8


def methodology() -> str:
    # TODO (Exercise 3): Return the string naming the currently active path.
    # When ANTHROPIC_API_KEY is set, return:
    #     "Anthropic messages.count_tokens endpoint (model-authoritative)"
    # otherwise return:
    #     f"len(text) / {_CHARS_PER_TOKEN} heuristic (no API key available)"
    # The returned string is written verbatim into budget.json so reviewers can
    # interpret the per-section numbers without re-deriving the algorithm.
    return f"len(text) / {_CHARS_PER_TOKEN} heuristic (stub — Exercise 3 adds the SDK dispatch)"


@lru_cache(maxsize=4096)
def count(text: str) -> int:
    if not text:
        return 0
    # TODO (Exercise 3): When ANTHROPIC_API_KEY is set, route the request through
    # the SDK's `messages.count_tokens` endpoint:
    #     resp = get_client().messages.count_tokens(
    #         model=get_model(),
    #         messages=[{"role": "user", "content": text}],
    #     )
    #     return int(resp.input_tokens)
    # When the key is not set, fall back to the heuristic below. The cap of 1
    # is intentional — a non-empty string never reports 0 tokens.
    return max(1, int(len(text) / _CHARS_PER_TOKEN))


def count_many(texts: list[str]) -> int:
    return sum(count(t) for t in texts)
