---
description: Conventions for React components and pages
paths:
  - "src/components/**/*"
  - "src/pages/**/*"
---

# React component & page rules

Loads when editing any file under `src/components/` or `src/pages/`.

## Imports

- Import React types as `import type { ... } from "react"` — never mixed with value imports. This keeps the dead-code-elimination boundary obvious.
- App-internal imports use the `@/` alias (resolved by Vite). Relative `../../../foo` paths are a code smell — promote the shared module instead.

## Component shape

- One default export per file, named to match the filename (`Cart.tsx` exports `Cart`).
- Props go through an `interface FooProps` declared in the same file. Do not spread arbitrary HTML attributes onto components — list the props you accept.
- Always destructure props in the function signature: `function Cart({ items, onCheckout }: CartProps)`.

## Hooks within components

- Custom hooks called inside the component body, top-level only — no hooks inside conditions, loops, or callbacks.
- When a component grows past ~150 lines, extract logic into a custom hook in `src/hooks/` before adding another `useState`.

## Accessibility

- Interactive elements use semantic tags (`button`, `a`, `label`). Do not put `onClick` on a `div` to make a clickable element.
- All images have a real `alt` attribute. Decorative images get `alt=""` explicitly, not omitted.

## Forbidden

- `dangerouslySetInnerHTML` — if you think you need it, talk to a senior engineer first.
- `useLayoutEffect` outside of `src/hooks/` — almost always `useEffect` is what you actually want.
