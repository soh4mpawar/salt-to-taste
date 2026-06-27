---
name: nextjs-patterns
description: Next.js 14 App Router conventions for Salt to Taste frontend. Load when working on any file in frontend/src/.
---

# Next.js Patterns for Salt to Taste

## Architecture
- App Router (not Pages Router) — all pages in src/app/
- Server Components by default — add "use client" only when needed
- API calls go through src/lib/api.ts — never call fetch directly in components
- Global state in src/store/ via Zustand
- All UI components in src/components/
- Page components in src/app/(routes)/

## Styling
- Tailwind only — no CSS modules, no styled-components
- Mobile-first: start with base styles, add md: and lg: breakpoints
- Kitchen color palette defined in tailwind.config.ts
- Touch targets minimum 44px height for kitchen use

## State Management
- Zustand stores in src/store/
- One store per domain: useRecipeStore, usePalateStore, useHealthStore
- Never put server state in Zustand — use React Query for that
- Zustand for: current recipe, scaling state, UI preferences

## API
- All endpoints defined in src/lib/api.ts
- React Query for all data fetching and mutations
- API base URL from NEXT_PUBLIC_API_URL env var
- Always handle loading and error states

## PWA
- next-pwa configured in next.config.ts
- Service worker handles offline caching
- App installable on mobile home screen
