# Exercise 4: Assemble the Engineered Context and Locate It on the Anatomy

*Assemble the engineered context with case facts at the top boundary, resolved summaries in the middle, and the active segment verbatim at the bottom boundary, using explicit section headers — and locate this work on the context-window anatomy diagram (Layer 2).*

This is the capstone. When you finish, `python -m retail_context.run --all` produces the full set of artifacts (`context.md`, `budget.json`, `case_facts_call.json`, `eval.jsonl`, `eval_control.jsonl`) and the README carries the writeup that ties the layout to the lost-in-the-middle effect and to Layer 2 of the context-window anatomy.

---

## What you start with

`starter/` is byte-identical to Exercise 3's `solution/` — your pruner, case-facts extractor, canonical token counter, compressor, and budget block are all in place. New for Exercise 4:

- `retail_context/assemble.py` is now the active file you implement (two TODO blocks: the header-contract dicts and the `build()` body).
- `README.md` has three writeup sections stubbed (`<!-- TODO (Exercise 4): ... -->`): the context-window anatomy diagram, "Why this layout?", and the before/after token budget table.
- The full test suite is now in scope — `tests/test_assemble.py` becomes the verify target for the assembler, and `python -m retail_context.run --all` will run end-to-end for the first time.

## What to build

1. **`assemble.py`** — fill in the two TODO blocks:
   - `RESOLVED_TITLES: dict[str, str]` and `ACTIVE_TITLES: dict[str, str]` — the exact-text header contract. `# Case Facts`, `# Resolved: Refund inquiry`, `# Resolved: Subscription cancellation`, `# Active issue: Payment-method update`. The AST audit regex-matches these strings; level-1 headings only.
   - `build(case_facts, compressed) -> AssembledContext`:
     - Top boundary: `case_facts.to_markdown()` (case-facts block).
     - Middle: each resolved-section block, in declaration order (refund → subscription), formatted as `f"{RESOLVED_TITLES[issue_id]}\n\n{summary_text}\n"`.
     - Bottom boundary: `f"{active_title}\n\n{compressed.active_text}\n"`, body byte-exact.
     - Final `markdown` = top + blank line + refund block + blank line + subscription block + blank line + active block.
     - Construct and return an `AssembledContext` with `markdown`, `case_facts_block`, `resolved_blocks`, `active_block`, and `active_raw_text=compressed.active_text` (the AST audit uses `active_raw_text` to verify the assembled active body equals the raw turns).

2. **`README.md`** — replace the three `<!-- TODO (Exercise 4): ... -->` blocks:
   - **Context-window anatomy.** A five-layer diagram (system prompt → CLAUDE.md → memory → conversation history → current turn) plus one paragraph naming which layer *this project* operates on. ASCII or Mermaid — what matters is that a reviewer can read a labeled box and find the corresponding section of `runs/<id>/context.md`.
   - **Why this layout?** 3–5 sentences citing the "lost in the middle" attention effect, the resolved-vs-active fidelity tradeoff, and the pass-complete-history baseline this project deliberately deviates from (only for resolved threads).
   - **Before / after token budget.** One line naming the methodology (sourced from `tokens.methodology()` and recorded in `budget.json`), followed by a Markdown table populated from `runs/<id>/budget.json` — per-section + assembled total + baseline + reduction percentage.

## Verify

```bash
pytest tests/ -v
ANTHROPIC_API_KEY=sk-ant-... python -m retail_context.run --all
```

What you should see:

- All 28 tests pass (2 skipped are the run-artifact tests; the `--all` run below populates them on the next pytest invocation).
- `runs/<id>/` contains five files: `context.md`, `budget.json`, `case_facts_call.json`, `eval.jsonl`, `eval_control.jsonl`.
- `eval.jsonl` shows ≥5/6 questions passing.
- `eval_control.jsonl` (Q1 + Q6 against a case-facts-stripped variant) shows **Q6 FAIL** — that's the project's main payoff. The structured `in_progress` status token for the payment-update issue lives *only* in the case-facts block; once you strip the block, the model has no way to recover that fact from the resolved summaries or the active verbatim. This is the empirical proof that the persistent block is load-bearing.

If you re-run `pytest tests/` after the `--all` run, the previously-skipped `test_assembled_context_active_segment_byte_exact` and `test_budget_json_section_counts_sum_consistently` will run against the artifacts in `runs/<id>/` and pass.

## Where to look if you get stuck

- **The header contract is part of the API the model sees.** Using `## Section` instead of `# Section` would still parse as Markdown but would change what the model picks up as a section boundary. The audit's exact-text match is the defense.
- **Why is the order refund → subscription → active and not something else?** The position contract: top boundary holds the densest structured content (case facts), middle holds the compressible-with-acceptable-fidelity-loss zone (resolved summaries, ordered by when each issue was opened in the transcript), bottom boundary holds the still-being-negotiated content where every turn matters (active verbatim, against the new user turn). Changing this order is a different concern than the one this exercise focuses on.
- **The README writeup is what makes the anatomy mapping measurable.** The diagram alone doesn't demonstrate the mapping; what does is the *map* from a labeled layer in the diagram to a corresponding section of the `context.md` you just produced. Write it so a reviewer can point at a box and find the bytes.

## When you're done

The diff you produced — `assemble.py` + the three README sections — is the entirety of Exercise 4. `solution/` is the reference and equals the original `module-02-retail-context-strategy/` repo modulo cleanup-only differences. You now hold a complete, working context strategy for a long-conversation customer-support copilot, with the auditable artifacts (`context.md`, `budget.json`, `eval.jsonl`) that a compliance reviewer or a design-review meeting would expect.
