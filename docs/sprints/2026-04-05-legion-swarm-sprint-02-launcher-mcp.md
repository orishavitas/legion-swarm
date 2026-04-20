# Sprint 02 — Launcher MCP Server

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans

**Goal:** Build the Launcher MCP Server — the component Legion calls to spawn, monitor, and close physical Windows Terminal agent sessions.

**Spec:** `docs/specs/2026-04-05-legion-swarm-design.md` Section 4
**Builds on:** Sprint 01 output — `agents/[role].md` files and `agents/settings/[role]-settings.json` stubs must exist

---

### Task 1: Finalize settings JSON schema

The Sprint 01 stubs have `{ "role": "...", "skills": [...] }`. The Launcher reads these at launch time to construct the `claude --config` command and inject skill-aware context. Finalize the full schema all 11 stubs must conform to.

**Schema fields:**
- `role` (string) — matches the filename and the agent identity file name
- `skills` (string[]) — skill names from the spec loadout table
- `model` (string) — Claude model ID to use for this role
- `workingDirectoryStrategy` (enum: `"repo"` | `"swarm-root"`) — where to `cd` before spawning; most roles use `"repo"`, Mapper may use `"swarm-root"`
- `contextBudget` (number) — max context tokens before watchdog fires compact; role-specific (Coder: high, Reviewer: medium, Documenter: low)
- `allowedTools` (string[]) — explicit MCP tool allowlist for this role (e.g., Coder gets `bash`, `edit`, `read`; Reviewer gets `read` only)
- `env` (Record<string, string>) — optional extra env vars injected at launch (empty object `{}` for most roles)

**Files to modify:** all 11 `agents/settings/[role]-settings.json` — replace stubs with full schema

**Verify:** `npx ajv validate` or equivalent confirms all 11 files parse against the schema; each file has all 7 fields populated with role-appropriate values

**Commit:** `feat: finalize agent settings schema with model, tools, and context budget`

---

### Task 2: Scaffold the Launcher MCP package

Initialize the Node.js/TypeScript MCP server project at `mcp/launcher/`.

**Files to create:**
- `mcp/launcher/package.json` — name `@legion-swarm/launcher-mcp`, dependencies: `@modelcontextprotocol/sdk`, `zod`; devDependencies: `typescript`, `tsx`, `@types/node`
- `mcp/launcher/tsconfig.json` — `"module": "NodeNext"`, `"moduleResolution": "NodeNext"`, `"outDir": "dist"`, `"strict": true`
- `mcp/launcher/src/index.ts` — entry point: creates MCP server, registers the 3 tools (stubs returning `not implemented`), starts stdio transport
- `mcp/launcher/src/types.ts` — defines `AgentRole` union type (all 11 roles), `TerminalID` (branded string), `AgentStatus` type, `AgentSettingsSchema` (Zod schema matching the finalized JSON from Task 1)
- `mcp/launcher/src/registry.ts` — in-memory map of `TerminalID → { role, repo, pid, spawnedAt }` — source of truth for all live sessions

**Verify:** `npm install && npx tsx src/index.ts` starts without error; MCP server responds to `tools/list` with 3 tool entries

**Commit:** `feat: scaffold launcher MCP server with tool stubs and type definitions`

---

### Task 3: Implement `launch_agent`

The core tool. Reads identity + settings, pulls task context, spawns the terminal, registers the session.

**Files to modify:** `mcp/launcher/src/tools/launch-agent.ts` (new file), `mcp/launcher/src/index.ts` (wire up)

