# Changelog - Legion Swarm

## 2026-05-18

### Changed
- Added `legion/monday_preflight.py` and tests for durable `.codex/state/MONDAY_MCP_PREFLIGHT.md` records.
- Updated Legion dispatch instructions and ownership tracking so missing Monday write access is recorded before agent launch.
- Committed refreshed Graphify output as `6194baa` after reviewing the hook-generated graph files.
- Added repo-local quartet closeout notes for the Graphify push loop: `TODO.md`, `MEMORY.md`, `CHANGELOG.md`, and `CODEX_HANDOFF.md`.
- Clarified that the default Claude/Codex sync loop is repo quartet first; Obsidian vault writeback is reserved for major phase summaries, handoff checkpoints, or explicit cross-repo knowledge.

### Notes
- The previous closeout plan referenced `00decc4`, but that commit was not present in this checkout. The actual outgoing Graphify commit is `6194baa`.

## 2026-05-05 — Legion Nerve Center v1

- Added `legion/` package: cross-repo live TUI dashboard.
- Panels: Repo Grid (all repos, git state + Nexus harness), Activity Feed (NDJSON tail), Agent Status (Claude ctx + Codex tasks), Command Bar.
- Read-only filesystem watcher, no network in v1.
- Entry: `python -m legion` (config at `legion/config.json`).

## 2026-05-12

### Added
- Sprint 08 Nerve Center v1: 8 task packets written to `.agent-harness/inbox/` (nc-01 through nc-08); `docs/plans/2026-05-05-legion-nerve-center.md` is the implementation plan.
- `docs/plans/2026-05-05-legion-nerve-center-operative.md` — operative version of the plan for Codex dispatch.
- `docs/sprints/2026-05-05-legion-swarm-sprint-08-nerve-center-v1.md` — sprint contract.
- `docs/dialogue-format.md` — dialogue format spec for Claude/Codex cross-terminal messaging.
- `docs/tracking/2026-05-06-legion-nexus-sync-tracker.md` — entries 1-9 recording all Legion/Nexus sync changes through 2026-05-10.

### Changed
- `TODO.md` — marked `project_nexus` group ID confirmed and template drift done; next action is Nerve Center v1.

## 2026-05-07

### Added
- Restarted Project Nexus sprint cadence with `documenter-project_nexus-20260507-1`.
- Recorded Project Nexus KB-backed dispatch state in `~/.claude/swarm-state.json`.
- Created Nexus sprint scaffold at `project_nexus/docs/sprints/2026-05-07-template-audit.md`.

### Notes
- Monday live item creation was not performed because no Monday MCP tool or `MONDAY_*` token was available in this Codex environment. Nexus work is routed through the known `_inbox` group until a `project_nexus` group ID is confirmed.

