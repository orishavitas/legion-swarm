# Memory - Legion Swarm

## 2026-05-18 - Monday MCP Dispatch Preflight

- Added `legion/monday_preflight.py` to record Monday write-access evidence at `.codex/state/MONDAY_MCP_PREFLIGHT.md` before Legion dispatch.
- `meta/CLAUDE.md` now gates `launch_agent`: if Monday write tools are missing or blocked, record `status: missing` with evidence and do not dispatch.
- This does not change Nexus packet closure; Project Nexus monitor remains the Monday writer for Nexus packets.

## 2026-05-18 - Graphify Push Closeout

- Graphify output was reviewed and committed as `6194baa` (`chore(graphify): update graph output`) before quartet closeout.
- The previous plan referenced `00decc4`, but that commit was not present in this checkout after `git fetch origin master`; `master` and `origin/master` were both at `50c064c` before the new Graphify commit.
- The Graphify post-commit hook rewrites `graphify-out/GRAPH_REPORT.md`; it can reintroduce trailing whitespace on empty-node lines. Clean the report and use a scoped `core.hooksPath` override for doc-only closeout commits when needed so the hook does not re-dirty generated output.
- Default closeout loop for this repo is repo quartet first: `TODO.md`, `CHANGELOG.md`, `MEMORY.md`, and `CODEX_HANDOFF.md`. Vault writeback is reserved for major phase summaries, handoff checkpoints, or explicit cross-repo knowledge.
