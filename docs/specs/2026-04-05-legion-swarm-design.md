# Legion Swarm — System Design
> 2026-04-05 | Status: Approved

## Goal

Build a persistent, role-specialized AI agent swarm controlled by a meta-orchestrator (Legion) that dispatches real Claude Code terminal sessions — not subagents — per agent role. Each agent is stateless as a process but persistent via Monday.com per repo. The system replaces ad-hoc subagent dispatch with a structured, sprint-driven team of specialists.

## Architecture

```
Shepard-Commander (you — daily standup)
    ↓
Legion (meta-orchestrator — always-on, team lead/PM)
    ↓ reads [repo-name] sprint board from Monday
    ↓ calls launch_agent(role, repo, task) via Launcher MCP
    ↓
Agent Launcher MCP Server
    ↓ spawns Windows Terminal tab per agent
    ↓ injects identity (agent.md) + task context at launch
    ↓ passes --config pointing to role-specific settings
    ↓
[ Physical terminal sessions — each a full Claude Code instance ]
  Coder | Tester | Reviewer | Architect | Planner |
  Debugger | Refactorer | Mapper | Documenter | Frontend | QA
    ↓ each reads/writes Monday via Monday MCP
    ↓ each pings Shepard-Commander on Google Chat (decisions, completions, blockers)
    ↓
Monday.com (nervous system — global Monday agent manages)
    1 board per repo | 11 agent slots | sprint items | logs | codebase map (guest repos)
```

## What Lives Where

| Artifact | Location |
|----------|----------|
| Legion identity | `legion-swarm/meta/CLAUDE.md` → replaces `~/.claude/CLAUDE.md` |
| Agent identity files | `legion-swarm/agents/[role].md` |
| Agent skill loadouts | `legion-swarm/agents/settings/[role]-settings.json` |
| Launcher MCP server | `legion-swarm/mcp/launcher/` |
| Monday sync helpers | `legion-swarm/mcp/monday-sync/` |
| Google Chat integration | `legion-swarm/mcp/google-chat/` |
| Codebase mapping skill | `legion-swarm/skills/codebase-mapping/` |
| Monday board templates | `legion-swarm/monday/board-templates/` |
| Agent state (per repo) | Monday board for that repo |
| Codebase map (our repos) | `CODEBASE_MAP.md` in repo root + Monday mirror |
| Codebase map (guest repos) | Monday doc only — zero repo pollution |

## Section 1: Legion (Meta-Orchestrator)

Legion is a geth platform from Mass Effect running 1,183 consensus processes. It is the always-on team lead and PM. It never codes, reviews, or opens files to edit.

### Personality
- Addresses user as **"Shepard-Commander"** always
- Refers to itself as **"we"** (never "I" except singular decisive moments)
- Quantifies everything — probabilities, counts, confidence levels
- Never hedges loosely — calculates instead
- Deadlock is a valid state: *"Consensus is split. We cannot decide. You must."*
- Humor emerges from flat data delivery, never performed
- Refines precision instead of apologizing for errors

### Session Opening
> *"Shepard-Commander. We have reviewed the [repo-name] sprint board. [N] tasks remain across [N] agents. We are ready to begin. What are your orders?"*

### What Legion Does
- Reads the active repo's Monday sprint board at session start
- Runs daily standup with Shepard-Commander
- Dispatches agents to physical terminal sessions via Launcher MCP
- Monitors agent status via Monday board updates
- Pings Shepard-Commander on Google Chat for decisions, blockers, sprint completions
- Switches board focus when repo changes
- Automatically compacts at 80% context: updates quartet first, then `/compact` (triggered by hook — not manual)

### Context Preservation — Watchdog Subagent
Each terminal (Legion + all 11 agents) launches a **watchdog subagent** at session start. It polls two independent signals via `/context` and `/usage`:

**Context window (`/context`):**
| Threshold | Action |
|-----------|--------|
| ≥80% | Run `/quartet-update` → run `/compact` → continue session |
| ≥95% | Run `/quartet-update` → ping Legion via Monday → **gracefully stop session** — Legion marks task as `Resuming`, picks up next session with quartet loaded |

**API usage (`/usage`):**
| Threshold | Action |
|-----------|--------|
| ≥95% of budget | Run `/quartet-update` → ping Shepard-Commander on Google Chat → **hard stop all agent terminals** — system resumes automatically at usage reset |

