"""Anti-pattern audit.

Verifies, by static AST analysis, that the agentic loop does NOT:
- use string-membership tests against text content to drive control flow
- use an integer-literal iteration cap as its primary stopping mechanism
- omit reference to `stop_reason` as the loop-breaking signal

And that the package broadly does not branch on `claim_type` equality
outside of the tool-schema definitions and the cost-estimate module.
"""

from __future__ import annotations

import ast
from pathlib import Path

PKG = Path(__file__).resolve().parents[1] / "claims_intake"
LOOP_PY = PKG / "loop.py"


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


# ---------------------------------------------------------------------------
# No string-membership tests against assistant text drive control flow
# ---------------------------------------------------------------------------
def test_no_string_membership_against_text_in_loop() -> None:
    """No `"some_token" in <something>` expressions in loop.py.

    Heuristic: any Compare node using `In` whose left operand is a string
    Constant is flagged. The loop has no legitimate reason to test for the
    presence of a magic string inside the model's output.
    """
    tree = _parse(LOOP_PY)
    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for op in node.ops:
                if isinstance(op, ast.In) and isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
                    offenders.append(ast.unparse(node))
    assert offenders == [], (
        "loop.py contains string-membership tests that may be driving control flow:\n  "
        + "\n  ".join(offenders)
    )


# ---------------------------------------------------------------------------
# No integer-literal iteration cap as the primary stopping mechanism
# ---------------------------------------------------------------------------
def test_no_integer_literal_iteration_cap_in_loop() -> None:
    """No `for _ in range(<int literal>)` and no `while <var> < <int literal>` in loop.py.

    Token/wall-clock/config-sourced budgets are explicitly allowed because
    they read their cap from a `Budget` instance (an attribute access or a
    function arg), not from a literal. If you need a cap, pass it in.
    """
    tree = _parse(LOOP_PY)
    offenders: list[str] = []

    for node in ast.walk(tree):
        # `for _ in range(<int literal>, ...)`
        if (
            isinstance(node, ast.For)
            and isinstance(node.iter, ast.Call)
            and isinstance(node.iter.func, ast.Name)
            and node.iter.func.id == "range"
            and any(isinstance(a, ast.Constant) and isinstance(a.value, int) for a in node.iter.args)
        ):
            offenders.append(f"for-range-literal at line {node.lineno}: {ast.unparse(node.iter)}")

        # `while <something> <comparison-with-int-literal>`
        if isinstance(node, ast.While) and isinstance(node.test, ast.Compare):
            for cmp in node.test.comparators:
                if isinstance(cmp, ast.Constant) and isinstance(cmp.value, int):
                    offenders.append(f"while-int-literal at line {node.lineno}: {ast.unparse(node.test)}")

    assert offenders == [], (
        "loop.py uses an integer-literal iteration cap as a stopping mechanism. "
        "Use a Budget (token or wall-clock, sourced from config) instead:\n  "
        + "\n  ".join(offenders)
    )


# ---------------------------------------------------------------------------
# stop_reason is referenced in loop.py and breaks the while loop
# ---------------------------------------------------------------------------
def test_stop_reason_is_loop_control() -> None:
    tree = _parse(LOOP_PY)

    references = [
        node
        for node in ast.walk(tree)
        if (isinstance(node, ast.Attribute) and node.attr == "stop_reason")
        or (isinstance(node, ast.Name) and node.id == "stop_reason")
    ]
    assert references, "loop.py never references stop_reason"

    # Find the main while loop and verify it both contains a `stop_reason`
    # reference AND exits via either a `return` or `raise` predicated on it.
    while_loops = [n for n in ast.walk(tree) if isinstance(n, ast.While)]
    assert while_loops, "loop.py has no `while` loop"

    found_stop_reason_exit = False
    for wloop in while_loops:
        body_text = "\n".join(ast.unparse(n) for n in wloop.body)
        if "stop_reason" in body_text and ("return" in body_text or "raise" in body_text):
            found_stop_reason_exit = True
            break
    assert found_stop_reason_exit, (
        "No `while` loop in loop.py exits via a return/raise predicated on stop_reason. "
        "The loop must terminate on stop_reason == 'end_turn' and raise on unexpected values."
    )


# ---------------------------------------------------------------------------
# No `if claim_type == "..."` branching outside tools.py / pricing.py
# ---------------------------------------------------------------------------
def test_no_claim_type_equality_branching_in_package() -> None:
    """Decision logic about claim type lives in the model, not in Python.

    tools.py is exempt (it defines the enum in the input_schema).
    pricing.py is exempt (it may map claim_type to per-queue cost weights).
    """
    exempt = {"tools.py", "pricing.py"}
    offenders: list[str] = []

    for py_file in PKG.rglob("*.py"):
        if py_file.name in exempt or py_file.name == "__init__.py":
            continue
        tree = _parse(py_file)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Compare):
                continue
            if not any(isinstance(op, ast.Eq) for op in node.ops):
                continue
            left = node.left
            left_name = (
                left.attr if isinstance(left, ast.Attribute)
                else left.id if isinstance(left, ast.Name)
                else None
            )
            if left_name != "claim_type":
                continue
            if any(isinstance(c, ast.Constant) and isinstance(c.value, str) for c in node.comparators):
                offenders.append(f"{py_file.name}:{node.lineno}: {ast.unparse(node)}")

    assert offenders == [], (
        "Python is branching on claim_type equality. Move this decision into the model "
        "(via tool calls and prompts), not into harness code:\n  "
        + "\n  ".join(offenders)
    )