**Implementation steps the agent must handle:**
1. Validate inputs against `AgentRole` union and non-empty `repo` and `task` strings
2. Resolve `LEGION_SWARM_ROOT` env var — absolute path to the `legion-swarm/` repo; throw if unset
3. Read `{LEGION_SWARM_ROOT}/agents/{role}.md` — agent identity text
4. Read and validate `{LEGION_SWARM_ROOT}/agents/settings/{role}-settings.json` against `AgentSettingsSchema`
5. Resolve repo path: `LEGION_SWARM_REPOS_ROOT/{repo}` (env var) or fall back to cwd
6. Determine working directory from `workingDirectoryStrategy`
7. Construct the initial prompt string: agent identity file contents + `\n\n## Your Task\n` + task argument
8. Write the prompt to a temp file (`os.tmpdir()/{terminalId}-prompt.txt`) — passed as `--print` flag to avoid shell escaping the full prompt inline
9. Build `wt.exe` command: `wt new-tab --title "{role}" --startingDirectory "{workingDir}" cmd /c claude --model {model} --config "{settingsPath}" --print "{promptFile}"`
10. Spawn via `child_process.spawn` with `detached: true`, `stdio: 'ignore'`; call `unref()` so Launcher doesn't block
11. Generate `TerminalID` as `{role}-{Date.now()}`; register in `registry.ts`; write `Terminal ID` to Monday board item for this repo+role via Monday MCP (fire-and-forget, don't block launch on it)
12. Return `{ terminalId, role, repo, spawnedAt }`

**Verify:** calling `launch_agent("coder", "my-repo", "implement the login form")` spawns a visible Windows Terminal tab with Claude Code starting; `registry.ts` contains the entry

**Commit:** `feat: implement launch_agent — spawns Windows Terminal Claude Code session per role`

---

### Task 4: Implement `get_agent_status`

Reads the latest Monday board update for the agent session identified by `terminalId`.

**Files to create:** `mcp/launcher/src/tools/get-agent-status.ts`

**Implementation steps:**
1. Look up `terminalId` in registry — return `{ status: "not_found" }` if missing
2. Use Monday MCP (`mcp__claude_ai_monday_com__get_updates`) to fetch the latest update on the board item where `Terminal ID` column matches `terminalId`
3. Parse the update text for the standard report format: `Status:`, `What:`, `Files:`, `Map update needed:`, `Ping Shepard-Commander:`
4. Return structured `AgentStatus`: `{ terminalId, role, repo, lastStatus, lastWhat, pingRequired, mapUpdateRequired, lastUpdatedAt }`
5. If no Monday update exists yet, return `{ terminalId, role, repo, lastStatus: "pending", lastUpdatedAt: null }`

**Verify:** after a launched agent writes its first Monday status update, `get_agent_status` returns the parsed fields correctly

**Commit:** `feat: implement get_agent_status — reads agent report from Monday board`

---

### Task 5: Implement `close_agent`

Closes a terminal session and cleans up registry and temp files.

**Files to create:** `mcp/launcher/src/tools/close-agent.ts`

**Implementation steps:**
1. Look up `terminalId` in registry — return `{ closed: false, reason: "not_found" }` if missing
2. Send WM_CLOSE to the process via `taskkill /PID {pid} /T` using `child_process.execSync` — graceful first, force only if exit code non-zero
3. Delete the temp prompt file `os.tmpdir()/{terminalId}-prompt.txt` if it exists
4. Remove entry from registry
5. Return `{ closed: true, terminalId, role, repo }`

**Verify:** after calling `close_agent`, the Windows Terminal tab disappears and the registry no longer contains the entry

**Commit:** `feat: implement close_agent — terminates session and cleans up registry`

---

### Task 6: Error handling, env validation, and MCP registration

Harden the server before it goes live.

**Files to modify:** `mcp/launcher/src/index.ts`, `mcp/launcher/src/env.ts` (new)

**What to build:**
- `env.ts`: validate required env vars at startup (`LEGION_SWARM_ROOT`, `LEGION_SWARM_REPOS_ROOT`); throw with a clear message if missing — fail fast, not at tool call time
- Wrap all three tool handlers in try/catch; return MCP error responses with structured `code` + `message` (never throw unhandled)
- Add Zod input schemas for all 3 tools wired into the MCP `inputSchema` field — Legion gets type-safe tool calls
- Add `mcp/launcher/README.md` listing: required env vars, how to register the server in Claude Code settings, example tool calls

**Verify:** starting the server without env vars prints a clear error and exits with code 1; calling a tool with wrong input type returns an MCP error (not a crash)

**Commit:** `feat: add env validation, error handling, and input schemas to launcher MCP`

---

### Task 7: Register Launcher MCP in legion-swarm CLAUDE.md

Legion needs to call Launcher MCP tools. Wire it in.

**Files to modify:** `meta/CLAUDE.md`

**What to add:**
- MCP server registration block: name `launcher`, command `node`, args pointing to `mcp/launcher/dist/index.js`, required env vars listed
- Section: "Dispatching Agents" — when Legion calls `launch_agent`, what args it passes, what it does with the returned `terminalId`
- Section: "Monitoring Agents" — polling pattern: Legion calls `get_agent_status` on active sessions during standup; if `pingRequired: true`, it surfaces the message to Shepard-Commander
- Section: "Closing Agents" — when task status is `DONE` or `BLOCKED` (unresolvable), Legion calls `close_agent`

**Verify:** `meta/CLAUDE.md` clearly documents the full Legion dispatch loop referencing Launcher MCP tool names

**Commit:** `docs: wire Launcher MCP into Legion identity — dispatch, monitor, close loop`

---

### Task 8: Push, smoke test end-to-end

Final integration check before sprint close.

**Steps:**
1. `npm run build` in `mcp/launcher/` — confirm zero TypeScript errors
2. Set env vars, start server: `LEGION_SWARM_ROOT=/path/to/legion-swarm LEGION_SWARM_REPOS_ROOT=/path/to/repos npx tsx src/index.ts`
3. Call `launch_agent("coder", "legion-swarm", "read CODEBASE_MAP.md and report back")` via MCP inspector or Claude Code
4. Confirm Windows Terminal tab opens with Claude Code session
5. Wait for agent to write Monday update, call `get_agent_status` — confirm parsed response
6. Call `close_agent` — confirm tab closes
7. Push all commits to GitHub

**Verify:** all 3 tool calls work in sequence against a real Windows Terminal session; zero TypeScript errors in build

**Commit:** `chore: push sprint 02 — launcher MCP complete`
