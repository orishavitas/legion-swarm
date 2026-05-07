# Legion Ownership Map

> Single source of truth for who writes what. When two systems could both write to the same target, this page is the tiebreaker.
> **Last updated:** 2026-05-06
> **Full contracts:** see the file references in the right column.
> **Legion/Nexus separation baseline:** [`docs/contracts/legion-nexus-baseline.md`](contracts/legion-nexus-baseline.md)

---

## Dispatch and Orchestration

| Concern | Owner | Contract / Evidence |
|---|---|---|
| TaskSpec construction (role, repo, objective, AC) | **Claude/Legion** | `~/.claude/docs/legion-dispatch.md` §Pre-Dispatch Checklist |
| Dispatching subagents (launch, retry, escalate) | **Claude/Legion** | `~/.claude/docs/legion-dispatch.md` §Dispatch Loop |
| `~/.claude/swarm-state.json` — ALL writes | **Claude/Legion (sole writer)** | `~/.claude/memory/legion-swarm.md` "Sprint 08 Decision"; `~/.claude/docs/legion-dispatch.md` steps 4 + 8 |
| `.codex/state/TASK_STATE.md` (pre-dispatch objective) | **Claude/Legion** | `agents/codex.md` §Step 3; `agents/kb/KB-TEMPLATE.md` Codex Runtime State table |
| `.codex/state/DECISIONS.md` (architectural decisions) | **Claude/Legion** (primary), Codex (may append during session) | `agents/codex.md` §Step 3 |

---

## Contract Change Propagation

Claude and Codex must be updated together whenever a change affects paths, methodology, execution plans, sprint conventions, task packets, monitor verification, vault ownership, Monday ownership, watchdog behavior, or handoff formats.

| Change type | Claude-visible update | Codex-visible update |
|---|---|---|
| Path or repo location | `~/.claude/CLAUDE.md`, dispatch docs, sprint/task packet, vault playbook if durable | `~/.codex/AGENTS.md`, repo `AGENTS.md`, KB file, task packet |
| Methodology or execution plan | Sprint file, plan doc, Monday update text, dispatch notes | Task packet, Codex KB, `.codex/state/TASK_STATE.md`, skill/runbook |
| Ownership or writer rule | `docs/ownership-map.md`, dispatch docs, relevant `CLAUDE.md` | `docs/ownership-map.md`, `agents/codex.md`, relevant `AGENTS.md` |
| Verification or monitor behavior | Nexus/Legion runbook, monitor docs, Monday status rule | Task packet verification commands, result/writeback contract |
| Handoff or watchdog behavior | Claude watchdog/dispatch docs, Monday closeout rule | Codex scripts, `agents/codex.md`, `.codex/state` contract |

If one side cannot be updated in the same pass, the current task must end with a blocker or handoff naming the unsynced source and the exact intended update. No agent should implement from stale or one-sided instructions.

For Legion/Nexus changes, also update this repo's `docs/tracking/2026-05-06-legion-nexus-sync-tracker.md` and Project Nexus' `docs/tracking/2026-05-06-nexus-legion-sync-tracker.md`.

---

## Codex Runtime (per-repo)

| Concern | Owner | Contract / Evidence |
|---|---|---|
| `.codex/state/LAST_RUN.md` | **Codex** | `agents/codex.md` §Step 9 completion signal |
| `.codex/state/HANDOFF_[ts].md` | **Codex** (via `scripts/codex-handoff.ps1`) | `scripts/codex-handoff.ps1` |
| `.codex/state/MONDAY_UPDATE.md` | **Codex** (via `scripts/codex-handoff.ps1`) | `agents/codex.md` §Monday Update Writing Guide |
| `.codex/state/DIALOGUE.md` | **Both Claude and Codex** (append-only, TURN-gated) | `docs/dialogue-format.md` |
| `.codex/state/TURN.md` | **Writer of each message sets TURN to the other party** | `docs/dialogue-format.md` §TURN.md Protocol |
| Sprint file task status (`pending → in_progress → done/blocked`) | **Codex** | `agents/codex.md` Steps 6 + 9 |

---

## Monday Board

| Item type | Who writes | When | Rule |
|---|---|---|---|
| Legion-driven task items | **Claude/Legion** | Once, on LEGION_COMPLETE received | `~/.claude/docs/legion-dispatch.md` §Monday Update Protocol |
| Nexus packet items (Done/Stuck) | **Monitor** (`project_nexus/project-nexus/monitor/`) | On countersignature | `project_nexus/project-nexus/docs/specs/nexus-spec-v1.md` |
| Dialogue log entries | **Claude** (logs on behalf of Codex too) | After every message exchange | `docs/dialogue-format.md` §Monday Logging; `scripts/claude-dialogue-log.ps1` |

**Hard rule:** Legion writes Monday for Legion-driven items. Monitor writes Monday for Nexus packets. **They never write the same item.** If an item appears in both paths, escalate to Shepard-Commander before writing.

---

## Vault (Obsidian `legion-wiki`)

| Concern | Owner | Rule |
|---|---|---|
| `projects/[repo]/index.md` refresh | **Mapper agent** (dispatched by Legion) | Legion never writes vault project pages directly. |
| `03-hard-truths/` sync (CLAUDE.md, CHANGELOG.md, TODO.md, memory/*.md) | **Operator** runs `scripts/sync-vault-hard-truths.ps1` | Not automated; run before any dispatch that requires Codex to read vault hard truths. |
| `system/` conventions, skills, agent-instructions | **Claude/Legion** via documented mapper dispatch | Mapper is sole writer of vault project and system pages. |

---

## Watchdog + Context Control

| Concern | Owner | Where |
|---|---|---|
| Context usage watchdog (Claude sessions) | **`~/.claude/hooks/context-watchdog.js`** (Claude Code Stop hook) | Automatically invoked on Claude session stop; reads transcript, triggers quartet-update at 75% |
| `.watchdog/STOP` sentinel write | **Claude context-watchdog hook** | Written at 95% API usage to halt all agents |
| `.watchdog/STOP` sentinel read (Codex) | **Codex** (Step 0 of session protocol) | `agents/codex.md` §Step 0; `scripts/codex-watchdog-check.ps1` |
| API usage hard stop broadcast | **Claude context-watchdog** | Writes sentinel; all agents with the PostToolUse hook or watchdog-check script observe it |

---

## Notes

- **Codex never writes to Monday directly.** Claude/Legion reads `MONDAY_UPDATE.md` and posts on Codex's behalf.
- **Monitor never writes to swarm-state.json.** That file is Claude/Legion-only.
- **Legion never writes vault project pages.** Vault pages are always a Mapper dispatch.
- If a concern is absent from this table, default owner is **Claude/Legion**, which may re-delegate via dispatch.
