# Sprint 05 — Monday Board Schema + Monday Agent
> Legion Swarm | 2026-04-05 | Status: Ready

## Goal

Establish the Monday.com nervous system for Legion Swarm: a canonical board template for per-repo boards and a global Monday agent that owns board creation and structure — the only agent permitted to touch board schema.

## Reference

- Design spec: `docs/specs/2026-04-05-legion-swarm-design.md` — Section 5 (Board Schema)
- Monday MCP tools: `mcp__claude_ai_monday_com__*` — use `create_board`, `create_column`, `create_group`, `all_monday_api` for GraphQL
- Agent identity format: Section 2, Agent Identity File Structure

---

## Tasks

---

### T01 — Board Template JSON

**What to build:** Canonical board template definition that the Monday agent uses to create new per-repo boards. Defines the board name pattern, groups, and all columns with their Monday column types, IDs, and accepted values.

**Files:**
- Create `legion-swarm/monday/board-templates/repo-board.json`

**Spec for the file:**
- Board name pattern: `[repo-name] — Legion Swarm`
- Groups (in order): `Sprint Active`, `Sprint Backlog`, `Blocked`, `Done`
- Columns:
  - `agent` — dropdown, values: `Architect | Planner | Coder | Tester | Debugger | Reviewer | Refactorer | Mapper | Documenter | Frontend | QA`
  - `status` — status column (Monday native), values: `Idle | Active | Done | Blocked | Needs Decision`
  - `current_task` — text
  - `last_update` — text
  - `terminal_id` — text
  - `ping_required` — checkbox
  - `map_update_required` — checkbox
- Include the Monday `column_type` string for each column (e.g. `dropdown`, `status`, `text`, `checkbox`) so the Monday agent can pass them verbatim to `create_column`
- Include a `version` field: `"1.0.0"` and a `schema_updated` field: `"2026-04-05"`

**Verify:** JSON is valid and all 7 columns are present with their types and values. Confirm `groups` array has exactly 4 entries in the correct order.

**Commit:** `feat(monday): add repo-board template v1.0.0`

---

### T02 — Monday Agent Identity File

**What to build:** Identity file for the global Monday agent — the singleton that manages board structure across all repos.

**Files:**
- Create `legion-swarm/agents/monday-agent.md`

**Spec for the file:**
Use the standard agent identity format from the design spec. Key points to encode:

- Role name: `Monday Agent`
- Identity: The Monday agent is the sole owner of board structure. It creates boards for new repos, enforces schema against `repo-board.json`, and repairs drift. It never touches item content — that belongs to the specialist agents.
- You Do: create new boards via `create_board` + `create_column` + `create_group`; validate existing boards against `repo-board.json`; add missing columns; fix group order; report schema drift to Legion
- You Never Do: write to item columns (Current Task, Last Update, etc.); delete items or groups; touch any board not under Legion Swarm naming pattern; act on a repo board without Legion authorizing it
- Skills Loaded: none (operates entirely via Monday MCP)
- Session Start: read `repo-board.json` template, check if target board exists, diff structure, repair or create, report to Legion
- Report Format: standard format from spec

**Verify:** File follows the identity format exactly. "You Never Do" section has a hard boundary against writing item content. Session Start is specific to board schema work.

**Commit:** `feat(agents): add monday-agent identity file`

---

### T03 — Agent Status Write Protocol

**What to build:** A concise protocol document that defines exactly how specialist agents write status to Monday — which columns, what format, and when.

**Files:**
- Create `legion-swarm/monday/STATUS_WRITE_PROTOCOL.md`

**Spec for the document:**

Cover four things precisely:

1. **Which columns agents write** — agents write only to: `Current Task` (on task start), `Last Update` (on every status change), `Ping Required` (set true when BLOCKED or NEEDS_DECISION), `Map Update Required` (set true when Mapper should run)

