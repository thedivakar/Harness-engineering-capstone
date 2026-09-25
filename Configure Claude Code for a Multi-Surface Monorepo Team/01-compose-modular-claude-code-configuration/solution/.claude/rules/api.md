---
description: Conventions for Node.js API handlers
paths:
  - "src/api/**/*"
---

# API handler rules

Loads when editing any file under `src/api/`.

## Handler signature

- Every handler is `async function handle(req: ApiRequest<TBody>): Promise<ApiResponse<TOut>>`. The framework adapter does the actual response write — handlers never call `res.send`.
- The `TBody` and `TOut` type parameters come from the schemas in `src/api/_schemas/`. Inline anonymous types here are not allowed.

## Error handling

- Throw `new ApiError(400, "VALIDATION_FAILED", "...")` for validation errors. Do not return a `{ status: 400 }` shape — let the middleware translate the throw.
- For not-found: `throw new ApiError(404, "NOT_FOUND", "...")`. Never return `{ status: 404, body: null }`.
- For unexpected failures: let the exception propagate. Do not catch-log-rethrow without adding context.

## Database access

- Handlers depend on functions exported from `src/db/<table>.ts`. They must not import `pool` or `prisma` directly.
- Multi-write operations must wrap in `withTransaction(async (tx) => { ... })` from `src/db/tx.ts`.

## Input validation

- Validate the request body with `bodySchema.parse(req.body)` at the very top of the handler, before any other work.
- Do not re-validate the parsed body downstream — once it has passed `parse`, trust the type.

## Logging

- Use the request-scoped logger `req.log.info({ field: value }, "message")`. Bare `console.log` is forbidden in `src/api/`.
- Log levels: `debug` for development hints, `info` for normal request milestones, `warn` for recoverable issues, `error` for caught exceptions only.
