# Database standards (PostgreSQL, repository pattern)

## Repositories

- Each table has a single repository module in `src/db/` exposing typed query functions.
- Handlers and services depend on repository functions — never on raw SQL or the connection pool.
- Repository functions return domain types from `src/db/types.ts`, not row records.

## Transactions

- Multi-statement writes use `withTransaction(async (tx) => ...)` from `src/db/tx.ts`. Never compose writes across multiple `await pool.query` calls without a wrapping transaction.

## Migrations

- Forward migrations only. To "roll back," write a new forward migration.
- Migration filenames: `NNNN__short_description.sql` (four-digit zero-padded sequence).
