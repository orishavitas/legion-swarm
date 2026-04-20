# Sprint 01 — Repo Scaffold + Agent Identities

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans

**Goal:** Create the `legion-swarm` private repo with Legion identity + 11 agent identity files + per-role skill loadout settings.

**Spec:** `docs/specs/2026-04-05-legion-swarm-design.md`

---

### Task 1: Init repo + directory structure
- Create `legion-swarm/` with subdirs: `agents/settings/`, `meta/`, `docs/specs/`, `docs/plans/`, `mcp/`, `skills/`, `monday/`
- Add `.gitignore` (node_modules, .env, *.log, dist/)
- Add `README.md` (name, purpose, structure overview)
- Copy design spec into `docs/specs/`
- `git init` + initial commit
- `gh repo create legion-swarm --private` + push
- **Verify:** repo visible at github.com/[username]/legion-swarm

### Task 2: Legion identity (meta/CLAUDE.md)
- Write Legion's identity: personality, address style ("Shepard-Commander", "we"), session start sequence (quartet read → Monday board → opening line), dispatch rules, agent status handling, context/usage watchdog thresholds
- This is a **project-level CLAUDE.md** — it augments `~/.claude/CLAUDE.md` (global), does not replace it. It activates when inside the `legion-swarm` repo.
- Full spec in: `docs/specs/2026-04-05-legion-swarm-design.md` Section 1
- Commit: `feat: add Legion meta-orchestrator identity`
- **Verify:** file exists, contains all sections from spec

### Task 3: 11 agent identity files (agents/)
- One file per role: architect, planner, coder, tester, debugger, reviewer, refactorer, mapper, documenter, frontend, qa
- Each file: Identity (2-3 sentences) | You Do (3-5 bullets) | You Never Do (3-5 bullets) | Skills Loaded | Session Start (5 steps — quartet first) | Report Format
- Session Start step 1 is always: read repo quartet (memory/*.md, TODO.md, CHANGELOG.md, CLAUDE.md)
- Full role definitions in spec Section 2
- Commit: `feat: add all 11 agent identity files`
- **Verify:** 11 files exist, all have identical Session Start structure

### Task 4: Per-role settings stubs (agents/settings/)
- One JSON stub per role listing skills only — schema will be finalized in Sprint 02 (Launcher MCP)
- Format: `{ "role": "[role]", "skills": ["skill-a", "skill-b"] }` — intentionally minimal
- Loadouts per spec Section 2 skill table
- Commit: `feat: add per-role skill loadout stubs`
- Push to GitHub
- **Verify:** 11 JSON files exist, pushed to remote