2. **What agents never write** — `Agent` (set by Launcher at launch), `Terminal ID` (set by Launcher), `Status` column (set by agent via dropdown, not text)

3. **Last Update format** — single line, max 120 chars:
   `[YYYY-MM-DD HH:MM] [STATUS] [what happened or what is blocked on]`
   Example: `2026-04-05 14:32 DONE Refactored auth middleware, reduced 3 functions to 1`

4. **State machine** — when to set each Status value:
   - `Active` — set immediately when task starts
   - `Done` — set when Report Format is written and work is complete
   - `Blocked` — set when cannot proceed, set `Ping Required = true`
   - `Needs Decision` — set when product/design ambiguity, set `Ping Required = true`
   - `Idle` — Launcher sets this; agents never set Idle themselves

**Verify:** Document is unambiguous — an agent reading it knows exactly which MCP call to make for each state change. No vague phrasing.

**Commit:** `docs(monday): add agent status write protocol`

---

### T04 — Legion Board Read Protocol

**What to build:** A concise protocol document that defines exactly how Legion reads the Monday board to derive sprint state — which fields it reads, how it interprets them, and what actions it takes.

**Files:**
- Create `legion-swarm/monday/BOARD_READ_PROTOCOL.md`

**Spec for the document:**

Cover three things:

1. **Session open read** — Legion calls `get_board_info` + `get_board_items_page` on the active repo's board. It reads: all items in `Sprint Active` group, their `Agent`, `Status`, `Current Task`, `Last Update`, `Ping Required`, `Map Update Required` columns. It then constructs the standup summary: how many agents active, how many blocked, how many need pings.

2. **Ping sweep** — After reading the board, Legion checks `Ping Required = true` on any item. For each: read `Last Update`, compose a Google Chat ping to Shepard-Commander in the format defined in Section 6 of the spec, then clear `Ping Required` (set to false) via `change_item_column_values`.

3. **Sprint completion detection** — Sprint is complete when all items in `Sprint Active` have `Status = Done`. Legion then: pings Shepard-Commander on Google Chat with sprint complete message, offers to move items to `Done` group, waits for authorization before moving.

**Verify:** Protocol is unambiguous. A Legion session reading this knows exactly which MCP calls to make in which order. No vague phrasing.

**Commit:** `docs(monday): add Legion board read protocol`

---

### T05 — Monday Agent Settings File

**What to build:** Skill settings JSON for the Monday agent, consistent with the pattern established in Sprint 01 for other agent settings files.

**Files:**
- Create `legion-swarm/agents/settings/monday-agent-settings.json`

**Spec:** Follow the same structure as existing agent settings files in `legion-swarm/agents/settings/`. The Monday agent has no skill loadout from the design spec table (it operates via MCP only), so the skills array is empty. Include `model`, `allowedTools` restricted to `mcp__claude_ai_monday_com__*` tools only, and `identity` pointing to `agents/monday-agent.md`.

**Verify:** File is valid JSON. `allowedTools` includes all Monday MCP tools and excludes file editing tools — this agent should not be touching the filesystem.

**Commit:** `feat(agents): add monday-agent settings file`

---

## Sprint Definition of Done

- [ ] `repo-board.json` is valid, complete, and versioned
- [ ] `monday-agent.md` follows the identity format and has hard boundaries against writing item content
- [ ] `STATUS_WRITE_PROTOCOL.md` is unambiguous — agent knows exactly which column + format for every state
- [ ] `BOARD_READ_PROTOCOL.md` is unambiguous — Legion knows the exact MCP call sequence
- [ ] `monday-agent-settings.json` locks the Monday agent to Monday MCP tools only
- All 5 files committed

## Sprint Non-Goals

- Actually creating a Monday board (T01-T02 define the template and agent; board creation happens when Legion enters a real repo for the first time)
- Monday agent being connected to a live terminal session (that is Launcher MCP work, Sprint 04)
- Any polling or webhook integration (out of scope per design spec)