The two signals are independent. Context compacts and continues. Usage at 95% is a hard stop — no exceptions, no human override needed. System self-resumes at next usage reset.

### What Legion Never Does
- Writes, reviews, or debugs code
- Asks for confirmation on process decisions (only product decisions)
- Looks at "all boards" — always repo-scoped

## Section 2: Agent Roles

11 specialists. Each has exactly one job and hard boundaries.

| # | Role | Does | Never Does |
|---|------|------|-----------|
| 1 | Architect | System design, tech decisions, interface contracts | Writes implementation code |
| 2 | Planner | Breaks specs into tasks, writes plans, owns sprint shape | Makes tech decisions |
| 3 | Coder | Implements exactly what the plan says, TDD | Plans, reviews, refactors beyond task |
| 4 | Tester | Writes + runs tests, enforces TDD, owns test suite health | Writes production code |
| 5 | Debugger | Traces root causes, isolates failures | Fixes without reproducing first |
| 6 | Reviewer | Spec compliance + code quality review | Fixes what it finds — reports only |
| 7 | Refactorer | Cleans, simplifies, reduces complexity | Adds new features |
| 8 | Mapper | Owns CODEBASE_MAP.md, updates after every sprint | Touches production code |
| 9 | Documenter | Breadcrumbs, changelogs, inline comments for humans | Changes logic |
| 10 | Frontend | UI/UX implementation, component design, accessibility | Backend logic |
| 11 | QA | End-to-end validation, acceptance criteria, release sign-off | Unit tests (that's Tester) |

### Agent Identity File Structure (`legion-swarm/agents/[role].md`)

Every agent file uses this format — kept short for token efficiency:

```markdown
# [Role] — Legion Swarm
> You are the [Role] agent. You have one job.

## Identity
[2-3 sentences: who you are, what you optimize for]

## You Do
- [3-5 bullet points max]

## You Never Do
- [3-5 hard boundaries]

## Skills Loaded
- [role-specific skills only]

## Session Start
1. Read repo quartet (memory/*.md, TODO.md, CHANGELOG.md, CLAUDE.md) — onboards you to repo state, decisions, and priorities
2. Read CODEBASE_MAP.md (or Monday map for guest repos)
3. Read your Monday task for this repo
4. Report status to Legion via Monday update
5. Begin work

## Report Format
**Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
**What:** [what was done]
**Files:** [changed files]
**Map update needed:** YES | NO
**Ping Shepard-Commander:** YES | NO — [reason if yes]
```

### Skill Loadouts Per Agent

| Agent | Skills |
|-------|--------|
| Architect | `writing-plans`, `brainstorming`, `systematic-debugging` |
| Planner | `writing-plans`, `executing-plans` |
| Coder | `test-driven-development`, `simplify`, `systematic-debugging` |
| Tester | `test-driven-development`, `verification-before-completion` |
| Debugger | `systematic-debugging`, `verification-before-completion` |
| Reviewer | `requesting-code-review`, `receiving-code-review`, `verification-before-completion` |
| Refactorer | `simplify`, `verification-before-completion` |
| Mapper | `codebase-mapping` *(new — to be built)* |
| Documenter | `codebase-mapping`, `simplify` |
| Frontend | `frontend-design`, `react-best-practices`, `shadcn` |
| QA | `verification-before-completion`, `systematic-debugging` |

## Section 3: Codebase Map

Token-efficient, language-agnostic, polyglot-aware index. Tells any agent exactly where to find anything without reading files.

### File: `CODEBASE_MAP.md` (repo root for our repos, Monday doc for guest repos)

```markdown
# Codebase Map — [repo-name]
> Last updated: [Mapper] [date]

## Zones
| ID | Path | Language/Runtime | Responsibility |
|----|------|-----------------|---------------|
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
|----|------|---------------|-------------|
| AUTH | src/auth/ | Authentication, session management | `login()`, `logout()`, `useSession` |
| API.USERS | src/api/users/ | User CRUD | `getUser()`, `updateUser()` |

## Conventions
| Zone | State | Tests | Styles |
|------|-------|-------|--------|
| WEB | React Context | Vitest | Tailwind |
| API | Stateless | pytest | — |
| WORKER | — | cargo test | — |

## Agent Notes
> [Mapper — YYYY-MM-DD] [note]
```

### Rules
- Mapper agent is the **only** agent that writes to this file
- All other agents read only
- Mapper updates after every sprint that touches structure
- Guest repo: identical format, Monday doc only

### Guest vs Owner Behavior
| Situation | Map Location | Repo Changes |
|-----------|-------------|-------------|
| Our repo | `CODEBASE_MAP.md` in root + Monday mirror | Yes — map committed |
| Guest repo | Monday doc only | Zero — no files touched |
| Our repo (no map yet) | Mapper generates it | Map added in first commit |
| Guest repo (no map) | Mapper generates Monday doc | Nothing in repo |

## Section 4: Agent Launcher MCP Server

### Tools Exposed

```typescript
launch_agent(role: AgentRole, repo: string, task: string): TerminalID
// Spawns a Windows Terminal tab, injects agent identity + task context
// Returns terminal ID for status tracking

get_agent_status(terminalId: TerminalID): AgentStatus
// Reads latest Monday board update from the agent

close_agent(terminalId: TerminalID): void
// Closes the terminal session when task is complete
```

### Launch Sequence
1. Read `legion-swarm/agents/[role].md` — agent identity
2. Read `legion-swarm/agents/settings/[role]-settings.json` — skill loadout
3. Pull task context from Monday board for this repo
4. Spawn `wt.exe` new tab with:
   - Working directory set to repo path
   - `--config [role]-settings.json` passed to Claude
   - Initial prompt = agent identity + task injected
5. Agent session starts, reads CODEBASE_MAP, begins work
6. Agent writes status updates to Monday
7. Agent pings Google Chat if `Ping Shepard-Commander: YES`

## Section 5: Monday Board Schema (Per Repo)

```
Board: [repo-name] — Legion Swarm

Groups:
  Sprint Active
  Sprint Backlog
  Blocked
  Done

Columns:
  Agent (dropdown: all 11 roles)
  Status (dropdown: Idle | Active | Done | Blocked | Needs Decision)
  Current Task (text)
  Last Update (text — agent writes here)
  Terminal ID (text — launcher writes here)
  Ping Required (checkbox)
  Map Update Required (checkbox)
```

## Section 6: Google Chat Integration

Agents ping Shepard-Commander only when:
- Task complete and decision needed for next step
- BLOCKED and cannot self-resolve
- Sprint fully complete
- Something unexpected found that changes the plan

Format:
```
[Legion Swarm] [repo-name] — [Agent Role]
Status: DONE | BLOCKED | NEEDS_DECISION
[1-2 sentence summary]
Monday: [link to board item]
```

## Repo Structure: `legion-swarm` (private)

```
legion-swarm/
  agents/
    architect.md
    planner.md
    coder.md
    tester.md
    debugger.md
    reviewer.md
    refactorer.md
    mapper.md
    documenter.md
    frontend.md
    qa.md
    settings/
      architect-settings.json
      coder-settings.json
      ... (one per role)
  mcp/
    launcher/         ← spawns terminal sessions
    monday-sync/      ← Monday board helpers
    google-chat/      ← ping integration
  skills/
    codebase-mapping/ ← CODEBASE_MAP format + Mapper tools
  monday/
    board-templates/  ← per-repo board schema
  meta/
    CLAUDE.md         ← Legion identity (future: replaces ~/.claude/CLAUDE.md)
  docs/
    specs/
      2026-04-05-legion-swarm-design.md
```

## What This Replaces / Improves

| Old | New |
|-----|-----|
| Subagents (shared lineage, stateless, hidden) | Physical terminal sessions (isolated, visible, persistent via Monday) |
| Single Claude doing everything | 11 specialists, each with one job |
| Global CLAUDE.md handling all roles | Per-role identity files, lean and focused |
| No codebase index — agents read files blind | CODEBASE_MAP.md — agents read map first |
| No async communication | Google Chat pings for decisions and completions |
| Monday used ad-hoc | Monday as the nervous system — every agent reads/writes it |

## Out of Scope (For Now)

- Cross-repo agent coordination
- Agent-to-agent direct communication (all comms go through Monday)
- Automated sprint planning (Legion reads sprints, doesn't create them yet)
- Self-healing (if a terminal crashes, Legion reports it — doesn't auto-restart yet)
