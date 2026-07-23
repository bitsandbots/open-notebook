# Frontend Rules (frontend/)

Normative rules for working on the Next.js frontend. Architecture and flow walkthroughs live in [docs/7-DEVELOPMENT/frontend.md](../docs/7-DEVELOPMENT/frontend.md) — this file is only what you must know before changing code. Project-wide rules are in the root [AGENTS.md](../AGENTS.md).

## Commands (run inside `frontend/`)

- Dev server: `npm run dev` (port 3000; API must be up at 5055 first)
- Lint: `npm run lint` (`eslint src/`)
- Tests: `npm run test` (`vitest run`) · coverage: `npm run test:coverage`
- Build: `npm run build`
- Run a production build locally: after `npm run build`, `output: "standalone"` (`next.config.ts`) writes a self-contained server to `.next/standalone/`, but it does **not** include static assets — copy them in first: `cp -r .next/static .next/standalone/.next/static && cp -r public .next/standalone/public`, then `node .next/standalone/server.js` (or `node start-server.js`, which just defaults `PORT` to 8502 and requires the same file). Mirrors the `frontend-builder` stage in the root `Dockerfile` — check there if the copy list ever changes.

## Hard rules

- **i18n is mandatory**: every UI string goes through `t('section.key')` and the key must exist in **all locales** under `src/lib/locales/` (currently 14; en-US is the reference). Missing keys fall back to en-US silently — keep locales in sync. Each non-en-US locale ends with `satisfies TranslationShape` (type derived from en-US), so a missing/extra key fails `tsc`; the parity test (`src/lib/locales/index.test.ts`) checks the same at runtime.
- All requests go through `apiClient` (`src/lib/api/client.ts`); never create a second axios instance. Auth token is auto-added from localStorage key `auth-storage`.
- Data fetching uses TanStack Query hooks in `src/lib/hooks/` with `QUERY_KEYS`; mutations invalidate caches and show toasts (sonner). Follow the existing hook shape.
- FormData requests: nested objects/arrays must be `JSON.stringify`-ed before appending; the interceptor strips Content-Type so the browser sets the multipart boundary — don't re-add it.
- No automatic request retry — handle failures in the consuming code (podcast retry is an explicit endpoint/hook, not a client retry).

## Gotchas

- Zustand stores with `persist`: check `hasHydrated` before rendering persisted state (SSR hydration mismatch), and keep each store's `name` key unique (localStorage collision).
- `NEXT_PUBLIC_API_TIMEOUT_MS`: default 600000 (10 min) for slow LLM calls; `0` disables the timeout.
- SSE (`useAsk`): incomplete lines stay in the buffer between reads; incomplete JSON is silently skipped — don't "simplify" the buffer handling.
- **`next dev` buffers SSE responses until the connection closes** — Ask/Search (`/api/search/ask`) and chat (`/api/sources/[sourceId]/chat/sessions/[sessionId]/messages`), both proxied through `src/app/api/_sse-proxy.ts`, will appear to hang with zero incremental output under the dev server, then dump the entire stream at once right before it closes. This is a Turbopack dev-server limitation, not a bug in `_sse-proxy.ts`, `ask.py`, or `use-ask.ts` — all stream correctly under `next start`/the standalone build. Don't chase a "hung" Ask/chat request as an app bug without first checking whether the frontend is running in dev mode; if it is, reproduce against a production build before concluding anything is actually broken.
- `useSourceStatus` polls every 2s while status is `running`/`queued`/`new`.
- Cache invalidation is deliberately broad (e.g. `['sources']` hits all source queries) — a simplicity/perf trade-off, be precise only when it matters.
- Dark mode requires the `dark` class on the document root, not just `prefers-color-scheme`. It's hand-rolled: the zustand `theme-store` (persisted as `theme-storage`) sets the class via `ThemeProvider` — no next-themes.
- Dialogs don't auto-reset form state (parent clears it) and auto-focus the first input (layout shift risk with conditional inputs). Fixed overlays use `z-50`.
- Provider nesting order in `app/layout.tsx` matters: ErrorBoundary → ThemeProvider → QueryProvider → I18nProvider → ConnectionGuard → Toaster. ErrorBoundary is a class component and uses the raw `enUS` locale object (no hooks).
- `i18n` runs with `useSuspense: false` (no SSR for translations).

## Deep dives

[frontend architecture](../docs/7-DEVELOPMENT/frontend.md) · [credentials system](../docs/7-DEVELOPMENT/credentials.md) · [change playbooks](../docs/7-DEVELOPMENT/change-playbooks.md) (i18n / frontend-only changes) · [code standards](../docs/7-DEVELOPMENT/code-standards.md)
