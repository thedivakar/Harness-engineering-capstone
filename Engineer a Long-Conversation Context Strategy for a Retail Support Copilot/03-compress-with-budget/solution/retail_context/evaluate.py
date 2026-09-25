"""Eval-question runner.

Issues one Claude call per question with the assembled context as the system prompt
and the question as the user turn. A question passes when the expected fragment
appears (case-insensitive) in the model's answer. Pass threshold ≥ 5/6.

Also runs a control variant with the Case Facts block removed; Q1 (refund amount)
and Q6 (active-card last-4) must FAIL in the control — that's how we verify the
case-facts block is doing real work rather than being coincidentally redundant
with the active verbatim section.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from retail_context.client import complete_with_system

EVAL_SYSTEM_PREFIX = (
    "You are a retail customer-support assistant for Pantry Plus. The conversation"
    " context for the current customer is provided below. Answer the question concisely"
    " using only information present in the context. If the answer is not present,"
    " say 'unknown' — do not invent.\n\n"
)


@dataclass
class EvalResult:
    question_id: str
    question: str
    expected_fragment: str
    model_answer: str
    passed: bool
    input_tokens: int
    output_tokens: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "question_id": self.question_id,
            "question": self.question,
            "expected_fragment": self.expected_fragment,
            "model_answer": self.model_answer,
            "passed": self.passed,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
        }


def _passed(expected: str, answer: str) -> bool:
    return expected.lower() in answer.lower()


def run_questions(
    questions: list[dict[str, Any]],
    context_markdown: str,
    *,
    model: str | None = None,
) -> list[EvalResult]:
    system = EVAL_SYSTEM_PREFIX + context_markdown
    results: list[EvalResult] = []
    for q in questions:
        answer, in_tok, out_tok = complete_with_system(
            system,
            q["question"],
            model=model,
            max_tokens=256,
        )
        results.append(
            EvalResult(
                question_id=q["id"],
                question=q["question"],
                expected_fragment=q["expected_fragment"],
                model_answer=answer,
                passed=_passed(q["expected_fragment"], answer),
                input_tokens=in_tok,
                output_tokens=out_tok,
            )
        )
    return results


def strip_case_facts(context_markdown: str) -> str:
    """Return the assembled context with the `# Case Facts` block removed.

    The control variant — Q1 and Q6 must fail when this block is gone.
    """
    lines = context_markdown.splitlines()
    out: list[str] = []
    skipping = False
    for line in lines:
        if line.startswith("# Case Facts"):
            skipping = True
            continue
        if skipping and line.startswith("# "):
            skipping = False
        if not skipping:
            out.append(line)
    return "\n".join(out).lstrip("\n")


def write_jsonl(results: list[EvalResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for r in results:
            f.write(json.dumps(r.to_dict()) + "\n")
