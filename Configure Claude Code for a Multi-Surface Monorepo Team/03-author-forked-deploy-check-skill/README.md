# Exercise 3 — Author the Forked `/deploy-check` Skill

## What you'll build

A `.claude/skills/deploy-check/SKILL.md` file that runs the team's pre-deployment checklist in a **forked sub-agent**, keeping verbose intermediate output out of the main session. Frontmatter must declare `context: fork` and a read-only `allowed-tools` allowlist; the body must include a skill-vs-`CLAUDE.md` rubric, a main-session-isolation rationale (with a Branching-Reality reference), three checks (each with Detect / Pass / Fail), and a personal-customization note.

## What's already provided

The `starter/` directory contains everything you produced in Exercises 1-2 plus a starter `.claude/skills/deploy-check/SKILL.md` with the intro paragraph, the Output format section, and the "What this skill deliberately does not do" section already filled in. Your TODOs are the frontmatter, the skill-vs-CLAUDE.md rubric, the `context: fork` rationale, the three checks, and the personalization note.

## How to run

```bash
cd starter/
pytest -q tests/test_us01_claude_md_hierarchy.py tests/test_us02_path_scoped_rules.py tests/test_us03_review_command.py tests/test_us04_deploy_check_skill.py
ecommerce-team-config .
```

## Verify command

```bash
pytest -q tests/test_us01_claude_md_hierarchy.py tests/test_us02_path_scoped_rules.py tests/test_us03_review_command.py tests/test_us04_deploy_check_skill.py && ecommerce-team-config .
```

Expected at completion: **28 passed** for pytest; **`OK`** for the CLI.

## Troubleshooting

- **IDE LSP warning on `context: fork` or `allowed-tools`.** The current Claude Code skill-frontmatter LSP (2026-05) lists only `argument-hint`, `compatibility`, `description`, `disable-model-invocation`, `license`, `metadata`, `name`, `user-invokable`. The skill-frontmatter documentation is the authoritative source; the LSP lags. Your `context: fork` is correct — proceed. If the warning is blocking, a temporary workaround is `metadata: {context: fork}`, but the canonical, correct form is the top-level field.
- **Frontmatter fails to load with a "nested mapping" error.** This is the YAML colon-inside-value trap. An unquoted value like `argument-hint: <target: optional>` parses as a nested map and breaks the file. Quote the value: `argument-hint: "[target] (defaults to main)"`.
