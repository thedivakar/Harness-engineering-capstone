# Exercise 1: Trim the Verbose `lookup_order` Response

*Trim a verbose 57-field tool response down to exactly the 5 fields needed for return/refund reasoning using deterministic field selection (no LLM call), and justify each kept field in a docstring that links it to the decision the tool supports.*

---

## What you start with

`starter/` is the project bootstrap scaffold. The pieces you need for Exercise 1:

- `data/lookup_order_response.json` — a real 57-field tool response from an `order_lookup` call.
- `retail_context/pruner.py` — a stub with three `# TODO (Exercise 1):` blocks.
- `tests/test_pruner.py` — the verify target.
- `tests/test_antipatterns.py::test_pruner_has_no_anthropic_import` — the AST audit that enforces the pruner stays LLM-free.

The other modules in `retail_context/` (`tokens.py`, `case_facts.py`, `compressor.py`, `assemble.py`, …) are present as later-exercise stubs. You do not edit them in this exercise. If you run `pytest tests/` against the whole suite you will see those stubs raise `NotImplementedError` — that is expected; the scoped verify command below is what to run.

## What to build

Open `starter/retail_context/pruner.py` and resolve the three TODO blocks:

1. The module-docstring justification — one sentence per kept field naming why it is decision-load-bearing for return/refund reasoning.
2. The `KEPT_FIELDS: tuple[str, ...]` constant — the exact 5 fields, in output order.
3. The `prune_lookup_order(raw: dict) -> dict` body — missing-field check raising `PrunerMissingFieldError`, then an order-preserving 5-field projection.

The pruner has **no `anthropic` import**. The AST audit will fail if you reach for an LLM to "decide" which fields to keep — the LO is *deterministic* tool pruning, and the audit is the reviewer's check that you wrote it that way.

## Verify

From inside the exercise directory (`starter/` or your in-progress copy):

```bash
pytest tests/test_pruner.py tests/test_antipatterns.py::test_pruner_has_no_anthropic_import -v
```

All five tests must pass:

- `test_pruner_keeps_exactly_the_contracted_set` — the 5-field contract.
- `test_pruned_output_preserves_declaration_order` — output dict order matches `KEPT_FIELDS`.
- `test_pruned_output_under_200_tokens` — quantified savings vs the 57-field raw.
- `test_pruner_raises_on_missing_required_field` — loud failure mode.
- `test_pruner_has_no_anthropic_import` — AST audit.

## Where to look if you get stuck

- **The 5 fields are listed inline** in the TODO comment in the module docstring. The important part is the *justification* — naming why each one matters for the return/refund decision.
- **"Why these 5 specifically?"** Each one anchors a different question the agent has to answer: *who* placed the order (identity), *when* it was placed (return window starts here), *how much* it cost (caps the refund), *where it is now* (refund vs. cancel routing), and *until when* the customer is eligible (the deadline).
- **`KEPT_FIELDS` is a `tuple`, not a `list`** because the output order is part of the contract — using an unordered container would let a future refactor silently reorder the dict.

## When you're done

The diff you produced is the entirety of Exercise 1's solution. Compare to `solution/retail_context/pruner.py` for the reference. Exercise 2 picks up from that solution.
