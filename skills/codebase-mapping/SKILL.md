---
name: codebase-mapping
description: Generates and maintains a token-efficient, polyglot-aware CODEBASE_MAP.md index for any repository. Loaded by Mapper (sole writer) and Documenter (read/update only).
---

# Codebase Mapping Skill

## Overview

This skill teaches how to generate a token-efficient, polyglot-aware codebase index (`CODEBASE_MAP.md`) that any agent can read to locate modules, entry points, and conventions without opening source files.

The map is the single source of truth for repo structure. It is written once by Mapper, kept current after structural changes, and mirrored to Monday.com.

---

## When to Use

Trigger this skill when **any** of the following are true:

1. No `CODEBASE_MAP.md` exists for the target repo
2. A sprint changed the repo's module structure, entry points, or zone layout
3. Mapper is explicitly dispatched by Legion to map or re-map a repo

---

## Core Pattern

### Step 1 — Detect Ownership

Determine whether this is **our repo** (legion-swarm or a repo we own) or a **guest repo** (a client or third-party repo we are working in).

- **Our repo** → write `CODEBASE_MAP.md` to repo root AND mirror to Monday doc
- **Guest repo** → write Monday doc ONLY — zero files touched in their repo

### Step 2 — Detect Zones

Scan root-level directories and config files to identify language/runtime boundaries.

Config files to check: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `Gemfile`, `composer.json`

Each distinct runtime = one zone. Assign each zone:
- A short uppercase ID (e.g. `WEB`, `API`, `WORKER`, `INFRA`)
- A root path (relative)
- A language/runtime label
- A one-line responsibility statement

### Step 3 — Build the Map

Populate all five sections in order. Follow the format template exactly (see below). Rules:
- IDs must be short and uppercase
- Module paths are relative to repo root
- Key exports are comma-separated identifiers — no prose
- No markdown prose inside table cells
- Agent Notes are append-only — never delete past entries

### Step 4 — Deliver

**Our repo:**
1. Write `CODEBASE_MAP.md` to repo root
2. Mirror full content to Monday doc for this repo
3. Commit: `docs: generate CODEBASE_MAP.md`

**Guest repo:**
1. Write Monday doc only
2. Confirm zero files were written to their repo
3. Report to Legion via status update

---

## Updating an Existing Map

**When to update (not regenerate):**
- A module was added or renamed → update that row only
- An entry point changed → update Entry Points section
- A convention was confirmed → add to Conventions section

**When to regenerate from scratch:**
- A major refactor restructured multiple zones
- A zone was added or removed
- The map is clearly stale (>50% of rows wrong)

**How to update in place:**
1. Update `Last updated` date
2. Revise only the affected rows
3. Append a new Agent Notes entry with the date and what changed

---

## Guest vs Owner Behavior

| Scenario | Write CODEBASE_MAP.md | Write Monday Doc |
|----------|----------------------|-----------------|
| Our repo, no map exists | YES — generate and commit | YES — mirror |
| Our repo, map exists | Only if structure changed | YES — update mirror |
| Guest repo, no map exists | NO | YES — generate here |
| Guest repo, map exists | NO | YES — update here |

---

## CODEBASE_MAP.md Format

Every map must use this exact template. Do not invent sections or rename headers.

```markdown
# CODEBASE_MAP.md
Last updated: YYYY-MM-DD | Updated by: mapper

## Zones

| ID | Path | Language/Runtime | Responsibility |
|----|------|-----------------|----------------|
| WEB | apps/web | TypeScript/Next.js | User-facing frontend |
| API | apps/api | TypeScript/Node.js | REST API and business logic |

## Entry Points

| Zone | File | Purpose |
|------|------|---------|
| WEB | apps/web/src/app/page.tsx | Root Next.js page |
| API | apps/api/src/index.ts | Express server bootstrap |

## Modules

| Zone | Path | Responsibility | Key Exports |
|------|------|----------------|-------------|
| API | apps/api/src/auth | Authentication middleware | verifyToken, requireRole |
| API | apps/api/src/db | Database client and migrations | db, runMigrations |

## Conventions

| Category | Convention |
|----------|-----------|
| Branching | feature/* for features, fix/* for bugs |
| Testing | Vitest, tests co-located with source files |
| Env vars | .env.local for local, Vercel env for deployed |

## Agent Notes

| Date | Agent | Note |
|------|-------|------|
| YYYY-MM-DD | mapper | Initial map generated |
```

---

## Common Mistakes

1. **Writing to a guest repo** — never touch files in a repo you don't own. Monday doc only.
2. **Prose in table cells** — cells must contain identifiers, paths, or short labels. No sentences.
3. **Listing every file as a module** — group by responsibility, not by file. One row per logical unit.
4. **Forgetting to mirror to Monday** — every map write (our repo) must be followed by a Monday doc update.
5. **Regenerating the full map for a single module change** — update in place. Only regenerate on structural upheaval.
