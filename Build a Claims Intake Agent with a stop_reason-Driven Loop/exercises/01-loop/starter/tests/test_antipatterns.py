"""Anti-pattern audit.

Verifies, by static AST analysis, that the agentic loop does NOT:
- use string-membership tests against text content to drive control flow
- use an integer-literal iteration cap as its primary stopping mechanism
- omit reference to `stop_reason` as the loop-breaking signal

And that the package broadly does not branch on `claim_type` equality
outside of the tool-schema definitions and the cost-estimate module.

Each test parses the relevant file with `ast` and walks the tree. There are
no runtime imports of claims_intake here — the audit is static, so it works
even if loop.py / tools.py do not run end-to-end.
"""

from __future__ import annotations

import ast
from pathlib import Path

PKG = Path(__file__).resolve().parents[1] / "claims_intake"
LOOP_PY = PKG / "loop.py"


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


# ---------------------------------------------------------------------------
# Anti-pattern 1 — no string-membership tests against assistant text in the loop
# ---------------------------------------------------------------------------
def test_no_string_membership_against_text_in_loop() -> None:
    """No `"some_token" in <something>` expressions in loop.py.

    Heuristic: any `ast.Compare` node using `ast.In` whose `left` operand is a
    string `ast.Constant` is flagged. The loop has no legitimate reason to test
    for the presence of a magic string inside the model's output — that would be
    natural-language-driven control flow.
    """
    # TODO:Parse LOOP_PY into an AST. Walk every node. For each
    # ast.Compare, look at its `ops` — if any op is ast.In AND `node.left` is an
    # ast.Constant holding a `str`, append `ast.unparse(node)` to an offenders list.
    # Assert the offenders list is empty; include the offending expressions in the
    # failure message so a reader can find the bad line.
    raise NotImplementedError("Exercise 2: write this AST audit")


# ---------------------------------------------------------------------------
# Anti-pattern 2 — no integer-literal iteration cap as the primary stop mechanism
# ---------------------------------------------------------------------------
def test_no_integer_literal_iteration_cap_in_loop() -> None:
    """No `for _ in range(<int literal>)` and no `while <var> < <int literal>` in loop.py.

    Token/wall-clock/config-sourced budgets are explicitly allowed because they
    read their cap from a `Budget` instance (an attribute access or a function
    arg), not from a literal. If you need a cap, pass it in.
    """
    # TODO:Walk LOOP_PY's AST. Flag:
    #   - any ast.For whose iter is `range(<int literal>, ...)`
    #     (ast.Call to a Name "range" with at least one Constant int arg)
    #   - any ast.While whose test is an ast.Compare with an int Constant on the right
    # Assert the offenders list is empty. Mention "use a Budget instead" in the failure
    # message so the reader sees the recommended fix.
    raise NotImplementedError("Exercise 2: write this AST audit")


# ---------------------------------------------------------------------------
# Positive evidence — stop_reason is the value that breaks the while loop
# ---------------------------------------------------------------------------
def test_stop_reason_is_loop_control() -> None:
    """loop.py references `stop_reason` AND a `while` loop exits via return/raise on it."""
    # TODO:Parse LOOP_PY. Walk the tree:
    #   1. Assert there is at least one reference to `stop_reason` (either as an
    #      ast.Attribute named `stop_reason` or an ast.Name named `stop_reason`).
    #   2. Find every ast.While node. For at least one of them, the unparsed body
    #      must mention BOTH "stop_reason" AND ("return" OR "raise"). That is what
    #      "the loop exits on stop_reason" looks like at the AST level.
    # Fail with a clear message if either condition is missing.
    raise NotImplementedError("Exercise 2: write this AST audit")


# ---------------------------------------------------------------------------
# Decision-tree-in-Python — no `if claim_type == "..."` branches in the package
# ---------------------------------------------------------------------------
def test_no_claim_type_equality_branching_in_package() -> None:
    """Decision logic about claim type lives in the model, not in Python.

    tools.py is exempt (it defines the enum in input_schema).
    pricing.py is exempt (it may map claim_type to per-queue cost weights).
    """
    # TODO:Walk every .py file under PKG (recursively). Skip tools.py,
    # pricing.py, and __init__.py. For each file, parse the AST, find every ast.Compare
    # whose operators include ast.Eq and whose left operand is a Name/Attribute named
    # "claim_type" compared against a string Constant. Collect "filename:lineno: <expr>"
    # for each match. Assert the list is empty; recommend in the failure message that
    # you move the decision into the model via tool calls.
    raise NotImplementedError("Exercise 2: write this AST audit")
