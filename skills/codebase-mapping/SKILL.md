---
name: codebase-mapping
description: Generates and maintains CODEBASE_MAP.md — a token-efficient, polyglot-aware codebase index that lets any agent locate anything without opening files. Used by Mapper (sole writer) and Documenter (reader/reference).
---

# Codebase Mapping Skill

## Overview

This skill teaches you to generate and maintain `CODEBASE_MAP.md` — a token-efficient, language-agnostic index of a repository's structure. Any agent on the swarm reads this file to locate zones, entry points, modules, and conventions without opening a single source file. Accuracy and brevity are both required: every cell must be a short identifier or path, never prose. Mapper is the only agent that writes to this file. All others read it.

---

## When to Use

Use this skill when any of the following is true:

1. No `CODEBASE_MAP.md` exists for this repo and the repo belongs to us.
2. A sprint changed the repo's module structure, entry points, or zone layout (new directory, renamed module, new runtime, removed service).
3. Mapper is explicitly dispatched by Legion to generate or update the map.

Do not use this skill for logic-only changes (no structural change = no map update needed).

---

## Core Pattern — Four Steps

### Step 1: Detect Ownership

Determine whether this is our repo or a guest repo.

- **Our repo**: `CODEBASE_MAP.md` is written to the repo root and committed. A Monday mirror is also created or updated.
- **Guest repo**: A Monday doc is generated with the same map content. Zero files are touched in the guest repo — no commits, no writes, no traces.

If unsure: check whether the repo path is under `C:/Users/OriShavit/repos/` or a known org. When in doubt, treat as guest and write only to Monday.

### Step 2: Detect Zones

Scan the root-level directories and config files to identify language/runtime boundaries. Each distinct runtime is a zone.

Config files that signal a zone boundary:
- `package.json` / `tsconfig.json` → TypeScript/Node.js
- `pyproject.toml` / `requirements.txt` / `setup.py` → Python
- `Cargo.toml` → Rust
- `go.mod` → Go
- `pom.xml` / `build.gradle` → Java/JVM
- `Gemfile` → Ruby
- `composer.json` → PHP

For each zone, record:
- **ID**: short, uppercase (e.g. `WEB`, `API`, `WORKER`, `SHARED`)
- **Path**: relative to repo root
- **Language/Runtime**: e.g. `TypeScript/Next.js`, `Python/FastAPI`
- **Responsibility**: one short phrase — what this zone does

A monorepo may have 4+ zones. A single-language repo may have 1.

### Step 3: Build the Map

Populate all five sections in order. IDs must be short and uppercase. Module paths are relative. Key exports are comma-separated identifiers — no prose.

Sections in order:
1. **Zones** — one row per runtime boundary
2. **Entry Points** — one row per zone's main entry file, with line number
3. **Modules** — one row per logical grouping of files (not one row per file)
4. **Conventions** — one row per zone: state management, test framework, style system
5. **Agent Notes** — dated notes from Mapper for significant structural changes

Group files by responsibility into modules. If a zone has 40 files, the Modules table may have 6-10 rows — not 40.

### Step 4: Deliver

**Our repo:**
1. Write `CODEBASE_MAP.md` to the repo root
2. Mirror identical content to the Monday board doc for this repo
3. Commit: `docs: update CODEBASE_MAP.md — [brief reason]`

**Guest repo:**
1. Write content to Monday doc only
2. Confirm zero files were written to the guest repo
3. Report: `Map update needed: NO` (Monday doc is the map for guest repos)

---

## Updating an Existing Map

### Does This Sprint Require a Map Update?

| Change type | Update needed? |
|-------------|----------------|
| New directory or moved directory | YES |
| New module (new group of files with distinct responsibility) | YES |
| Entry point changed | YES |
| New zone (new runtime added) | YES |
| Zone removed or merged | YES |
| Logic-only change (no structural change) | NO |
| Rename within same zone, same responsibility | YES |
| Test file added (no new module) | NO |

### How to Update In Place

Do not regenerate the full map when only one module changed:
1. Update the `Last updated` line at the top
2. Add an Agent Note entry at the bottom with today's date and what changed
3. Revise only the affected rows in the relevant section(s)

