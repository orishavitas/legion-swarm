# Legion Swarm - Codex KB

> Codex reads this file once at session start. It is the single source of truth for repo-specific context.
> Update this file whenever conventions, stack, or known issues change.
> For cross-repo and product-level context, see the Obsidian wiki path below.

## What This Repo Does

`legion-swarm` is the local meta-orchestration repo for Legion: a persistent, role-specialized agent swarm coordinated through Monday.com, Google Chat, and launcher MCP terminal sessions. Legion owns planning, dispatch, monitoring, and durable handoff state for agent work across repos under `C:/Users/OriShavit/Documents/GitHub/`.

## Obsidian Wiki

- **Project page:** `~/obsidian/legion-wiki/wiki/projects/legion-swarm.md`
- **Cross-repo index:** `~/obsidian/legion-wiki/wiki/index.md`
- Read the project page for current operational state, sprint context, and cross-repo dependencies that are broader than this KB.

## Stack

- Language / runtime: Python and TypeScript/Node.js, depending on subsystem
- Framework: Model Context Protocol servers for launcher and integrations
- Test runner: subsystem-specific; Python tasks use `pytest`, Node MCP packages use their package scripts
- Package manager: `npm` for MCP Node packages; Python package tasks use `pip` with local requirements files
- Key dependencies: Launcher MCP, Monday board `18408420731`, Google Chat webhook integration, `.agent-harness` task packets

## Repo Layout

```text
agents/                 Agent identity files and Codex KB files.
agents/kb/              Repo-specific Codex startup context.
agents/settings/        Per-role skill loadout/settings stubs.
docs/plans/             Detailed implementation plans.
docs/sprints/           Monitor-readable sprint files.
meta/CLAUDE.md          Legion operating identity and dispatch contract.
mcp/launcher/           MCP server that launches physical Windows Terminal agent sessions.
mcp/google-chat/        Google Chat ping integration.
monday/                 Monday board templates and helpers.
.agent-harness/inbox/   Nexus-style task packets for executable agent work.
.agent-harness/outbox/  Expected result packet location after task execution.
.agent-harness/artifacts/ Expected verification evidence location after task execution.
```

## Conventions

- Follow `meta/CLAUDE.md` first for Legion dispatch and monitoring rules.
- Codex implementation work is sprint-driven: read the active sprint file, execute only the requested task ID, and stop after writing the required result/evidence.
- Do not start a dependent Nerve Center task until the previous task has a monitor countersignature.
- Keep branch names aligned with task packets, for example `task/T-20260505-nc-01-scaffold`.
- Preserve existing dirty work. Do not revert files you did not change.
- Use file-backed verification evidence where a packet or sprint asks for it.
- Monday board for this repo is `18408420731`, group `group_mm2df5v0`.

## Known Issues / Gotchas

- `agents/kb/legion-swarm.md` is required before dispatching Codex for this repo. `meta/CLAUDE.md` explicitly blocks Codex dispatch if the KB file is missing.
- Monday MCP tools may be unavailable in some Codex sessions. If live update is blocked, record the exact pending update text in the operative handoff.
- The working tree can be dirty from prior agent sessions. Treat unrelated edits as user-owned.
- Root quartet files (`AGENTS.md`, `CHANGELOG.md`, `TODO.md`) may be absent in this checkout; use `meta/CLAUDE.md`, sprint files, plans, and task packets as the active contract.
- `project_nexus/` parent folder is a stale flat snapshot — NOT the live repo. The live clone is `C:/Users/OriShavit/Documents/GitHub/project_nexus/project-nexus/`. Any reference to `project_nexus/` without the nested suffix targets stale files. See `project_nexus/STALE.md`.

## Key Files to Know

| File | Purpose |
|------|---------|
| `meta/CLAUDE.md` | Legion identity, Monday board mapping, Codex dispatch contract. |
| `docs/sprints/SPRINT-FORMAT.md` | Required task block format for monitor-readable sprint files. |
| `docs/plans/2026-05-05-legion-nerve-center.md` | Detailed Nerve Center v1 implementation source of truth. |
| `docs/sprints/2026-05-05-legion-swarm-sprint-08-nerve-center-v1.md` | Active sprint file for Nerve Center v1. |
| `.agent-harness/inbox/T-20260505-nc-01-scaffold.task.md` | Active first executable task packet. |
| `mcp/launcher/` | Launcher MCP server used by Legion to dispatch physical agent terminals. |

## How to Run Tests

Use the verification command from the active task packet. For the current first task:

```powershell
python -c "import legion; print(legion.__version__)"
```

## How to Run the App Locally

The Nerve Center app does not exist until Sprint 08 implementation tasks create it. After the sprint is complete, the intended entry point is:

```powershell
python -m legion
```

## Codex Runtime State

> `.codex/state/` in repo root - Codex reads and writes these every session when present.

| File | Written by | Purpose |
|------|-----------|---------|
| `TASK_STATE.md` | Legion | Current objective, constraints, task context. |
| `LAST_RUN.md` | Codex | What last session did, commands run, result, remaining risk. |
| `DECISIONS.md` | Legion / Codex | Architectural/product decisions that must not be reversed. |
| `HANDOFF_[ts].md` | `codex-handoff.ps1` | Timestamped snapshot of state and git at session end. |

Stop conditions for Codex:
- Tests fail twice for the same unclear reason.
- Unrelated dirty files make the requested task unsafe to isolate.
- Next step requires product or architecture judgment not covered by the plan or packet.
- Required live Monday update or launcher action is unavailable and the packet requires it before work can continue.
