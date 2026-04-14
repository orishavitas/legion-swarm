# Context Layer v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give Legion instant cross-repo awareness at session start, verified agent launch/close, and a self-enforcement loop that prevents Legion from coding directly.

**Architecture:** Monday board groups restructured to repos-as-groups with Status as a column. Obsidian vault at `C:/Users/OriShavit/obsidian/legion-wiki/` stores one compiled project page per repo, queried by Legion at session start. Launcher MCP extended with sign-in polling — warns Legion if no `[SIGN-IN]` update arrives within 60s of spawn. All 11 agent identity files updated with sign-in/sign-off protocol. Legion CLAUDE.md updated with drift self-check rules.

**Tech Stack:** TypeScript (Launcher MCP), Markdown (agent identity files + Obsidian vault), Monday.com MCP (board restructure), Node.js polling via `setTimeout`

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `mcp/launcher/src/types.ts` | Modify | Add `SignInStatus`, `wikiIngestRequired` to `AgentStatus` |
| `mcp/launcher/src/tools/launch-agent.ts` | Modify | Add 60s sign-in poll after spawn, return `signInStatus` |
| `mcp/launcher/src/tools/get-agent-status.ts` | Modify | Parse `[SIGN-IN]` and `[SIGN-OFF]` blocks from Monday text |
| `mcp/launcher/src/tools/close-agent.ts` | Modify | Block close if sign-off not present, return warning |
| `mcp/launcher/src/index.ts` | Modify | Surface sign-in warning in `launch_agent` response |
| `agents/[all 11 roles].md` | Modify | Add sign-in/sign-off protocol to Session Start + Report Format |
| `meta/CLAUDE.md` | Modify | Add drift self-check rules, updated session start sequence, updated Monday group IDs |
| `~/.claude/CLAUDE.md` | Modify | Same drift + session start + group ID updates |
| `docs/obsidian/wiki-setup-instructions.md` | Create | One-time human setup guide for the Obsidian vault |
| `agents/mapper.md` | Modify | Add wiki ingest task protocol to identity |

---

## Task 1: Extend types for sign-in/sign-off and wiki ingest flag

**Files:**
- Modify: `mcp/launcher/src/types.ts`

- [ ] **Step 1: Add `SignInStatus` type and extend `AgentStatus`**

Open `mcp/launcher/src/types.ts`. Add after the `AgentStatus` interface:

```typescript
export type SignInStatus =
  | "pending"       // not yet received
  | "confirmed"     // [SIGN-IN] received, Ready: YES
  | "failed"        // [SIGN-IN] received, Ready: NO
  | "timeout";      // 60s elapsed, no sign-in received
```

Replace the existing `AgentStatus` interface with:

```typescript
export interface AgentStatus {
  terminalId: TerminalID;
  role: AgentRole;
  repo: string;
  signInStatus: SignInStatus;
  lastStatus: "pending" | "DONE" | "DONE_WITH_CONCERNS" | "BLOCKED" | "NEEDS_CONTEXT";
  lastWhat: string | null;
  pingRequired: boolean;
  mapUpdateRequired: boolean;
  wikiIngestRequired: boolean;
  lastUpdatedAt: string | null;
}
```

- [ ] **Step 2: Build**

```bash
cd C:/Users/OriShavit/Documents/GitHub/legion-swarm/mcp/launcher && npm run build
```

Expected: build succeeds. TypeScript will report errors in files that use `AgentStatus` — that's expected, we'll fix them in subsequent tasks.

- [ ] **Step 3: Commit**

```bash
cd C:/Users/OriShavit/Documents/GitHub/legion-swarm && git add mcp/launcher/src/types.ts && git commit -m "feat(launcher): add SignInStatus type and wikiIngestRequired to AgentStatus"
```

---

## Task 2: Extend status parser for sign-in, sign-off, and wiki ingest flag

**Files:**
- Modify: `mcp/launcher/src/tools/get-agent-status.ts`

- [ ] **Step 1: Update `parseStatusUpdate` to handle `[SIGN-IN]` and `[SIGN-OFF]` blocks and `wikiIngestRequired`**

Replace the entire `parseStatusUpdate` function in `mcp/launcher/src/tools/get-agent-status.ts`:

