# Starter — Exercise 2

This starter is byte-identical to Exercise 1's solution, with one addition: a starter `.claude/commands/review.md` containing `<!-- TODO: -->` blocks for the parts you author.

## Files you will edit

- `.claude/commands/review.md` — five TODO blocks:
  1. Frontmatter (`description`, `argument-hint`, read-only `allowed-tools` with granular `Bash(git diff:*)`-style entries).
  2. Phase 1 — Interview pattern subsection with concrete trigger conditions.
  3. Phase 2 — Must-report vs Skip taxonomy.
  4. Phase 3 — Interacting-vs-independent bundling paragraph.
  5. Two worked I/O examples in the `## Examples` section (one independent, one interacting).

## Run / verify

```bash
source .venv/bin/activate    # reuses the venv from Exercise 1
pytest -q tests/test_us01_claude_md_hierarchy.py tests/test_us02_path_scoped_rules.py tests/test_us03_review_command.py
```

Replace each TODO until pytest reports `21 passed`.
