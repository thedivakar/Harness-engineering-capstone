---
description: Conventions for test files (co-located *.test.ts and *.test.tsx)
paths:
  - "**/*.test.tsx"
  - "**/*.test.ts"
---

# Test file rules

Loads when editing any co-located test file anywhere in the tree. Applies on top of the React or API rules when the file under test sits in those directories.

## Structure

- One top-level `describe` per file, named after the unit under test (`describe("Cart", () => { ... })`).
- Group related cases with nested `describe`. Avoid deeper than 2 nesting levels.
- Each `it("...")` description starts with a verb and describes observable behavior: `it("disables checkout when cart is empty")`, not `it("works")`.

## Assertions

- Use `expect(...).toBe(...)` for primitives, `toEqual` for objects/arrays. Never `toBeTruthy()` on a value where the exact shape matters.
- Prefer one assertion per case. If a test needs four `expect` calls, it is probably four tests.

## Test data

- Build domain objects via the factories in `src/test/factories/` (e.g. `aCart({ items: [...] })`). Inline literal objects make refactors painful.
- Time-sensitive assertions use the `freezeTime("2026-01-15T10:00:00Z")` helper. Real `Date.now()` is forbidden in tests.

## Forbidden

- Snapshot tests for component output — they pass for the wrong reasons and rot silently.
- Mocking the database layer in repository tests. Hit the real test PostgreSQL instance via the Docker Compose fixture.
- `setTimeout` / `setInterval` in tests. Use `vi.useFakeTimers()` and advance explicitly.

## Coverage expectations

- New behavior requires at least one test covering the happy path and one covering an explicit edge case (empty input, max boundary, error state). PRs without both will be flagged by `/review`.
