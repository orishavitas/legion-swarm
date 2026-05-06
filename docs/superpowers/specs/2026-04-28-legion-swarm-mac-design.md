# legion-swarm-mac — Design Spec
> 2026-04-28 | Status: Approved

## Goal

Port the Legion Swarm system to macOS as a new repository (`legion-swarm-mac`). Replace
Windows Terminal (`wt.exe`) agent spawning with tmux-based session management. Preserve
all platform-neutral components: 11 agent identities, Monday integration, Google Chat,
sign-in/sign-off protocol, watchdog, and sprint tooling.

---

## Problem Statement

`legion-swarm` was built for Windows Terminal on a Windows machine. Three hard blockers
on Mac:

1. `launch-agent.ts` calls `spawn("wt.exe", ...)` — not available on macOS.
2. `meta/CLAUDE.md` and `.mcp.json` contain Windows absolute paths
   (`C:\Users\OriShavit\...`).
3. Obsidian vault path is hardcoded as a Windows path.

Everything else (agent identities, MCP servers, Monday schema, sprint docs, sign-off
protocol) is platform-neutral and carries over unchanged.

---

## Architecture

```
Shepard-Commander
    ↓ opens Claude Code in tmux window 0 (legion)
Legion (meta-orchestrator — meta/CLAUDE.md identity)
    ↓ reads Obsidian wiki/index.md → cross-repo state
    ↓ reads Monday board → all groups = repos, task counts
    ↓ calls launch_agent(role, repo, task) via Launcher MCP
    ↓
Launcher MCP (mcp/launcher/ — Node.js/TypeScript)
    ↓ ensures tmux session "legion" exists (idempotent)
    ↓ opens new-window named <terminalId>
    ↓ runs: claude --model <model> --print <promptFile>
    ↓
tmux session: legion
  window 0: legion          ← Legion session (Shepard-Commander's terminal)
  window N: coder-<id>      ← spawned agent, auto-named by terminalId
  window N: tester-<id>
  window N: reviewer-<id>
  ...
    ↓ each agent writes status updates to Monday via Monday MCP
    ↓ Google Chat pings on decisions / blockers / sprint complete
    ↓
Monday.com board 18408420731
    groups = repositories | Status column per item
    ↑ Legion reads for standup / monitoring
    ↑ Agents write sign-in / sign-off / progress updates
```

---

## Section 1: Launcher MCP — Mac Dispatch

### Current (Windows)
```typescript
spawn("wt.exe", ["new-tab", "--title", role, "--startingDirectory", workingDir,
                 "cmd", "/k", "claude", "--model", model, "--print", promptFile])
```

### New (Mac/tmux)
```typescript
// Step 1 — ensure session exists (noop if already running)
spawnSync("tmux", ["new-session", "-d", "-s", "legion"], { stdio: "ignore" });

// Step 2 — open agent window
spawn("tmux", [
  "new-window",
  "-t", "legion",
  "-n", terminalId,
  "-c", workingDir,
  `claude --model ${settings.model} --print ${promptFile}`
], { detached: true, stdio: "ignore" });
```

**terminalId format**: `<role>-<8-char-hex>` — e.g. `coder-a3f9b12e`
**Window name = terminalId**: makes `tmux kill-window -t legion:<terminalId>` precise.

### close_agent addition
```typescript
spawnSync("tmux", ["kill-window", "-t", `legion:${terminalId}`], { stdio: "ignore" });
```
Called after sign-off verification (existing logic unchanged).

### get_agent_status bonus
Optionally capture raw pane output for debugging:
```typescript
const paneOutput = spawnSync("tmux", [
  "capture-pane", "-t", `legion:${terminalId}`, "-p"
], { encoding: "utf8" }).stdout;
```
Not used in normal flow — available for diagnostics.

---

## Section 2: Path Strategy — Zero Hardcoded Paths

All paths are injected via environment variables. `.env` is never committed.

### Required env vars
| Variable | Purpose | Example |
|----------|---------|---------|
| `LEGION_SWARM_ROOT` | Absolute path to this repo | `/Users/rdhome/Documents/GitHub/legion-swarm-mac` |
| `LEGION_SWARM_REPOS_ROOT` | Parent directory of all guest repos | `/Users/rdhome/Documents/GitHub` |
| `OBSIDIAN_VAULT` | Absolute path to Obsidian vault root | `/Users/rdhome/obsidian/legion-wiki` |
| `MONDAY_API_KEY` | Monday.com API token | (secret) |
| `GOOGLE_CHAT_WEBHOOK_URL` | Google Chat webhook for Legion pings | (secret) |