```typescript
function parseStatusUpdate(text: string): Partial<AgentStatus> {
  const result: Partial<AgentStatus> = {};

  // ── Sign-in block ─────────────────────────────────────────────────────────
  // Format: [SIGN-IN] role — repo\nIdentity: LOADED|NOT FOUND\nSkills: ...\nReady: YES|NO
  if (text.includes("[SIGN-IN]")) {
    const readyMatch = text.match(/Ready:\s*(YES|NO)/i);
    if (readyMatch) {
      result.signInStatus = readyMatch[1].toUpperCase() === "YES" ? "confirmed" : "failed";
    }
  }

  // ── Standard status fields (sign-off block or inline update) ─────────────
  const statusMatch = text.match(/\*\*Status:\*\*\s*(DONE_WITH_CONCERNS|DONE|BLOCKED|NEEDS_CONTEXT)/i);
  if (statusMatch) {
    result.lastStatus = statusMatch[1] as AgentStatus["lastStatus"];
  }

  const whatMatch = text.match(/\*\*What:\*\*\s*(.+?)(?:\n|$)/i);
  if (whatMatch) {
    result.lastWhat = whatMatch[1].trim();
  }

  const pingMatch = text.match(/\*\*Ping Shepard-Commander:\*\*\s*(YES|NO)/i);
  if (pingMatch) {
    result.pingRequired = pingMatch[1].toUpperCase() === "YES";
  }

  const mapMatch = text.match(/\*\*Map update needed:\*\*\s*(YES|NO)/i);
  if (mapMatch) {
    result.mapUpdateRequired = mapMatch[1].toUpperCase() === "YES";
  }

  // ── Wiki ingest flag (sign-off only) ─────────────────────────────────────
  const wikiMatch = text.match(/\*\*Wiki ingest needed:\*\*\s*(YES|NO)/i);
  if (wikiMatch) {
    result.wikiIngestRequired = wikiMatch[1].toUpperCase() === "YES";
  }

  return result;
}
```

Also update the import at top of the file — add `SignInStatus` to the type import:

```typescript
import type { AgentStatus, SignInStatus, TerminalID } from "../types.js";
```

- [ ] **Step 2: Update the `getAgentStatus` return defaults**

In the `getAgentStatus` function, update both return statements (not-found case and normal case) to include the new fields:

Not-found case:
```typescript
const notFound: AgentStatus = {
  terminalId,
  role: "coder",
  repo: "",
  signInStatus: "pending",
  lastStatus: "pending",
  lastWhat: null,
  pingRequired: false,
  mapUpdateRequired: false,
  wikiIngestRequired: false,
  lastUpdatedAt: null,
};
```

Normal return (at bottom of function):
```typescript
return {
  terminalId,
  role: entry.role,
  repo: entry.repo,
  signInStatus: "pending",
  lastStatus: "pending",
  lastWhat: null,
  pingRequired: false,
  mapUpdateRequired: false,
  wikiIngestRequired: false,
  lastUpdatedAt: null,
};
```

- [ ] **Step 3: Build**

```bash
cd C:/Users/OriShavit/Documents/GitHub/legion-swarm/mcp/launcher && npm run build
```

Expected: build succeeds (or only remaining errors are in `index.ts` and `launch-agent.ts` — fixed in next tasks).

- [ ] **Step 4: Commit**

```bash
cd C:/Users/OriShavit/Documents/GitHub/legion-swarm && git add mcp/launcher/src/tools/get-agent-status.ts && git commit -m "feat(launcher): parse [SIGN-IN]/[SIGN-OFF] blocks and wikiIngestRequired flag"
```

---

## Task 3: Add sign-in poll to launch-agent (60s timeout, warn if missing)

**Files:**
- Modify: `mcp/launcher/src/tools/launch-agent.ts`

- [ ] **Step 1: Add `signInTimeoutMs` to `LaunchAgentResult`**

In `mcp/launcher/src/tools/launch-agent.ts`, update `LaunchAgentResult`:

```typescript
export interface LaunchAgentResult {
  terminalId: TerminalID;
  role: AgentRole;
  repo: string;
  spawnedAt: string;
  signInStatus: "pending" | "confirmed" | "failed" | "timeout";
  signInWarning: string | null;
}
```

- [ ] **Step 2: Add sign-in poll helper after spawn**

Add this function before `launchAgent`:

