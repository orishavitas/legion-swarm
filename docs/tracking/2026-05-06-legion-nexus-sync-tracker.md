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

## Entry 3 - Sprint 11.1 Handoff Smoke Proof

Date: 2026-05-07

Change:
- Hardened `scripts/codex-handoff.ps1` so its read-only Git probes bypass the broken workstation global Git ignore path.
- Ran the local Sprint 11.1 smoke proof for `HANDOFF_[timestamp].md` and `MONDAY_UPDATE.md`.
- Removed the smoke output files after verification.

Concept:
- The Codex-to-Legion Monday update handoff must be executable, not just documented.
- Smoke output must never remain in `.codex/state/` where Legion could mistake it for a real task update.

Implementation:
- Added `git -c core.excludesFile=` to the script's `branch`, `status`, and `log` calls.
- This avoids the local `C:\Users\OriShavit\.config\git\ignore` permission warning that PowerShell treats as a terminating native command error under `$ErrorActionPreference = "Stop"`.

Methodology Impact:
- Sprint 11.1 proof now has local evidence that the handoff script can write both required files.
- The script still writes to `.codex/state`; on this machine, direct Codex sandbox writes to that folder can be denied by ACLs, so the smoke proof required the approved local PowerShell execution path.

Failures / Blockers:
- First smoke run failed before writing files because Git emitted the global-ignore permission warning during `git status --short`.
- Second smoke run failed in the sandbox because `.codex/state` has a deny-write ACL for the sandbox identity.
- Escalated local PowerShell run succeeded.

Verification / Tests:
- PowerShell parser check passed for `scripts/codex-handoff.ps1`.
- Smoke run wrote `.codex/state/HANDOFF_20260507_085043.md`.
- Smoke run wrote `.codex/state/MONDAY_UPDATE.md` with `[TECHNICAL]` and `[SUMMARY]` sections.
- Smoke files were removed after verification.

Matching Repo Update Status:
- Project Nexus does not require a contract change for this script hardening because Nexus packet closure remains monitor-owned. Project Nexus tracker records awareness only.

## Entry 4 - Sprint 11.2 Path Ambiguity Verification

Date: 2026-05-07

Change:
- Verified the `project_nexus/` parent-folder ambiguity is already resolved on disk.
- Clarified the parent `STALE.md` file with the absolute live clone path.

Concept:
- Agents must never work from `C:\Users\OriShavit\Documents\GitHub\project_nexus` directly.
- The live Project Nexus git clone is `C:\Users\OriShavit\Documents\GitHub\project_nexus\project-nexus`.

Implementation:
- Confirmed `C:\Users\OriShavit\Documents\GitHub\project_nexus\STALE.md` exists.
- Confirmed `agents/kb/legion-swarm.md` warns that the parent folder is stale.
- Confirmed `~/.claude/memory/legion-swarm.md` records the canonical nested path.
- Updated parent `STALE.md` wording for clarity. The parent folder is not the live git repo, so this is a workstation file update, not a repo commit.

Methodology Impact:
- Any future Nexus work must target the nested clone.
- Any document or TaskSpec that points to `project_nexus/` without `project-nexus/` is suspect until verified.

Failures / Blockers:
- None.

Verification / Tests:
- `Test-Path C:\Users\OriShavit\Documents\GitHub\project_nexus\STALE.md` returned true.
- `rg` confirmed Legion KB has the stale-parent warning.
- `Select-String` confirmed Claude memory has the canonical nested path.

Matching Repo Update Status:
- Complete locally: Nexus live repo does not require a contract change because its own path is already the canonical target.

## Entry 5 - Sprint 11.3-11.6 Contract Audit

Date: 2026-05-07

Change:
- Audited the remaining Sprint 11 runtime-hardening contract surfaces.
- Fixed the last `.codex/sprints` contradiction in `C:\Users\OriShavit\.claude\docs\legion-dispatch.md`.

Concept:
- Claude dispatch, Codex runtime instructions, and Legion ownership documentation must agree before any live dispatch depends on them.

