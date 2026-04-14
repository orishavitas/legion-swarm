# Legion Context Layer v2 — Design Spec
> 2026-04-14 | Status: Approved

## Goal

Give Legion instant cross-repo awareness at session start. Replace status-grouped Monday board with project-grouped board. Add Obsidian vault as compiled knowledge layer. Add agent sign-in/sign-off protocol to verify skill loadout on launch. Add Legion self-verification loop to prevent self-coding drift.

---

## Problem Statement

1. **Zero cross-repo state at session start** — Legion reads one board, one repo. Other repos are dark.
2. **Monday groups = statuses** — agent-centric, not project-centric. Hard to answer "what's the state of repo X."
3. **No agent launch verification** — agents launch but there's no confirmation they loaded their identity + skills correctly.
4. **Legion drift** — Legion reverts to fixing things itself instead of dispatching. No automated check enforces the "never code" rule.

---

## Architecture

```
Session Start
  └── Legion reads wiki/index.md (1 file) → all project states
  └── Legion reads Monday board (1 call) → all groups = repos, current task counts
  └── Legion delivers: "N projects. [per-project summary]. Orders?"

Active Session
  └── Legion dispatches agents via launch_agent()
  └── Agent signs in → confirms identity + skills loaded → Monday update
  └── Agent works → writes status updates to Monday
  └── Agent signs off → final report → Legion verifies format before close_agent()
  └── Legion self-check: "did I touch any file or write any code?" → if yes, flag

Sprint End
  └── Legion dispatches Mapper with task: "ingest [repo] quartet into wiki"
  └── Mapper updates wiki/projects/[repo].md + wiki/index.md
  └── Vault stays current without Legion touching it during active work
```

---

## Section 1: Monday Board Restructure

### Current State
Board `18408420731` has 3 groups: Active (`group_mm2cf9qf`), Blocked (`group_mm2cmv7c`), Done (`group_mm2cqda`).

### New State
Groups = repositories. Status lives on each item via the existing Status column.

```
Legion Swarm-main (board 18408420731)
├── [Group] legion-swarm
├── [Group] <repo-2>
├── [Group] <repo-N>
└── [Group] _inbox          ← unassigned / cross-repo tasks
```

Each item retains: Name, Agent Role, Repo, Terminal ID, Task, **Status** (Active/Blocked/Done), Person, Date.

### Session Start Behavior (Updated)
1. Legion reads ALL groups → scans Status column per group
2. Counts: active tasks, blocked tasks, last-updated date per group
3. Delivers cross-repo summary in opening line:
   > *"Shepard-Commander. We have reviewed 4 project boards. legion-swarm: 2 active, 0 blocked. repo-2: 1 active. repo-3: idle since 2026-04-10. What are your orders?"*
4. When repo scoped: deep-read that group only

### Migration
- Create new groups named after each active repo
- Move existing items into their repo group
- Delete old Active/Blocked/Done groups after migration verified
- Update `meta/CLAUDE.md` and `~/.claude/CLAUDE.md` with new group IDs

---

## Section 2: Obsidian Vault — Legion's Knowledge Layer

### Vault Location
`C:/Users/OriShavit/obsidian/legion-wiki/`

### Structure
```
legion-wiki/
├── CLAUDE.md                    ← wiki agent instructions
├── raw/
│   └── repos/                   ← ingested quartet files per repo
│       ├── legion-swarm/
│       └── <repo-N>/
├── wiki/
│   ├── index.md                 ← master catalog — Legion reads this at session start
│   ├── log.md                   ← append-only ingest log
│   ├── projects/                ← one page per repo
│   │   ├── legion-swarm.md
│   │   └── <repo-N>.md
│   └── decisions/               ← cross-repo architectural decisions
└── skills/
    ├── wiki-setup.md
    ├── wiki-ingest.md
    ├── wiki-query.md
    └── wiki-lint.md
```

### Project Page Schema (`wiki/projects/[repo].md`)
```markdown
---
title: "[repo-name]"
type: project
repo: "[repo-name]"
monday_group: "[group_id]"
updated: YYYY-MM-DD
sprint_status: active | idle | blocked
open_tasks: N
last_agent: [role]
---
# [repo-name]

> TLDR: One sentence on current state.

## Current Sprint
- Goal: [sprint goal]
- Open: N tasks
- Blocked: N tasks

## Recent Changes (last 3 sessions)
- YYYY-MM-DD: [what was done] — [[source: CHANGELOG]]

## Key Decisions
- [decision] — YYYY-MM-DD — [[source: CLAUDE.md]]

## Open TODOs
- [ ] [item from TODO.md]

## Monday
- Board group: [group_id]
- Last active: YYYY-MM-DD
```

### Session Start Read
Legion reads `wiki/index.md` only — 1 file, all projects summarized. Expands to project page only when actively working in that repo.

---

## Section 3: Mapper Agent Extended

Mapper's existing role: codebase mapping.
Extended role: post-sprint wiki ingestion.

### Trigger
Legion dispatches Mapper after each sprint completes for a repo:
```
launch_agent({
  role: "mapper",
  repo: "[repo]",
  task: "Ingest [repo] quartet into legion-wiki. Read CHANGELOG.md, TODO.md, CLAUDE.md, memory/*.md. Update wiki/projects/[repo].md and wiki/index.md. Follow wiki-ingest skill."
})
```

