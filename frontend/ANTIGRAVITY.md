# Salt to Taste — Frontend Agent Context

## Project
This is the Next.js 14 App Router PWA frontend for "Salt to Taste".
It connects to a FastAPI backend running at http://localhost:8000/api/v1.

## Stack
- Next.js 14 with App Router and TypeScript
- Tailwind CSS for styling (mobile-first)
- Zustand for client state
- React Query (@tanstack/react-query) for server state
- Axios for HTTP requests
- lucide-react for icons
- next-pwa for PWA support

## File Structure
- src/app/ — Next.js App Router pages
- src/components/ — Reusable UI components
- src/store/ — Zustand state stores
- src/lib/ — API client, utilities, types
- src/hooks/ — Custom React hooks
- public/ — Static assets, PWA icons

## Key Rules
- Always use "use client" directive for components with state or event handlers
- Never call fetch directly — use src/lib/api.ts functions
- All touch targets must be at least 44px tall (kitchen use on mobile)
- Never use inline styles — Tailwind classes only
- TypeScript strict mode is on — no `any` types
- React Query for ALL API calls — no useEffect+fetch patterns
- Default user ID comes from NEXT_PUBLIC_DEFAULT_USER_ID env var

## Backend Endpoints Used
- POST /recipes — submit recipe text/URL
- POST /recipes/image-upload — submit cookbook photo
- GET /recipes/{id}/sodium-breakdown — ingredient sodium detail
- GET /recipes/{id}/scale?target_servings=N — scale recipe
- POST /feedback — submit Perfect/Too Salty/Needs More
- GET /salt-types — list salt types
- POST /salt/convert — convert between salt types
- POST /recommendations/salty-swap — mid-cook adjustment
- POST /rescue — over-salted rescue protocol
- GET /palate/{user_id} — palate summary
- GET /palate/{user_id}/history — feedback history
- GET /health/sodium-report/{user_id} — health dashboard
- GET /health/daily-log/{user_id} — today's sodium log