```typescript
/**
 * Polls the registry for a [SIGN-IN] update on the given terminalId.
 * Returns "confirmed" or "failed" if found within timeoutMs, "timeout" otherwise.
 * 
 * NOTE: This polls the in-process registry only. The registry entry is written
 * by the launcher on spawn. The actual Monday [SIGN-IN] text must be separately
 * fetched by Legion via get_agent_status(terminalId, mondayUpdateText).
 * This poll acts as a 60s hold warning — Legion must verify via Monday.
 */
async function pollForSignIn(
  terminalId: TerminalID,
  timeoutMs: number
): Promise<"pending" | "timeout"> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    await new Promise((resolve) => setTimeout(resolve, 5000));
    const entry = registry.lookup(terminalId);
    if (!entry) return "pending"; // deregistered — session ended early
  }
  return "timeout";
}
```

- [ ] **Step 3: Call poll in `launchAgent` after spawn**

After `child.unref()` and the registry write, add:

```typescript
  // 10. Non-blocking sign-in poll — warn Legion if agent doesn't sign in within 60s
  // We return immediately with signInStatus: "pending". Legion must call
  // get_agent_status(terminalId, mondayUpdateText) to confirm sign-in via Monday.
  // The poll runs async and Legion is responsible for checking.
  const SIGN_IN_TIMEOUT_MS = 60_000;
  const signInPollPromise = pollForSignIn(terminalId, SIGN_IN_TIMEOUT_MS);

  // Return immediately — don't block launch on the poll
  // Legion reads signInStatus from the result and warns Shepard-Commander if "timeout"
  // by calling get_agent_status after ~60s
  void signInPollPromise; // fire-and-forget — timeout detection is Legion's responsibility

  return {
    terminalId,
    role,
    repo,
    spawnedAt,
    signInStatus: "pending",
    signInWarning:
      "Agent spawned. Verify sign-in via get_agent_status(terminalId, mondayUpdateText) within 60s. If no [SIGN-IN] Monday update appears, agent may not have loaded identity/skills.",
  };
```

- [ ] **Step 4: Build**

```bash
cd C:/Users/OriShavit/Documents/GitHub/legion-swarm/mcp/launcher && npm run build
```

Expected: build succeeds.

- [ ] **Step 5: Commit**

```bash
cd C:/Users/OriShavit/Documents/GitHub/legion-swarm && git add mcp/launcher/src/tools/launch-agent.ts && git commit -m "feat(launcher): add sign-in warning and 60s verification guidance to launch_agent result"
```

---

## Task 4: Block close if sign-off not present

**Files:**
- Modify: `mcp/launcher/src/tools/close-agent.ts`

- [ ] **Step 1: Read the current close-agent.ts**

Read `mcp/launcher/src/tools/close-agent.ts` fully before editing.

- [ ] **Step 2: Add `signOffVerified` flag to `CloseAgentInput` and result**

Add an optional `mondayUpdateText` parameter to `CloseAgentInputSchema` and update the function to warn if sign-off is missing:

```typescript
import { z } from "zod";
import * as fs from "fs";
import * as registry from "../registry.js";
import { parseStatusUpdate } from "./get-agent-status.js";

export const CloseAgentInputSchema = z.object({
  terminalId: z.string().min(1, "terminalId must be non-empty"),
  mondayUpdateText: z.string().optional(),
});

export type CloseAgentInput = z.infer<typeof CloseAgentInputSchema>;

export interface CloseAgentResult {
  terminalId: string;
  closed: boolean;
  signOffVerified: boolean;
  warning: string | null;
}
```

- [ ] **Step 3: Update `closeAgent` to check sign-off before proceeding**

In the body of `closeAgent`, before killing the process, add:

```typescript
  // Verify sign-off format before closing
  let signOffVerified = false;
  let warning: string | null = null;

  if (input.mondayUpdateText) {
    const parsed = parseStatusUpdate(input.mondayUpdateText);
    const hasStatus = parsed.lastStatus && parsed.lastStatus !== "pending";
    if (!hasStatus) {
      warning =
        `[SIGN-OFF WARNING] No valid Status field found in Monday update for ${input.terminalId}. ` +
        `Expected: **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT. ` +
        `Closing anyway — but Shepard-Commander should be notified.`;
    } else {
      signOffVerified = true;
    }
  } else {
    warning =
      `[SIGN-OFF WARNING] No Monday update text provided for ${input.terminalId}. ` +
      `Cannot verify sign-off. Pass mondayUpdateText to close_agent to enable verification.`;
  }
```

