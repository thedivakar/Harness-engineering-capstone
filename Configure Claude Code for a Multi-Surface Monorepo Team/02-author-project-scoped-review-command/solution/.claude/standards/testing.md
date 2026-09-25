# Testing standards

The path-scoped rule `.claude/rules/tests.md` adds rules that *only* apply when editing `*.test.ts(x)` files. This file covers cross-cutting expectations.

## Where tests live

- Tests are co-located with source: `Cart.tsx` next to `Cart.test.tsx`. No parallel `__tests__/` mirror tree.
- Integration tests that span modules live in `tests/integration/`.

## What to test

- Component tests assert on rendered output and user-visible behavior, not internal hook state.
- API handler tests call the handler function directly with a request shape — never spin up the HTTP layer.
- Repository tests hit a real PostgreSQL test instance (Docker Compose configures one for CI). Mocking the DB layer is forbidden — we got burned by a mocked test that hid a broken migration.

## What not to test

- Generated code (Prisma client, OpenAPI types).
- Third-party library behavior — trust the library or wrap it.
