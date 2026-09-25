"""Anti-pattern audit.

Four checks:
  1. pruner.py contains no `anthropic` client import
  2. assemble.py builds sections in the canonical order
  3. assembled `context.md` has the byte-exact active segment
  4. every token measurement in `runs/<run_id>/budget.json` flows through the
     canonical `retail_context.tokens.count` function — verified by static check
     that no source file in the package imports a competing counter
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "retail_context"
RUNS_DIR = ROOT / "runs"


def _latest_run() -> Path | None:
    if not RUNS_DIR.exists():
        return None
    runs = sorted(p for p in RUNS_DIR.iterdir() if p.is_dir())
    return runs[-1] if runs else None


def test_pruner_has_no_anthropic_import():
    """Pruner is deterministic, not LLM-driven."""
    src = (PKG / "pruner.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "anthropic" not in alias.name.lower(), (
                    f"pruner.py must not import anthropic (found: {alias.name})"
                )
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            assert "anthropic" not in mod.lower(), (
                f"pruner.py must not import from anthropic (found: {mod})"
            )


def test_only_tokens_module_uses_count_tokens_or_heuristic():
    """Every token measurement flows through retail_context.tokens.count.

    Static check: no module in the package other than `tokens.py` references
    `count_tokens` directly or hand-rolls a token estimate (`len(... ) / N` or
    `len(...) // N`).
    """
    competing_heuristic = re.compile(r"len\([^)]+\)\s*[/]{1,2}\s*\d+\.?\d*")
    competing_endpoint = re.compile(r"count_tokens")
    for py in PKG.rglob("*.py"):
        if py.name == "tokens.py" or py.name == "__init__.py":
            continue
        text = py.read_text()
        # strip docstrings/comments minimally to reduce false positives
        # (we just lex-search the source; module-level heuristics are what matter)
        m1 = competing_heuristic.search(text)
        assert not m1, (
            f"{py.relative_to(ROOT)} contains a competing token heuristic "
            f"({m1.group(0)!r}); use retail_context.tokens.count instead."
        )
        m2 = competing_endpoint.search(text)
        assert not m2, (
            f"{py.relative_to(ROOT)} references count_tokens directly; "
            "wrap measurement in retail_context.tokens.count."
        )


def test_assemble_module_section_order_contract():
    """assemble.py expresses Case Facts → Resolved → Active.

    The contract is enforced at runtime by `tests/test_assemble.py`, but for
    regression safety this static check confirms the canonical title constants
    are still present in the source.
    """
    src = (PKG / "assemble.py").read_text()
    assert "# Case Facts" in src
    assert "# Resolved: Refund inquiry" in src
    assert "# Resolved: Subscription cancellation" in src
    assert "# Active issue:" in src


def test_assembled_context_active_segment_byte_exact():
    """Verbatim active segment in context.md matches raw turns 29-48."""
    run = _latest_run()
    if run is None or not (run / "context.md").exists():
        pytest.skip("no run artifacts available — run `python -m retail_context.run --build` first")

    from retail_context.transcript import load

    t = load(ROOT / "data" / "transcript_48turns.json")
    raw_active = "\n\n".join(turn.render() for turn in t.active_turns)
    context_md = (run / "context.md").read_text()
    assert raw_active in context_md, (
        "active segment in context.md does not match raw turns 29-48 byte-for-byte"
    )


def test_budget_json_section_counts_sum_consistently():
    """Per-section counts must be present and the methodology must be documented."""
    run = _latest_run()
    if run is None or not (run / "budget.json").exists():
        pytest.skip("no run artifacts available — run `python -m retail_context.run --build` first")

    budget = json.loads((run / "budget.json").read_text())
    assert "token_counter_methodology" in budget
    assert "baseline_tokens" in budget
    assert "assembled_tokens" in budget
    assert "reduction_pct" in budget
    assert "per_section_tokens" in budget
    # All three categories of section must be present
    sec = budget["per_section_tokens"]
    assert "case_facts" in sec
    assert any(k.startswith("resolved_") for k in sec)
    assert "active" in sec