### `.env.example` (committed)
```
LEGION_SWARM_ROOT=/path/to/legion-swarm-mac
LEGION_SWARM_REPOS_ROOT=/path/to/github
OBSIDIAN_VAULT=/path/to/obsidian/legion-wiki
MONDAY_API_KEY=
GOOGLE_CHAT_WEBHOOK_URL=
```

### meta/CLAUDE.md session-start
Replace hardcoded Windows vault path with env-relative reference:
```
Read $OBSIDIAN_VAULT/wiki/index.md — cross-repo project state
```
Claude Code resolves env vars from the shell session.

---

## Section 3: Monday Hook Verification

A smoke-test script runs before the first Legion session to confirm the Monday
connection is live.

### `scripts/verify-monday.ts`
1. Reads `MONDAY_API_KEY` from env (fails fast if missing)
2. Calls Monday GraphQL: `boards(ids: [18408420731]) { name groups { id title } }`
3. Prints group names and IDs — operator confirms they match `meta/CLAUDE.md` table
4. Exits 0 on success, 1 on auth/network error

Run: `npm run verify-monday` (added to `package.json` root scripts).

---

## Section 4: Bootstrap Script

### `scripts/bootstrap-session.sh`
```bash
#!/usr/bin/env bash
# Creates the legion tmux session and opens Legion in window 0.
# Run once per work session. Safe to re-run (checks for existing session).
SESSION="legion"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "Session '$SESSION' already running. Attaching..."
  tmux attach-session -t "$SESSION"
  exit 0
fi

tmux new-session -d -s "$SESSION" -n "legion" -c "$REPO_ROOT"
tmux send-keys -t "$SESSION:legion" "claude --model claude-opus-4-7" Enter
tmux attach-session -t "$SESSION"
```

---

## Section 5: What Is Preserved Unchanged

| Component | Status |
|-----------|--------|
| 11 agent identity files (`agents/*.md`) | Copied verbatim |
| Agent settings / skill loadouts (`agents/settings/`) | Copied verbatim |
| Monday MCP server (`mcp/monday-sync/`) | Copied verbatim |
| Google Chat MCP server (`mcp/google-chat/`) | Copied verbatim |
| Legion identity (`meta/CLAUDE.md`) | Copied, vault path line updated |
| Sign-in / sign-off protocol | Unchanged |
| Watchdog thresholds (80% compact, 95% stop) | Unchanged |
| Sprint docs (`docs/sprints/`) | Copied verbatim |
| Monday board ID + group IDs + column IDs | Unchanged |
| MCP tool API (`launch_agent`, `get_agent_status`, `close_agent`) | Unchanged |

---

## Section 6: New Repository Structure

```
legion-swarm-mac/
├── .env.example
├── .gitignore              ← includes .env, node_modules, dist
├── .mcp.json               ← env-relative paths (no absolutes)
├── README.md
├── agents/                 ← 11 identity files + settings (copied)
├── docs/
│   ├── obsidian/
│   ├── specs/
│   │   └── 2026-04-28-legion-swarm-mac-design.md
│   ├── sprints/            ← all sprint docs (copied)
│   └── superpowers/
├── meta/
│   └── CLAUDE.md           ← Legion identity (vault path updated)
├── mcp/
│   ├── launcher/           ← TypeScript, wt.exe → tmux
│   ├── google-chat/        ← copied verbatim
│   └── monday-sync/        ← copied verbatim
├── monday/                 ← board templates (copied)
├── scripts/
│   ├── bootstrap-session.sh
│   └── verify-monday.ts
└── skills/                 ← codebase-mapping skill (copied)
```

---

## Section 7: Out of Scope

- Cross-machine sync (this repo is Mac-only)
- Gemma node (sprint 07 — separate effort)
- UI or dashboard for agent monitoring
- Automatic Obsidian write-back (still manual / Mapper-dispatched)

---

## Risks

| Risk | Mitigation |
|------|-----------|
| tmux not installed | `bootstrap-session.sh` checks and prints install instructions (`brew install tmux`) |
| `claude` CLI not on PATH inside tmux | Bootstrap sources `.zshrc`/`.zprofile`; README documents this |
| Monday board restructure invalidates group IDs | `verify-monday.ts` prints current IDs for confirmation before first session |
| Agent windows pile up if close_agent not called | `tmux kill-session -t legion` as nuclear reset; documented in README |