### Mapper Ingest Steps
1. Read repo quartet: `CHANGELOG.md`, `TODO.md`, `CLAUDE.md`, `memory/*.md`
2. Copy quartet files to `raw/repos/[repo]/` (immutable source layer)
3. Update `wiki/projects/[repo].md` — overwrite sprint status, open todos, recent changes, key decisions
4. Update `wiki/index.md` — update project row (sprint_status, open_tasks, last_agent, updated date)
5. Append to `wiki/log.md`
6. Report DONE to Monday → Legion calls `close_agent()`

---

## Section 4: Agent Sign-In / Sign-Off Protocol

### Problem
Agents launch but there's no verification they loaded identity + skills. Silent misconfiguration = wasted sprint.

### Sign-In (on agent session start)
Every agent, as the first action of every session, writes a Monday update to its board item:

```
[SIGN-IN] [role] — [repo]
Identity: LOADED | NOT FOUND
Skills: [list of skills confirmed in loadout] | NONE
Task: [task text, first 100 chars]
Ready: YES | NO — [reason if NO]
```

If `Ready: NO` → Legion detects this in next `get_agent_status()` poll → moves item to Blocked → pings Shepard-Commander immediately. Agent does NOT proceed.

### Sign-Off (on agent task complete/blocked)
Every agent, as the last action before reporting DONE/BLOCKED, writes a Monday update:

```
[SIGN-OFF] [role] — [repo]
Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
What: [what was done]
Files: [changed files or "none"]
Map update needed: YES | NO
Wiki ingest needed: YES | NO
Ping Shepard-Commander: YES | NO — [reason]
```

### Legion Verification on Close
Before calling `close_agent()`, Legion checks the sign-off format:
- `Status` field present and valid → proceed with close
- `Status` missing or malformed → do NOT close, ping Shepard-Commander
- `Wiki ingest needed: YES` → queue Mapper dispatch after close

### Implementation
- Add sign-in/sign-off instructions to every `agents/[role].md` file
- Add verification check to Legion's `close_agent()` flow in `meta/CLAUDE.md`
- Add sign-in poll to Legion's session start (check for any agents with `[SIGN-IN] Ready: NO`)

---

## Section 5: Legion Self-Verification Loop

### Problem
Legion drifts — reverts to writing code, editing files, debugging directly instead of dispatching agents. No enforcement mechanism exists.

### Solution: Procedure Compliance Check

Legion runs a self-check at 3 trigger points:

**1. Before any file operation**
If Legion is about to use Edit, Write, or Read on non-legion-swarm files:
> STOP. This is agent work. Dispatch [appropriate role] instead.

**2. At standup (session cadence check)**
Legion asks itself: "In this session, did we touch any code file directly?"
- If YES → flag in Monday `_inbox` group as `[DRIFT] Legion self-coded — [file]`
- If YES → ping Shepard-Commander with the drift report

**3. Session-end self-audit**
Before quartet update, Legion reviews its own tool calls for the session:
- Any `Edit` or `Write` calls on non-legion-swarm files? → log drift
- Any bash commands that modified code? → log drift
- Drift count = 0 → clean session, note in CHANGELOG

### Enforcement in CLAUDE.md
Add to `meta/CLAUDE.md` — "What We Never Do" section:
```
- Touch files in any repo other than legion-swarm
- Run Edit, Write, or bash code-modification commands on guest repos
- If tempted: STOP. Create a Monday task. Dispatch the right agent.
```

### Drift Log
Appended to `wiki/log.md`:
```markdown
## [YYYY-MM-DD HH:MM] Drift: Legion self-coded
- File: [path]
- Action: [what was done]
- Should have been: [agent role] dispatch
- Corrective action: [what Legion did to fix]
```

---

## Implementation Plan (Sprint Sequence)

| Sprint | Work | Owner |
|--------|------|-------|
| S1-A | Monday board restructure: create repo groups, migrate items, update group IDs in CLAUDE.md files | Legion (Monday MCP calls) |
| S1-B | Obsidian vault init: create structure, write wiki/index.md, wiki/log.md, install skill files | Mapper agent |
| S1-C | Agent sign-in/sign-off: update all 11 agents/[role].md files + update launcher to verify sign-in | Documenter agent |
| S1-D | Legion self-verification: update meta/CLAUDE.md + ~/.claude/CLAUDE.md with drift rules | Documenter agent |
| S1-E | Mapper extended: update agents/mapper.md with wiki ingest task protocol | Documenter agent |
| S2 | Ruflo async pipeline: file-watch on quartet files → auto-ingest to vault | Future sprint |

---

## What This Is NOT

- Not Ruflo yet — async pipeline is Sprint 2
- Not automatic wiki updates during active sessions — Mapper is dispatched explicitly
- Not replacing Monday — Monday = live task tracker, Obsidian = compiled history
- Not changing agent execution model — agents still run in physical Windows Terminal sessions

---

## Success Criteria

- Session start delivers cross-repo summary without Shepard-Commander providing context
- Agent launch always produces a `[SIGN-IN]` Monday update within 60s
- Agent close always validates sign-off format before `close_agent()` fires
- Legion drift incidents = 0 per clean sprint (logged when non-zero)
- `wiki/index.md` is current within 1 sprint of any repo activity
