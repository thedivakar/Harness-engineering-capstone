# Starter — Exercise 1

## Files you will edit

Each location is marked with a `# TODO:` (or `<!-- TODO:` for markdown) comment so it's grep-friendly:

- `CLAUDE.md` — three TODO blocks: scope-distinction table, `@-import` block, `/memory` troubleshooting one-liner.
- `.claude/rules/api.md` — two TODO blocks: YAML frontmatter (`description` + `paths`) and at least one concrete API convention in the body.
- `.claude/rules/tests.md` — two TODO blocks: YAML frontmatter (with a glob that cross-cuts the React and API directories) and at least one concrete testing convention.

`.claude/rules/react.md` and `.claude/standards/*.md` are already complete and serve as worked examples.

## Run / verify

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q tests/test_us01_claude_md_hierarchy.py tests/test_us02_path_scoped_rules.py
```

You should see failures while the TODOs are unfilled. Replace each TODO until pytest reports `13 passed`.
