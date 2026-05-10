# Project Nexus - Codex KB

> Codex reads this file once at session start when Legion dispatches work for Project Nexus.
> Keep this file aligned with the live Project Nexus clone, not the stale parent folder.

## Canonical Paths

- Live repo: `C:/Users/OriShavit/Documents/GitHub/project_nexus/project-nexus`
- Stale parent marker: `C:/Users/OriShavit/Documents/GitHub/project_nexus/STALE.md`
- Legion tracker: `C:/Users/OriShavit/Documents/GitHub/legion-swarm/docs/tracking/2026-05-06-legion-nexus-sync-tracker.md`
- Nexus tracker: `C:/Users/OriShavit/Documents/GitHub/project_nexus/project-nexus/docs/tracking/2026-05-06-nexus-legion-sync-tracker.md`
- Vault playbooks: `C:/Users/OriShavit/Documents/legion-vault/30_Playbooks/Nexus`

Do not work from `C:/Users/OriShavit/Documents/GitHub/project_nexus` directly. It is a parent container/stale snapshot area; the git clone is the nested `project-nexus` folder.

## What This Repo Does

Project Nexus is the local execution and verification harness for agent task packets. It receives task packets, constrains scope, verifies result files through the monitor, writes countersignatures, and owns Monday closure for Nexus packets only.

## Stack

- Runtime: Python 3.x
- Framework: none; mostly stdlib plus `watchdog`, `pyyaml`, and `pytest`
- Test runner: `pytest`
- Active harness root: `.agent-harness/`
- Monitor log: `.agent-harness/logs/monitor.ndjson`

## Repo Layout

```text
.agent-harness/config/          Packet, result, review, and manifest contracts.
.agent-harness/inbox/           Task packets.
.agent-harness/outbox/          Agent result files for monitor review.
.agent-harness/artifacts/       Verification artifacts per task.
.agent-harness/logs/            Monitor and task-loop logs.
monitor/monitor.py              Verification monitor and Monday skip/write path.
monitor/task_loop.py            Worker-side task packet execution loop.
scripts/local_no_external_proof.py
                                 Safe local packet proof with no external writes.
docs/contracts/                 Legion/Nexus baseline contracts.
docs/runbooks/                  End-to-end runbooks.
docs/tracking/                  Nexus-side cross-system tracker.
```

## Operating Rules

- Read `CLAUDE.md`, the relevant task packet, and `docs/contracts/legion-nexus-baseline.md` before changing Nexus behavior.
- Keep Nexus and Legion tracker entries paired when changing paths, methodology, execution plans, proof flows, or ownership rules.
- Do not let both Legion and Nexus write the same Monday item. Legion owns Legion-task Monday updates; Nexus monitor owns Nexus-packet Monday closure.
- Under Safe YOLO, local proof, local tests, local commits, and local documentation updates are allowed. Pushes, live Monday posts, and Google Chat posts remain explicit approval gates.
- Treat generated proof artifacts under `.agent-harness/local-proof/` as runtime evidence, not commit material.

## Known Issues / Gotchas

- The parent `project_nexus` path is ambiguous and must be treated as stale unless the path includes `project-nexus`.
- Old pytest temp directories may be unreadable because of prior Windows ACL failures. Do not treat those as current test failures.
- Git may warn that `C:/Users/OriShavit/.config/git/ignore` is unreadable. This is workstation-level friction, not a Nexus code failure.
- If Monday credentials are absent, the monitor should record `monday_skipped`; preserve the intended update text instead of claiming a live write.

## Key Commands

Run from `C:/Users/OriShavit/Documents/GitHub/project_nexus/project-nexus`:

```powershell
python -m py_compile monitor\monitor.py monitor\task_loop.py scripts\local_no_external_proof.py
python monitor\monitor.py --startup-check
python monitor\self_test.py
python scripts\local_no_external_proof.py
```

Use `python scripts\local_no_external_proof.py` before any live Monday or Google Chat proof. It creates an isolated harness under `.agent-harness/local-proof/`, runs packet parsing, task-loop verification, monitor startup checks, countersignature, and verifies `monday_skipped`.

## Current Proof Baseline

- Latest local proof command: `python scripts\local_no_external_proof.py`
- Latest proof task ID: `T-20260508-local-legion-nexus-proof-20260508_144742`
- Expected proof events: `startup_scan`, `verification_started`, `verification_passed`, `monday_skipped`
- Expected countersignature: `NEXUS_VERIFICATION: PASSED`

## Stop Conditions

- The task packet conflicts with `CLAUDE.md` or the baseline contract.
- A change would write to the stale parent path.
- A live Monday/Google Chat write is required but not explicitly approved.
- Tests fail twice for the same unclear reason.
- Unrelated dirty files make the requested change unsafe to isolate.
