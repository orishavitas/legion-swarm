# Legion Swarm Sync Tracker - 2026-05-06

Purpose: track Legion-side changes that affect Project Nexus synchronization.

## Entry 1 - Baseline Sync Constraint

Date: 2026-05-06

Change:
- Added a root `AGENTS.md` for Legion Swarm.
- Added `docs/contracts/legion-nexus-baseline.md`.
- Linked the baseline from `README.md` and `docs/ownership-map.md`.

Concept:
- Legion and Nexus stay separate.
- Legion orchestrates.
- Nexus executes and verifies.
- The systems synchronize through explicit bridge contracts and mirrored repo updates.

Implementation:
- Legion now has a repo-root agent contract requiring Codex/agents to read the baseline before changing paths, methodology, execution plans, sprint conventions, packet rules, monitor behavior, vault ownership, Monday ownership, watchdog behavior, or handoff formats.
- The baseline contract defines the Legion-to-Nexus flow and required matching Nexus updates.

Methodology Impact:
- Any cross-system change is incomplete until the matching Nexus source or tracker is updated.
- Git pushes are not part of the local baseline workflow unless the operator explicitly asks for a push.

Failures / Blockers:
- None during implementation.
- Existing unrelated untracked runtime files remain in the working tree and were not edited.

Verification / Tests:
- Confirmed `README.md` links to the baseline contract.
- Confirmed `docs/ownership-map.md` links to the baseline contract and names both sync trackers.
- Confirmed Project Nexus was updated in the same local pass.

Matching Repo Update Status:
- Complete locally: Project Nexus tracker, baseline contract, README, CLAUDE, and AGENTS sources were updated in the same local execution pass.

## Entry 2 - Context and Usage Watchdog Cadence

Date: 2026-05-06

Change:
- Added the explicit every-round plus five-minute check cadence for visible context and session/API usage.
- Added the 75 percent context handoff threshold and 90 percent session/API usage stop threshold to Legion-side contracts.

Concept:
- Context and usage limits are operational constraints, not advisory reminders.
- Agents must preserve state before the system becomes unreliable.

Implementation:
- Updated `AGENTS.md`.
- Updated `docs/contracts/legion-nexus-baseline.md`.
- Updated global workstation contracts outside this repo for Codex and Claude pickup.

Methodology Impact:
- At 75 percent context, work pauses for quartet/status updates, checkpoint creation, and session handoff before context is cleared or compacted.
- At 90 percent session/API usage, work stops after handoff and does not resume until reset.

Failures / Blockers:
- None.

Verification / Tests:
- `rg` confirmed the five-minute, 75 percent context, and 90 percent session/API usage rules are present in global, Legion, and Nexus contracts.
- `git diff --check` passed for `legion-swarm`; only pre-existing line-ending warnings were reported.

Matching Repo Update Status:
- Complete locally: Project Nexus tracker and baseline contract were updated in the same local execution pass.