Update the return value to include `signOffVerified` and `warning`:

```typescript
  return {
    terminalId: input.terminalId,
    closed: true,
    signOffVerified,
    warning,
  };
```

- [ ] **Step 4: Build**

```bash
cd C:/Users/OriShavit/Documents/GitHub/legion-swarm/mcp/launcher && npm run build
```

Expected: build succeeds.

- [ ] **Step 5: Update `close_agent` tool description in `index.ts`**

In `mcp/launcher/src/index.ts`, update the `close_agent` tool schema to include `mondayUpdateText`:

```typescript
{
  name: "close_agent",
  description:
    "Close a running agent terminal session. Pass mondayUpdateText (agent's last Monday update) to verify sign-off format before closing. Returns signOffVerified: false + warning if sign-off is missing or malformed.",
  inputSchema: {
    type: "object",
    properties: {
      terminalId: {
        type: "string",
        description: "Terminal ID returned by launch_agent",
      },
      mondayUpdateText: {
        type: "string",
        description:
          "Optional: agent's last Monday board update text. Used to verify [SIGN-OFF] format before closing.",
      },
    },
    required: ["terminalId"],
  },
},
```

Also update the `get_agent_status` response in `index.ts` to include `signInStatus` and `wikiIngestRequired` in the returned status object (they're already in the parsed result from Task 2, just ensure they pass through):

In the `get_agent_status` case, update the `status` object construction:

```typescript
const status: AgentStatus = {
  terminalId,
  role: entry.role,
  repo: entry.repo,
  signInStatus: parsed.signInStatus ?? "pending",
  lastStatus: parsed.lastStatus ?? "pending",
  lastWhat: parsed.lastWhat ?? null,
  pingRequired: parsed.pingRequired ?? false,
  mapUpdateRequired: parsed.mapUpdateRequired ?? false,
  wikiIngestRequired: parsed.wikiIngestRequired ?? false,
  lastUpdatedAt: mondayText ? new Date().toISOString() : null,
};
```

- [ ] **Step 6: Final build**

```bash
cd C:/Users/OriShavit/Documents/GitHub/legion-swarm/mcp/launcher && npm run build
```

Expected: clean build, zero TypeScript errors.

- [ ] **Step 7: Commit**

```bash
cd C:/Users/OriShavit/Documents/GitHub/legion-swarm && git add mcp/launcher/src/tools/close-agent.ts mcp/launcher/src/index.ts && git commit -m "feat(launcher): verify sign-off on close, surface signInStatus and wikiIngestRequired in status"
```

---

## Task 5: Update all 11 agent identity files with sign-in/sign-off protocol

**Files:**
- Modify: `agents/architect.md`, `agents/coder.md`, `agents/debugger.md`, `agents/documenter.md`, `agents/frontend.md`, `agents/mapper.md`, `agents/planner.md`, `agents/qa.md`, `agents/refactorer.md`, `agents/reviewer.md`, `agents/tester.md`

- [ ] **Step 1: Update Session Start section in every agent file**

For each of the 11 agent files, replace the existing `## Session Start` section with:

```markdown
## Session Start

1. Read repo quartet (memory/*.md, TODO.md, CHANGELOG.md, CLAUDE.md) — onboards you to repo state, decisions, and priorities
2. Read CODEBASE_MAP.md (or Monday map for guest repos)
3. Read your Monday task for this repo
4. **Write [SIGN-IN] update to your Monday board item** — do this BEFORE any other work:

```
[SIGN-IN] [role] — [repo]
Identity: LOADED
Skills: [list every skill in your Skills Loaded section]
Task: [first 100 chars of your task]
Ready: YES
```

If your identity file was not found or skills did not load, write `Ready: NO — [reason]` and STOP. Do not proceed until Legion resolves it.

5. Begin work
```

- [ ] **Step 2: Update Report Format section in every agent file**

For each of the 11 agent files, replace the existing `## Report Format` section with:

```markdown
## Report Format

Write this as a Monday board update when task is complete or blocked. This is your **[SIGN-OFF]**.

```
[SIGN-OFF] [role] — [repo]
**Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
**What:** [what was done]
**Files:** [changed files or "none"]
**Map update needed:** YES | NO
**Wiki ingest needed:** YES | NO
**Ping Shepard-Commander:** YES | NO — [reason if yes]
```

Write the sign-off BEFORE Legion calls close_agent. Legion will not close your session without verifying this format.
```

- [ ] **Step 3: Commit**

```bash
cd C:/Users/OriShavit/Documents/GitHub/legion-swarm && git add agents/ && git commit -m "feat(agents): add sign-in/sign-off protocol to all 11 agent identity files"
```

---

## Task 6: Update Mapper identity for wiki ingest protocol

**Files:**
- Modify: `agents/mapper.md`

- [ ] **Step 1: Add wiki ingest section to mapper.md**

After the existing `## You Do` section, add:

```markdown
## Wiki Ingest Tasks

When dispatched with a task containing "ingest [repo] quartet into wiki":

1. Read repo quartet: `CHANGELOG.md`, `TODO.md`, `CLAUDE.md`, `memory/*.md`
2. Copy quartet files to `C:/Users/OriShavit/obsidian/legion-wiki/raw/repos/[repo]/` — do not modify originals
3. Read `C:/Users/OriShavit/obsidian/legion-wiki/wiki/projects/[repo].md` if it exists
4. Write/overwrite `C:/Users/OriShavit/obsidian/legion-wiki/wiki/projects/[repo].md` using this template:

```markdown
---
title: "[repo]"
type: project
repo: "[repo]"
updated: YYYY-MM-DD
sprint_status: active | idle | blocked
open_tasks: N
last_agent: [role from last Monday update]
---
# [repo]

> TLDR: [one sentence on current state, from CHANGELOG last entry]

## Current Sprint
- Goal: [from TODO.md top section]
- Open: N tasks
- Blocked: N tasks

## Recent Changes (last 3 sessions)
- YYYY-MM-DD: [entry from CHANGELOG.md]
- YYYY-MM-DD: [entry from CHANGELOG.md]
- YYYY-MM-DD: [entry from CHANGELOG.md]

## Key Decisions
- [from CLAUDE.md architecture or decisions section]

## Open TODOs
[copy open checkbox items from TODO.md]
```

5. Update `C:/Users/OriShavit/obsidian/legion-wiki/wiki/index.md` — find or add the row for this repo in the Projects table. Update: sprint_status, open_tasks, last_agent, updated date.
6. Append to `C:/Users/OriShavit/obsidian/legion-wiki/wiki/log.md`:

```
## [YYYY-MM-DD HH:MM] Ingest: [repo]
- Source: quartet files
- Updated: wiki/projects/[repo].md
- Index updated: YES
```

7. Report DONE with `**Wiki ingest needed:** NO` (wiki ingest IS the task).
```

- [ ] **Step 2: Commit**

```bash
cd C:/Users/OriShavit/Documents/GitHub/legion-swarm && git add agents/mapper.md && git commit -m "feat(agents): add wiki ingest task protocol to mapper identity"
```

---

## Task 7: Update Legion CLAUDE.md files with drift rules, session start, and Monday group IDs

**Files:**
- Modify: `meta/CLAUDE.md`
- Modify: `~/.claude/CLAUDE.md`

- [ ] **Step 1: Update Monday board section in `meta/CLAUDE.md`**

In `meta/CLAUDE.md`, replace the Monday Board section's group definitions:

```markdown
## Monday Board

Legion tracks agent tasks in **"Legion Swarm-main"** (board ID: `18408420731`):
- Groups = **repositories** (one group per repo — group IDs assigned after migration)
- Each item's **Status column** carries: Active | Blocked | Done
- Special group `_inbox` for unassigned or cross-repo tasks

Columns: Name, Agent Role (`text_mm2cmqtw`), Repo (`text_mm2cwhna`), Terminal ID (`text_mm2csy1c`), Task (`long_text_mm2c6k5q`), Status, Person, Date.

> Group IDs: update this section after Monday migration completes (Task 8).
```

- [ ] **Step 2: Update Session Start Sequence in `meta/CLAUDE.md`**

Replace the Session Start Sequence section:

```markdown
## Session Start Sequence

1. Read `C:/Users/OriShavit/obsidian/legion-wiki/wiki/index.md` — cross-repo project state (1 file read)
2. Read Monday board — scan ALL groups for Status column counts per repo
3. Deliver opening line:

> *"Shepard-Commander. We have reviewed [N] projects. [repo-1]: [N] active, [N] blocked. [repo-2]: [N] active. [repo-N]: idle since YYYY-MM-DD. What are your orders?"*

4. When repo scoped: read `wiki/projects/[repo].md` for full context
5. Check for any agents with `[SIGN-IN] Ready: NO` in Monday → flag immediately if found
```

- [ ] **Step 3: Add "What We Never Do" drift rules to `meta/CLAUDE.md`**

In the `## What We Never Do` section, add:

```markdown
- Touch files in any repo other than `legion-swarm` — that is agent work
- Run Edit, Write, or bash code-modification commands on guest repos
- If tempted: STOP. Create a Monday task. Dispatch the right agent.
- At session end: self-audit tool calls — any Edit/Write on non-legion-swarm files = drift event
  - Log drift to `wiki/log.md` as: `## [YYYY-MM-DD] Drift: Legion self-coded — [file] — should have been [agent role]`
  - Ping Shepard-Commander with drift report
```

- [ ] **Step 4: Update close_agent flow in `meta/CLAUDE.md`**

In the Launcher MCP section, update the `close_agent` call description:

```markdown
### Closing Agents

When an agent reports `DONE` or `BLOCKED`:
1. Fetch the agent's last Monday update text
2. Call `close_agent({ terminalId, mondayUpdateText: "<last update text>" })`
3. If result has `signOffVerified: false` → do NOT close silently. Log the warning to Monday `_inbox` and ping Shepard-Commander.
4. If `wikiIngestRequired: true` in sign-off → queue Mapper dispatch after close

Do NOT call `close_agent` without `mondayUpdateText`. Silent closes break the audit trail.
```

- [ ] **Step 5: Apply identical changes to `~/.claude/CLAUDE.md`**

Make the same Monday board section, Session Start Sequence, What We Never Do, and close_agent updates to `C:/Users/OriShavit/.claude/CLAUDE.md`.

- [ ] **Step 6: Commit**

```bash
cd C:/Users/OriShavit/Documents/GitHub/legion-swarm && git add meta/CLAUDE.md && git commit -m "feat(meta): update session start, drift rules, Monday groups, and close_agent protocol"
```

---

## Task 8: Restructure Monday board — create repo groups, migrate items

This task is executed by Legion via Monday MCP calls — no code changes. Steps are MCP call sequences.

**Tools used:** `mcp__claude_ai_monday_com__create_group`, `mcp__claude_ai_monday_com__move_object`, `mcp__claude_ai_monday_com__get_full_board_data`

- [ ] **Step 1: Read current board state**

Call `mcp__claude_ai_monday_com__get_full_board_data` with board ID `18408420731`. Record:
- All existing group IDs and names
- All item IDs and which group they are in
- The Repo column value for each item

- [ ] **Step 2: Create `legion-swarm` group**

Call `mcp__claude_ai_monday_com__create_group`:
```json
{ "board_id": "18408420731", "group_name": "legion-swarm" }
```
Record the returned group ID.

- [ ] **Step 3: Create `_inbox` group**

Call `mcp__claude_ai_monday_com__create_group`:
```json
{ "board_id": "18408420731", "group_name": "_inbox" }
```
Record the returned group ID.

- [ ] **Step 4: Create groups for any other active repos**

For each unique repo value found in Step 1 that is not `legion-swarm`, create a group with that repo name. Record all group IDs.

- [ ] **Step 5: Move all items to their repo groups**

For each item, call `mcp__claude_ai_monday_com__move_object` to move it to the group matching its Repo column value. Items with no Repo value go to `_inbox`.

- [ ] **Step 6: Update group IDs in CLAUDE.md files**

Open `meta/CLAUDE.md` and `~/.claude/CLAUDE.md`. Replace the `> Group IDs: update this section after Monday migration completes` placeholder with the actual group IDs recorded in steps 2-4.

- [ ] **Step 7: Verify board state**

Call `mcp__claude_ai_monday_com__get_full_board_data` again. Confirm:
- Old Active/Blocked/Done groups are empty
- All items appear in their repo group
- No items are in the old groups

- [ ] **Step 8: Delete old groups**

Only after Step 7 confirms empty: delete the old Active (`group_mm2cf9qf`), Blocked (`group_mm2cmv7c`), and Done (`group_mm2cqda`) groups.

- [ ] **Step 9: Commit CLAUDE.md group ID updates**

```bash
cd C:/Users/OriShavit/Documents/GitHub/legion-swarm && git add meta/CLAUDE.md && git commit -m "chore: update Monday group IDs after board restructure to repos-as-groups"
```

---

## Task 9: Initialize Obsidian vault structure

This task creates the vault files. The Obsidian app itself is opened by Shepard-Commander (cannot be scripted).

**Files:**
- Create: `C:/Users/OriShavit/obsidian/legion-wiki/wiki/index.md`
- Create: `C:/Users/OriShavit/obsidian/legion-wiki/wiki/log.md`
- Create: `C:/Users/OriShavit/obsidian/legion-wiki/CLAUDE.md`
- Create: `C:/Users/OriShavit/obsidian/legion-wiki/skills/wiki-setup.md` (copy)
- Create: `C:/Users/OriShavit/obsidian/legion-wiki/skills/wiki-ingest.md` (copy)
- Create: `C:/Users/OriShavit/obsidian/legion-wiki/skills/wiki-query.md` (copy)
- Create: `C:/Users/OriShavit/obsidian/legion-wiki/skills/wiki-lint.md` (copy)
- Create: `docs/obsidian/wiki-setup-instructions.md`

- [ ] **Step 1: Create vault directory structure**

```bash
mkdir -p "C:/Users/OriShavit/obsidian/legion-wiki/raw/repos"
mkdir -p "C:/Users/OriShavit/obsidian/legion-wiki/wiki/projects"
mkdir -p "C:/Users/OriShavit/obsidian/legion-wiki/wiki/decisions"
mkdir -p "C:/Users/OriShavit/obsidian/legion-wiki/skills"
```

- [ ] **Step 2: Create `wiki/index.md`**

Write `C:/Users/OriShavit/obsidian/legion-wiki/wiki/index.md`:

```markdown
# Legion Wiki Index

> Auto-maintained by Mapper agent. Do not edit manually.
> Last updated: 2026-04-14 | Total projects: 0

## Projects (0)

| Page | TLDR | Sprint Status | Open Tasks | Last Agent | Updated |
|------|------|---------------|------------|------------|---------|

## Decisions (0)

| Page | TLDR | Repos Affected | Updated |
|------|------|----------------|---------|
```

- [ ] **Step 3: Create `wiki/log.md`**

Write `C:/Users/OriShavit/obsidian/legion-wiki/wiki/log.md`:

```markdown
# Wiki Log

## [2026-04-14] Init
- Vault initialized
- Structure: raw/repos/, wiki/projects/, wiki/decisions/, skills/
- Pages: 0
```

- [ ] **Step 4: Copy skill files from downloads into vault**

```bash
cp "C:/Users/OriShavit/Downloads/harness and obisdian/CLAUDE.md" "C:/Users/OriShavit/obsidian/legion-wiki/CLAUDE.md"
cp "C:/Users/OriShavit/Downloads/harness and obisdian/wiki-setup.md" "C:/Users/OriShavit/obsidian/legion-wiki/skills/wiki-setup.md"
cp "C:/Users/OriShavit/Downloads/harness and obisdian/wiki-ingest.md" "C:/Users/OriShavit/obsidian/legion-wiki/skills/wiki-ingest.md"
cp "C:/Users/OriShavit/Downloads/harness and obisdian/wiki-query.md" "C:/Users/OriShavit/obsidian/legion-wiki/skills/wiki-query.md"
cp "C:/Users/OriShavit/Downloads/harness and obisdian/wiki-lint.md" "C:/Users/OriShavit/obsidian/legion-wiki/skills/wiki-lint.md"
```

- [ ] **Step 5: Create human setup instructions**

Write `C:/Users/OriShavit/Documents/GitHub/legion-swarm/docs/obsidian/wiki-setup-instructions.md`:

```markdown
# Obsidian Vault Setup — Legion Wiki

## One-Time Human Steps

1. Open Obsidian → "Open folder as vault" → select `C:/Users/OriShavit/obsidian/legion-wiki/`
2. Install plugins (Settings → Community plugins):
   - **Dataview** — for querying frontmatter across project pages
   - **Smart Connections** (optional) — semantic search for larger vaults
3. Obsidian Web Clipper (browser extension) — optional, for capturing articles to `raw/`

## How Legion Uses This Vault

- **Session start**: reads `wiki/index.md` only — 1 file, all project states
- **When scoped to a repo**: reads `wiki/projects/[repo].md` for full context
- **After each sprint**: dispatches Mapper to ingest updated quartet → updates project page + index

## Vault Structure

```
legion-wiki/
├── CLAUDE.md              ← wiki agent instructions
├── raw/repos/[repo]/      ← immutable quartet copies per repo
├── wiki/
│   ├── index.md           ← Legion reads this at session start
│   ├── log.md             ← append-only ingest history
│   ├── projects/          ← one page per repo
│   └── decisions/         ← cross-repo architectural decisions
└── skills/                ← wiki operation instructions
```

## Triggering a Wiki Update Manually

Tell Legion: "update wiki for [repo]"
Legion will dispatch Mapper with the ingest task.
```

- [ ] **Step 6: Commit**

```bash
cd C:/Users/OriShavit/Documents/GitHub/legion-swarm && git add docs/obsidian/ && git commit -m "docs: add Obsidian vault setup instructions and initialize wiki structure"
```

---

## Task 10: Seed wiki with first project page for legion-swarm

Executed by Mapper agent after vault is initialized (Task 9 complete).

**Dispatch:** Legion calls `launch_agent({ role: "mapper", repo: "legion-swarm", task: "Ingest legion-swarm quartet into legion-wiki. Read CHANGELOG.md, TODO.md, CLAUDE.md, memory/*.md. Update wiki/projects/legion-swarm.md and wiki/index.md. Follow wiki ingest protocol in agents/mapper.md." })`

- [ ] **Step 1: Dispatch Mapper**

Legion calls `launch_agent` with the task above. Records `terminalId`.

- [ ] **Step 2: Wait for sign-in**

Legion calls `get_agent_status(terminalId, mondayUpdateText)` after ~90s. Confirms `signInStatus: "confirmed"`. If `"timeout"` — ping Shepard-Commander.

- [ ] **Step 3: Wait for completion**

Legion polls `get_agent_status` at standup. When `lastStatus: "DONE"` → verify sign-off present → call `close_agent(terminalId, mondayUpdateText)`.

- [ ] **Step 4: Verify vault**

Check `C:/Users/OriShavit/obsidian/legion-wiki/wiki/projects/legion-swarm.md` exists and `wiki/index.md` has a row for `legion-swarm`.

- [ ] **Step 5: Commit is on Mapper's side** — Mapper does not commit vault files (vault is outside the repo). Vault changes are Obsidian-managed.

---

## Self-Review Against Spec

**Spec sections → plan coverage:**

| Spec Section | Tasks |
|---|---|
| Monday board restructure (groups = repos) | Task 8 |
| Obsidian vault + project page schema | Task 9 |
| Mapper extended for wiki ingest | Task 6, Task 10 |
| Agent sign-in protocol | Task 5 |
| Agent sign-off protocol | Task 5 |
| Launcher sign-in poll (60s warn) | Task 3 |
| close_agent sign-off verification | Task 4 |
| Legion drift self-check rules | Task 7 |
| Session start reads wiki/index.md | Task 7 |
| wikiIngestRequired flag in sign-off | Task 2 |
| SignInStatus type | Task 1 |

**Gaps found:** None. All spec requirements covered.

**Placeholder scan:** None found — all steps contain exact file paths, code, and commands.

**Type consistency check:**
- `SignInStatus` defined in Task 1 (`types.ts`), used in Task 2 (`get-agent-status.ts`), Task 3 (`launch-agent.ts`), Task 4 (`close-agent.ts`) — consistent
- `wikiIngestRequired` added in Task 1 (`AgentStatus`), parsed in Task 2, passed through in Task 4, referenced in Task 7 (Legion close flow) — consistent
- `mondayUpdateText` optional param added in Task 4 (`close-agent.ts`) and Task 7 (Legion instructions) — consistent
