# API standards (Node.js)

These apply to all handlers under `src/api/`. The path-scoped rule `.claude/rules/api.md` adds enforcement details that only fire when editing API files.

## Handler shape

- `async` functions only. No callback-based handlers.
- Each handler returns `{ status, body }` (never writes to the response object directly) — the framework adapter does the actual write. This keeps handlers testable without HTTP fixtures.

## Errors

- Throw `ApiError(status, code, message)` for any expected failure (validation, not-found, auth). The middleware turns it into a structured response.
- Never `throw new Error(...)` from handler code — those bubble as 500s and obscure the real cause.
- Unexpected exceptions propagate to the global handler. Do not catch-and-rethrow without adding context.

## Inputs

- Validate request bodies at the boundary with the shared `zod` schemas in `src/api/_schemas/`. Do not re-validate downstream.

## Outputs

- Response bodies match the schemas in `src/api/_schemas/responses/`. Adding a field to a response requires updating the schema in the same commit.
