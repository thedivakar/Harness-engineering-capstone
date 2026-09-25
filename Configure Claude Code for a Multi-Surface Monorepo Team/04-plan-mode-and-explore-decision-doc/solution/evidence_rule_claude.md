# E-Commerce Platform — Shared Claude Code Conventions

This file is the **project-level** entry point for the e-commerce monorepo. Every teammate's Claude session loads it automatically.

## Scope: what belongs here vs. elsewhere

Claude Code resolves configuration in a hierarchy:

| Scope | Path | Purpose |
|-------|------|---------|
| **Project-level** | `./CLAUDE.md`, `.claude/standards/`, `.claude/rules/` | Conventions for *this* repo. Lives in git. Shared with the whole team. |
| **User-level** | `~/.claude/CLAUDE.md`, `~/.claude/commands/`, `~/.claude/skills/` | Personal preferences. **Not shared via version control** — they stay on your laptop and never reach teammates. |
| **Directory-level** | `path/CLAUDE.md` inside a subdir | Conventions narrower than the whole repo. We prefer `.claude/rules/` with glob `paths:` instead, so cross-cutting conventions (e.g. test files everywhere) work cleanly. |

If something would only matter to you — your preferred commit-message style, your editor-specific snippets, a personal `/morning` summary command — put it under `~/.claude/`. Anything the whole team should agree on goes here in `./CLAUDE.md` or under `.claude/standards/`.

## Shared standards (modular via @-imports)

The actual conventions live in focused files so this entry point stays scannable:

- @.claude/standards/frontend.md
- @.claude/standards/api.md
- @.claude/standards/database.md
- @.claude/standards/testing.md

Path-scoped rules in [.claude/rules/](.claude/rules/) layer on top of these standards and activate only when Claude is editing matching files (React components, API handlers, test files).

## Repository layout

```
src/components/   React components (functional + hooks)
src/pages/        Top-level routes
src/api/          Node.js API handlers
src/db/           PostgreSQL repository-pattern modules
```

Tests are co-located: `Foo.tsx` lives next to `Foo.test.tsx`.

## Troubleshooting

**Convention isn't being followed?** Run `/memory` in your Claude Code session to see exactly which configuration files actually loaded. The most common cause is an instruction that lives in `~/.claude/CLAUDE.md` (user-level, never shared) when it should be in this file or under `.claude/standards/`.

## Team workflows

- `/review <pr-ref>` — codified PR review checklist. See [.claude/commands/review.md](.claude/commands/review.md).
- `/deploy-check` — read-only pre-deployment validation, runs in a forked sub-agent to keep its output out of your main session. See [.claude/skills/deploy-check/SKILL.md](.claude/skills/deploy-check/SKILL.md).

For decisions about when to use plan mode vs. direct execution on this codebase, see [docs/plan-mode-vs-direct-execution.md](docs/plan-mode-vs-direct-execution.md).