### When to Regenerate from Scratch

Regenerate the full map when:
- A major refactor changed zone boundaries or zone responsibilities
- A zone was added or removed
- 30%+ of module paths changed in a single sprint

---

## Guest vs Owner Behavior

| Situation | Map Location | Repo Changes |
|-----------|-------------|--------------|
| Our repo — map exists | Update `CODEBASE_MAP.md` in root + Monday mirror | YES — committed |
| Our repo — no map yet | Mapper generates it from scratch | YES — first commit |
| Guest repo — map exists (Monday doc) | Update Monday doc only | ZERO |
| Guest repo — no map yet | Mapper generates Monday doc from scratch | ZERO |

---

## CODEBASE_MAP.md Format

Agents must reproduce this format exactly. No variations in section names, column order, or header levels.

```markdown
# Codebase Map — [repo-name]
> Last updated: [Mapper] [YYYY-MM-DD]

## Zones
| ID | Path | Language/Runtime | Responsibility |
|----|------|-----------------|----------------|
| WEB | apps/web/ | TypeScript/Next.js | Frontend app |
| API | apps/api/ | Python/FastAPI | REST backend |
| WORKER | services/worker/ | Rust | Background jobs |
| SHARED | packages/shared/ | TypeScript | Shared types/utils |

## Entry Points
| Zone | What | Where |
|------|------|-------|
| WEB | App root | apps/web/src/index.tsx:1 |
| API | Server | apps/api/main.py:1 |
| WORKER | Binary entry | services/worker/src/main.rs:1 |

## Modules
| ID | Path | Responsibility | Key exports |
|----|------|----------------|-------------|
| AUTH | src/auth/ | Authentication, session management | `login()`, `logout()`, `useSession` |
| API.USERS | src/api/users/ | User CRUD | `getUser()`, `updateUser()` |

## Conventions
| Zone | State | Tests | Styles |
|------|-------|-------|--------|
| WEB | React Context | Vitest | Tailwind |
| API | Stateless | pytest | — |
| WORKER | — | cargo test | — |

## Agent Notes
> [Mapper — YYYY-MM-DD] [note about what changed and why]
```

### Column Definitions

**Zones table**
- `ID`: 2-8 uppercase chars, unique across the map
- `Path`: relative path from repo root, trailing slash
- `Language/Runtime`: language + framework if applicable
- `Responsibility`: ≤6 words

**Entry Points table**
- `Zone`: matches ID from Zones table
- `What`: short label (`App root`, `Server`, `CLI entrypoint`)
- `Where`: relative path + `:line`

**Modules table**
- `ID`: zone prefix + `.` + module name, uppercase (e.g. `API.USERS`)
- `Path`: relative path
- `Responsibility`: ≤8 words
- `Key exports`: comma-separated identifiers only, backtick-wrapped

**Conventions table**
- `Zone`: matches ID from Zones table
- `State`: state management approach or `—`
- `Tests`: test framework name or `—`
- `Styles`: CSS approach or `—`

**Agent Notes**
- One bullet per significant structural change
- Format: `> [Mapper — YYYY-MM-DD] [note]`

---

## Common Mistakes

1. **Writing to a guest repo.** Never commit, write, or touch any file in a guest repo. The Monday doc IS the map. If you wrote a file to a guest repo, revert it immediately.

2. **Using prose in table cells.** Table cells must be identifiers, paths, or short labels — never full sentences. Wrong: `Handles all user authentication including OAuth`. Correct: `Auth, session management`.

3. **One row per file instead of grouping by responsibility.** A module is a logical grouping (e.g. `src/auth/`), not a file (e.g. `src/auth/login.ts`). If your Modules table has more rows than the repo has directories, you are listing files — regroup by responsibility.

4. **Forgetting to mirror to Monday after writing the file.** Every map write to a repo file must be followed by a Monday doc update with the same content. Agents on mobile or in other contexts read from Monday, not from the filesystem.

5. **Regenerating the full map when only one module changed.** Regeneration is expensive and introduces drift. Update in place: revise only the affected rows, update the `Last updated` line, and add an Agent Note. Full regeneration is only for major refactors or zone-level changes.
