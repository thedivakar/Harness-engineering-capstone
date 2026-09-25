# Exercise 4 — Document the Plan-Mode vs Direct-Execution vs Explore Decision Framework

## What you'll build

A `docs/plan-mode-vs-direct-execution.md` decision doc with a Knight-Webb citation block and four worked examples drawn from this repo's scaffold:

1. **Plan mode** — extracting a shared `useCart` hook across three components.
2. **Direct execution** — adding a `min: 0` validation to one quantity field.
3. **Explore sub-agent** — inventorying `processRefund` call sites with the scratchpad pattern.
4. **Combined workflow** — renaming `ordersRepo.findById` → `getById` (investigate, then mechanical edit).

## What's already provided

The `starter/` directory contains everything you produced in Exercises 1-3 plus a starter `docs/plan-mode-vs-direct-execution.md` with the intro paragraph, the four section dividers, and the Quick Reference table at the bottom already filled in. Your TODOs are the Knight-Webb citation and the four worked examples.

## How to run

```bash
cd starter/
pytest -q
ecommerce-team-config .
```

## Verify command

```bash
pytest -q && ecommerce-team-config .
```

Expected at completion: **35 passed, 0 failed** for pytest; **`OK`** for the CLI. Your finished work matches the complete reference repo.
