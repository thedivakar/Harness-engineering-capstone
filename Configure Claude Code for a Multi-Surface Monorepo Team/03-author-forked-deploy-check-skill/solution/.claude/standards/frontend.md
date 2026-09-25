# Frontend standards (React)

These apply across the whole frontend. Path-scoped rules in `.claude/rules/react.md` layer on top with rules that *only* apply when editing components/pages.

## Components

- Function components only. No class components.
- Props are typed via `interface` (not `type`) when the shape may be extended by composition; `type` is fine for unions and one-off shapes.
- Co-locate component-only types in the component file. Promote to `src/types/` only when re-used across modules.

## Hooks

- Custom hooks live in `src/hooks/` and start with `use`.
- Side effects only inside `useEffect` / event handlers — never inline in the render body.
- Dependency arrays are exhaustive. If you're tempted to omit a dep, the value belongs in a ref or the effect belongs elsewhere.

## State

- Local component state via `useState` / `useReducer`. App-wide state via the existing `CartContext` / `SessionContext` providers — do not add a fourth state library.

## Styling

- Tailwind utility classes for layout/spacing. Component-specific overrides via CSS modules co-located with the component.
