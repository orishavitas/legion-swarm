# helm-dashboard — Codex KB

> Codex reads this file once at session start. Single source of truth for repo-specific context.
> For cross-repo and product-level context, see the Obsidian wiki (path below).

## What This Repo Does
A personal developer command center built on Next.js 15. Aggregates project status, sprint tasks, GitHub PRs, and Vercel deploy state into one authenticated dashboard. Single user (Ori Shavit). Live at localhost:3000 in dev; deployed to Vercel.

## Obsidian Wiki
- **Project page:** `~/obsidian/legion-wiki/wiki/projects/helm-dashboard.md`
- Read for architecture decisions and cross-repo context.

## Stack
- Language / runtime: TypeScript, Node.js 20
- Framework: Next.js 15 App Router (RSC + Server Actions + Route Handlers)
- Styling: Tailwind CSS, shadcn-compatible local UI primitives, lucide-react
- Auth: Auth.js v5 (next-auth), Google OAuth, database sessions
- ORM: Drizzle ORM 0.38 + Neon (serverless Postgres)
- Package manager: pnpm (corepack) — always `corepack pnpm <cmd>`
- Key dependencies: @tanstack/react-query, @octokit/auth-app, @octokit/rest, zod, clsx, tailwind-merge

## Repo Layout
```
app/
  (app)/          — authenticated route group
    layout.tsx    — app shell (nav + sidebar)
    page.tsx      — dashboard (project grid + global todos)
    projects/[id]/page.tsx — project detail
    settings/page.tsx
  (auth)/
    login/page.tsx
  api/
    auth/[...nextauth]/route.ts
    github/repos/route.ts, install/route.ts, callback/route.ts
    vercel/projects/route.ts
  globals.css
  layout.tsx      — root layout

components/
  app-shell.tsx
  project-card.tsx
  task-list.tsx
  todo-list.tsx
  query-provider.tsx
  forms/           — project-form, sprint-form, task-form, todo-form, integration-forms
  ui/              — button, badge, text-field, select-field

lib/
  actions/         — server actions: projects, sprints, tasks, todos, integrations
  data/            — read queries: projects.ts, todos.ts
  db/              — schema split: auth-schema, product-schema, integration-schema, enums, index, schema (re-export)
  integrations/    — github.ts, vercel.ts
  security/        — encryption.ts (AES-256-GCM)
  auth.ts, session.ts, env.ts, ownership.ts, utils.ts, view-models.ts

drizzle/           — migration SQL files
DOCS/
  helm-dashboard.md  — quick reference (stack, commands, env vars)
  REF/               — kickstart docs: PRD, tech specs, architecture, etc.
.codex/state/      — Codex runtime state (TASK_STATE, LAST_RUN, DECISIONS, HANDOFF_*)
```

## Conventions
- All pages are RSC by default. Only add `"use client"` when absolutely needed (forms with event handlers, TanStack Query).
- Server Actions live in `lib/actions/`. Each file = one domain. All must start with `"use server"`.
- Read queries in `lib/data/`. No mutations there.
- Auth guard: always call `requireUser()` at the top of protected server components.
- Ownership check: always call `assertProjectOwner(projectId, userId)` in actions before mutations.
- Soft deletes via `deletedAt` — always filter `isNull(deletedAt)` in queries.
- DB: `getDb()` returns Drizzle instance. Use pooled URL for app queries; `DATABASE_URL_UNPOOLED` for migrations only.
- Vercel tokens stored encrypted — use `lib/security/encryption.ts`. Never send raw token to client.
- No inline SQL — Drizzle query builder only.
- No comments unless the WHY is non-obvious.
- No `any` types.

## Known Issues / Gotchas
- GitHub/Vercel snapshot tables (`github_repo_snapshots`, `vercel_deployment_snapshots`) exist in schema but **are never populated** — there is no refresh job yet. This is the primary functional gap.
- No `/api/github/[owner]/[repo]/pulls` or `/commits` route handlers yet.
- No `/api/vercel/deployments/[projectId]` route handler yet.
- `types/` directory exists but is empty.
- `githubInstallationId` is not stored on `userIntegrations` during callback — verify the callback route fully persists the installation.
- No tests exist yet — TDD from here on.

## Key Files to Know
| File | Purpose |
|------|---------|
| `lib/db/product-schema.ts` | projects, sprints, tasks, todos |
| `lib/db/integration-schema.ts` | userIntegrations, githubRepoSnapshots, vercelDeploymentSnapshots |
| `lib/db/auth-schema.ts` | users, accounts, sessions |
| `lib/data/projects.ts` | `getProjectSummaries()` + `getProjectDetail()` — primary read path |
| `lib/actions/integrations.ts` | save Vercel token, link GitHub/Vercel to project |
| `lib/integrations/github.ts` | GitHub App auth, listInstallationRepos, getOpenPullRequests |
| `lib/integrations/vercel.ts` | Vercel API calls with encrypted token |
| `lib/security/encryption.ts` | AES-256-GCM encrypt/decrypt for Vercel token |
| `lib/view-models.ts` | TypeScript types for all UI-facing data shapes |
| `DOCS/REF/02-prd.md` | Full PRD — feature requirements and acceptance criteria |
| `DOCS/REF/03-tech-specs.md` | Data models, API contracts, env vars |

## How to Run Tests
```bash
# No test runner configured yet — first task is to add one
corepack pnpm typecheck
corepack pnpm lint
```

## How to Run the App Locally
```bash
corepack pnpm dev
# Starts on http://localhost:3000
# Requires .env.local with DATABASE_URL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, ENCRYPTION_KEY
# App boots without AUTH_SECRET in dev; uses fallback secret
```

## Active Sprint
`docs/sprints/2026-05-06-helm-dashboard-sprint-01-overlord-monitor.md`
GitHub: https://github.com/orishavitas/helm-dashboard/blob/master/DOCS/sprints/2026-05-06-helm-dashboard-sprint-01-overlord-monitor.md
Goal: Overlord Monitor — terminal heartbeat push endpoint, state poll endpoint, `<OverlordPanel>` widget.
Start task: `helm-overlord-01`

## Codex Runtime State
> `.codex/state/` in repo root — Codex reads and writes these every session.

| File | Written by | Purpose |
|------|-----------|---------|
| `TASK_STATE.md` | Legion | Current objective, constraints, task context |
| `LAST_RUN.md` | Codex | What last session did, commands run, result, remaining risk |
| `DECISIONS.md` | Legion / Codex | Architectural/product decisions that must not be reversed |
| `HANDOFF_[ts].md` | `scripts/codex-handoff.ps1` | Timestamped snapshot for Legion audit |
| `MONDAY_UPDATE.md` | `scripts/codex-handoff.ps1` | Dual-format `[TECHNICAL]` and `[SUMMARY]` update that Legion posts to Monday |

Scripts (repo root):
- `scripts/codex-handoff.ps1` — run at session end (done or blocked) to write `HANDOFF_[timestamp].md` and `MONDAY_UPDATE.md`
- `scripts/codex-dialogue-check.ps1` — check TURN.md at session start
- `scripts/codex-watchdog-check.ps1` — check for STOP sentinel at session start

Stop conditions (Codex must stop and write BLOCKED):
- Tests fail twice for the same unclear reason
- Unrelated dirty files in git status
- Next step requires product or architecture judgment
- `git push --dry-run` fails
- `db:migrate` fails on Neon connection (do not retry more than once)
