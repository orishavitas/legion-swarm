# AGENTS.md - Legion Swarm

This file applies to Codex and any other coding agent working in this repo.

## Baseline Constraint

Legion Swarm and Project Nexus are separate systems that must operate in sync.
Legion owns orchestration, dispatch, swarm state, role ownership, and Monday coordination for Legion-managed tasks.
Nexus owns packet execution, monitor verification, countersignature, and Monday closure for Nexus packets.

Do not merge one system into the other. Integrate them through an explicit bridge contract.

Before changing paths, methodology, execution plans, sprint conventions, packet rules, monitor behavior, vault ownership, Monday ownership, watchdog behavior, or handoff formats:
- Read `docs/contracts/legion-nexus-baseline.md`.
- Read `docs/ownership-map.md`.
- Update the matching Project Nexus contract or tracker when the change affects Nexus behavior.
- Update this repo's tracker at `docs/tracking/2026-05-06-legion-nexus-sync-tracker.md`.

If the matching Nexus update cannot be made in the same pass, the work is not complete. Record the stale source, intended update, blocker, and next safe step in the tracker.

## Local Execution Rules

- Work locally and test locally.
- Do not push unless the operator explicitly asks for a push.
- Do not edit unrelated dirty files.
- Commit only scoped, related changes.
- Keep runtime artifacts out of commits unless a task explicitly makes them durable fixtures.
- Check visible context and session/API usage every round and at least once every five minutes during long work. At 75 percent context, pause for quartet/status updates plus checkpoint handoff; at 90 percent session/API usage, stop after handoff and wait for reset.

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)