Implementation:
- Confirmed `docs/ownership-map.md` declares the Monday split: Legion writes Monday for Legion-driven items; Nexus Monitor writes Monday for Nexus packets; never both.
- Confirmed `agents/codex.md` uses `docs/sprints/YYYY-MM-DD-[repo]-sprint-NN-[slug].md` as the sprint convention.
- Confirmed `scripts/codex-watchdog-check.ps1` exists and parses.
- Confirmed `agents/codex.md` Step 0 and Step 7 call the watchdog check.
- Confirmed `~/.claude/CLAUDE.md` references `legion-swarm/docs/ownership-map.md`.
- Updated `~/.claude/docs/legion-dispatch.md` TaskSpec template to use `docs/sprints/...` instead of `.codex/sprints/...`.

Methodology Impact:
- Sprint files now have one canonical location: `docs/sprints/` in the target repo root.
- Claude-side dispatch now expects `MONDAY_UPDATE.md` after every `LEGION_COMPLETE`.

Failures / Blockers:
- None after the TaskSpec template contradiction was corrected.

Verification / Tests:
- `rg` confirmed no active dispatch contract still tells Claude to create sprint files under `.codex/sprints`.
- PowerShell parser check passed for `scripts/codex-watchdog-check.ps1`.
- `git diff --check` passed for the `.claude` dispatch doc; only line-ending warnings were reported.

Matching Repo Update Status:
- Complete locally: this was a Claude/Legion dispatch-contract correction; Project Nexus packet and monitor contracts did not change.

## Entry 6 - Nexus Local Proof Readiness Awareness

Date: 2026-05-07

Change:
- Project Nexus local verification passed after rerunning pytest outside sandbox ACL constraints.

Concept:
- Legion can dispatch Nexus packet proof only after Nexus local monitor/startup/test readiness is green.

Implementation:
- No Legion contract changed.
- This tracker records the Nexus verification state so Legion does not infer readiness from chat-only context.

Methodology Impact:
- The next Legion/Nexus proof should be a controlled local no-external proof before any Monday/Google Chat posting.
- Monday closure remains a live external risk because Nexus self-test saw Monday 500 errors even though monitor verification passed.

Failures / Blockers:
- Pytest under sandbox failed due temp/cache ACL denial.
- Nexus `monitor\self_test.py` attempted Monday updates and received Monday internal server errors.

Verification / Tests:
- Nexus py_compile passed for monitor modules.
- Nexus startup check passed.
- Nexus monitor self-test passed locally but logged Monday 500 errors.
- Nexus pytest passed 19/19 outside sandbox with `-p no:cacheprovider`.

Matching Repo Update Status:
- Complete locally: Project Nexus tracker records the full command evidence.

## Entry 7 - Local No-External Legion-to-Nexus Proof

Date: 2026-05-08

Change:
- Project Nexus added and ran `scripts/local_no_external_proof.py`.

Concept:
- Legion can now ask Nexus for a local no-external proof before escalating to any live Monday or Google Chat proof.

Implementation:
- Nexus script creates an isolated harness under `.agent-harness/local-proof/`.
- It runs packet parsing, task-loop verification, monitor startup checks, monitor outbox scan, countersignature, and Monday skip behavior.

Methodology Impact:
- The next live proof should start from this local proof baseline.
- Monday and Google Chat remain Safe YOLO outbound-communication gates and require explicit approval before use.

Failures / Blockers:
- First script run failed due missing repo root on Python import path; fixed in Nexus script.

Verification / Tests:
- Nexus `python -m py_compile scripts\local_no_external_proof.py`: passed.
- Nexus `python scripts\local_no_external_proof.py`: passed.
- Proof task ID: `T-20260508-local-legion-nexus-proof-20260508_144742`.
- Proof events: `startup_scan`, `verification_started`, `verification_passed`, `monday_skipped`.
- Nexus result contains `NEXUS_VERIFICATION: PASSED`.

Matching Repo Update Status:
- Complete locally: Project Nexus tracker records the script, proof evidence, and generated proof report path.
