# Sprint 04 — Watchdog Subagent
> Legion Swarm | 2026-04-05 | Status: Ready

## Goal

Build a stateless watchdog subagent that every terminal session (Legion + all 11 agents) launches at startup. It polls `/context` and `/usage` independently, triggers saves and stops at defined thresholds, and propagates hard stops across all agent terminals via a shared sentinel file.

---

## Architecture Decisions

### How does the watchdog poll?

**PostToolUse hook, counting tool uses.** Not a timer (no reliable async sleep in Claude Code). After every N tool uses (default: 5), the watchdog runs `/context` and `/usage` and evaluates thresholds. N=5 is the balance between responsiveness and token overhead.

The watchdog is a subagent launched via `Task` at session start. It runs a tight `while true` loop where each iteration checks both signals and then idles for N parent tool uses by monitoring a shared counter file.

### How does the watchdog communicate back to the parent session?

Two channels, each purpose-built:

- **File write** — watchdog writes to `legion-swarm/.watchdog/status.json` after each poll. Parent session reads this on the PostToolUse hook to check for action flags.
- **Monday update** — for context ≥95% (graceful stop), watchdog writes a Monday update on the agent's board item flagging status as `Resuming` and reason as context limit.
- **Google Chat** — for usage ≥95% (hard stop), watchdog sends a Google Chat ping to Shepard-Commander via the Google Chat MCP.

### How does the 95% usage hard stop propagate to ALL terminals?

**Shared sentinel file.** When any watchdog detects usage ≥95%, it writes `legion-swarm/.watchdog/STOP` before stopping its own session. Every other terminal's PostToolUse hook checks for the existence of `STOP` at the start of each tool use. If found, that session runs `/quartet-update` and exits. The file is deleted only manually by Shepard-Commander (or at usage reset) to re-enable sessions.

This is a filesystem-level broadcast — no agent-to-agent direct communication, no Monday polling loop. Fast, simple, reliable.

---

## Tasks

### Task 1 — Watchdog directory and sentinel scaffold

**What to build:** Create `legion-swarm/skills/watchdog/` directory and `legion-swarm/.watchdog/` at repo root (gitignored). The `.watchdog/` directory holds runtime files: `status.json` (poll results) and `STOP` (hard-stop sentinel). Add `.watchdog/` to `.gitignore`.

**Files to create/modify:**
- `legion-swarm/.watchdog/.gitkeep` — placeholder so directory commits
- `legion-swarm/.gitignore` — add `.watchdog/STOP` and `.watchdog/status.json`
- `legion-swarm/skills/watchdog/` — directory created (empty until Task 2)

**Verify:** `.watchdog/` exists, `.gitignore` excludes runtime files, `skills/watchdog/` is present.

**Commit message:** `feat(watchdog): scaffold watchdog runtime dir and skill directory`

---

### Task 2 — `watchdog-prompt.md` — the subagent prompt template

**What to build:** The prompt injected into the watchdog subagent at launch. It defines the watchdog's identity, polling loop, threshold logic, and both communication channels. It is a template with one substitution: `{{AGENT_ROLE}}` — filled at launch time by the parent session.

**Design constraints:**
- Token-lean — watchdog runs in a subagent context with its own budget
- Stateless — no memory between iterations; all state is in files
- Self-terminating — watchdog stops itself cleanly at thresholds, never crashes

**Polling loop logic the prompt must encode:**
1. Increment tool-use counter in `status.json`
2. Every 5 tool uses: run `/context`, parse percentage, evaluate threshold
3. Every 5 tool uses: run `/usage`, parse percentage against budget cap, evaluate threshold
4. Context ≥80%: run `/quartet-update`, run `/compact`, reset counter, continue
5. Context ≥95%: run `/quartet-update`, write Monday update (status=Resuming, reason=context limit), stop session
6. Usage ≥95%: run `/quartet-update`, write `STOP` sentinel, ping Shepard-Commander on Google Chat, stop session
7. Write current poll results to `status.json` after each check

**Files to create:**
- `legion-swarm/skills/watchdog/watchdog-prompt.md`

**Verify:** Prompt covers both signals independently. Threshold actions match spec exactly. No threshold is silently swallowed. Sentinel write happens before session stop.

