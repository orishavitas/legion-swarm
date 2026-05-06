# Legion/Nexus Baseline Contract

> Baseline project constraint. This file is the repo-local rule for how Legion Swarm integrates with Project Nexus.

## Position

Legion Swarm and Project Nexus must work together, but one should not be packed into the other.

Legion is the orchestration layer:
- defines sprint/task intent;
- assigns owners;
- launches agents;
- owns swarm-state;
- coordinates vault and Monday updates for Legion-managed tasks.

Nexus is the execution and verification harness:
- receives task packets;
- constrains scope;
- records inbox/outbox/artifacts/logs;
- runs monitor verification;
- countersigns results;
- closes Monday only for Nexus packets.

## Bridge Rule

Integration happens through a bridge contract, not through repo consolidation.

Required flow:
1. Legion decides whether work is plain Legion dispatch or Nexus packet dispatch.
2. For Nexus packet dispatch, Legion emits a complete Nexus task packet.
3. Codex executes the packet under Nexus rules.
4. Nexus monitor verifies and writes result/review/artifacts.
5. Legion reads the Nexus result and updates swarm-state, vault, and Monday only where Legion owns the target.

## Baseline Constraints

- Do not move Legion state into Project Nexus.
- Do not move Nexus monitor rules into Legion docs only.
- Do not let Legion and Nexus write the same Monday item.
- Do not change packet, monitor, sprint, watchdog, vault, path, or handoff contracts in only one repo.
- Do not push sync-contract changes until both repos have been updated and local verification has run.
- Check visible context and session/API usage every round and at least once every five minutes during long work. At 75 percent context, pause for quartet/status updates plus checkpoint handoff; at 90 percent session/API usage, stop after handoff and wait for reset.

## Required Cross-Repo Updates

When this repo changes:

| Change in Legion Swarm | Required Project Nexus update |
|---|---|
| Dispatch methodology | Nexus bridge contract or task-packet producer docs |
| Sprint/task ownership rule | Nexus AGENTS/CLAUDE planning or result contract if packets are affected |
| Monday ownership rule | Nexus monitor spec/runbook if Nexus packet closure is affected |
| Vault path or mapper rule | Nexus CLAUDE/wiki/runbook if Nexus reads that path |
| Watchdog or handoff behavior | Nexus AGENTS/runbook if packets or monitor depend on it |
| Codex runtime state format | Nexus task packet/result contract if Codex execution is affected |

## Tracking Requirement

Every cross-system methodology or path change must be logged in:
- this repo: `docs/tracking/2026-05-06-legion-nexus-sync-tracker.md`;
- Project Nexus: `docs/tracking/2026-05-06-nexus-legion-sync-tracker.md`.

Each tracker entry must include:
- date;
- change;
- concept;
- implementation;
- methodology impact;
- failures or blockers;
- verification and tests;
- matching repo update status.