**Commit message:** `feat(watchdog): add watchdog subagent prompt template`

---

### Task 3 — `SKILL.md` — agent skill documentation

**What to build:** The skill file that teaches agents how to launch and interact with the watchdog. Every agent session loads this skill. It answers three questions: when to launch, how to launch, and what to do when the watchdog signals.

**Content the SKILL.md must cover:**
- Launch instruction: at session start, after reading the quartet and Monday task, launch watchdog via `Task` tool with `watchdog-prompt.md` content substituted with the agent's role
- Monitoring instruction: parent session's PostToolUse hook reads `status.json` and checks for `STOP` sentinel at each tool use
- Response to `STOP` sentinel: run `/quartet-update`, write Monday update (status=Paused, reason=system-wide usage limit), exit session — do not wait for watchdog signal again
- Response to context compact (≥80%): watchdog handles this autonomously — parent session just continues after `/compact`
- Response to graceful stop (context ≥95%): watchdog handles this autonomously — parent session is stopped by watchdog, Legion resumes on next session

**Files to create:**
- `legion-swarm/skills/watchdog/SKILL.md`

**Verify:** A new agent reading only this file knows exactly how to launch the watchdog, what the sentinel file means, and what its own responsibility is vs the watchdog's. No ambiguity on who does what.

**Commit message:** `feat(watchdog): add watchdog SKILL.md`

---

### Task 4 — Wire watchdog into agent session-start sequence

**What to build:** Update each agent identity file (`legion-swarm/agents/[role].md`) to include watchdog launch as step 5 of the Session Start sequence. Also update the Legion identity (`legion-swarm/meta/CLAUDE.md`) if it exists.

**Exact addition to Session Start in every agent file:**
> 5. Launch watchdog subagent (see `legion-swarm/skills/watchdog/SKILL.md`)

**Files to modify:**
- All 11 `legion-swarm/agents/*.md` files
- `legion-swarm/meta/CLAUDE.md` if present

**Verify:** Every agent file lists watchdog launch at step 5. No agent file is missing it. Legion identity file updated if it exists.

**Commit message:** `feat(watchdog): wire watchdog launch into all agent session-start sequences`

---

### Task 5 — PostToolUse hook for STOP sentinel detection

**What to build:** A PostToolUse hook configured in agent settings that reads the `STOP` sentinel file after each tool use and triggers graceful exit if found. This hook fires in the parent session — not the watchdog subagent — so it catches the hard stop broadcast from any terminal that hit 95% usage.

**Hook behavior:**
- After every tool use, check if `legion-swarm/.watchdog/STOP` exists
- If exists: run `/quartet-update`, write Monday update (status=Paused, reason=system-wide usage limit), stop session
- If not exists: continue normally

**Files to create/modify:**
- `legion-swarm/agents/settings/shared-hooks.json` — define the PostToolUse hook
- Update each `legion-swarm/agents/settings/[role]-settings.json` to include the shared hook (or reference it)

**Verify:** Hook definition is valid Claude Code settings format. Hook fires PostToolUse (not PreToolUse). All 11 agent settings files reference it. Legion settings updated if applicable.

**Commit message:** `feat(watchdog): add PostToolUse STOP sentinel hook to all agent settings`

---

## Done Criteria

- [ ] `.watchdog/` runtime dir exists and is gitignored correctly
- [ ] `watchdog-prompt.md` covers both signals, all four threshold actions, and sentinel write sequence
- [ ] `SKILL.md` gives a complete launch and response guide with zero ambiguity
- [ ] All 11 agent identity files include watchdog launch at Session Start step 5
- [ ] All 11 agent settings files include the PostToolUse STOP sentinel hook
- [ ] Hard stop propagates via filesystem sentinel — no direct agent communication required
- [ ] Watchdog is stateless — no database, no persistent subagent process between sessions

## Out of Scope

- Watchdog restart logic if subagent crashes (self-healing is a future sprint)
- Configurable polling interval per agent (N=5 is fixed for now)
- Usage reset detection (manual resume by Shepard-Commander)
- Cross-repo STOP propagation (per-repo `.watchdog/` dirs are independent)
