# Codex Integration — Execution Plan (Sprints 11 + 12)

> **Date:** 2026-05-05
> **Status:** Proposal awaiting Claude/Legion review.
> **Companion review:** `docs/plans/2026-05-05-codex-integration-review.md`
> **Do not begin implementation until Claude approves this plan, dispatches each sprint as a packet trail, or converts it into sprint files.**

This plan addresses the gaps (G1–G7) and risks (R1–R6) identified in the companion review file. It assumes Sprint 08 (Nerve Center v1) continues independently on its own packet trail; Sprints 11 and 12 here run **after** Sprint 08 closes (or in parallel only if Claude explicitly approves it).

---

## Roles and Ownership (applies to all tasks below)

| Concern | Owner |
|---|---|
| Build TaskSpec, dispatch, retries, swarm-state writes, Legion-task Monday updates | **Claude/Legion** (sole writer of `~/.claude/swarm-state.json`; Monday for Legion items) |
| Repo-local execution, `.codex/state/*` writes (LAST_RUN, DIALOGUE, TURN, HANDOFF_*, MONDAY_UPDATE), task status flips in sprint files | **Codex** |
| Nexus packet verification (countersignature) and Monday Done/Stuck for **Nexus** packets only | **Monitor** (`project_nexus/project-nexus/monitor/monitor.py`) |
| Vault project page refresh (`legion-wiki/projects/<repo>/index.md`) | **Mapper** agent, dispatched by Legion |

Hard rule (proposed, to be ratified in Sprint 11 Task 1): **Legion writes Monday for Legion-driven tasks. Monitor writes Monday for Nexus packets. Both never write the same item.**

---

## Sprint 11 — Codex Runtime Hardening

### Goal

Lock down the Codex ↔ Legion ↔ Nexus seam so that the next live dispatch cannot drift into a stale tree, lose a Monday update, or run past the API budget. No new features — only contract tightening.

### Sequencing Rule

Tasks 11.1 → 11.2 → 11.3 → 11.4 → 11.5 → 11.6 in strict order. Each task has its own packet, branch, and verification. Dependent tasks remain `blocked` until the previous is countersigned, then Legion resets the next to `pending`.

### Task 11.1 — Land the `MONDAY_UPDATE.md` patch

**Owner:** Codex (commit), Claude/Legion (review + Monday post-test).

**Files:**
- Commit `agents/codex.md` (already modified) and any companion script changes.
- Confirm `scripts/codex-handoff.ps1` writes both `HANDOFF_[ts].md` and `MONDAY_UPDATE.md` with the `[TECHNICAL]` and `[SUMMARY]` sections.

**Acceptance criteria:**
- [ ] `scripts/codex-handoff.ps1` is tracked and committed.
- [ ] `git status --short` no longer lists handoff-script or Codex-agent-contract changes as untracked or modified after the commit.
- [ ] Smoke-test `MONDAY_UPDATE.md` and `HANDOFF_*.md` outputs are removed after verification so Legion cannot post test text accidentally.
- [ ] `scripts/codex-handoff.ps1 -TaskId TEST -Status passed -Technical "x" -Summary "y"` (run in a scratch dir) produces both files with the documented headers.
- [ ] Commit message follows existing style: `chore(codex): commit MONDAY_UPDATE.md generation patch`.

**Verification:**
```powershell
git diff --stat HEAD~1 HEAD agents/codex.md scripts/codex-handoff.ps1
.\scripts\codex-handoff.ps1 -TaskId smoke -Status passed -Technical "smoke test" -Summary "smoke test"
Get-Content .codex\state\MONDAY_UPDATE.md
```

**Addresses:** G6, R5.

---

### Task 11.2 — Resolve `project_nexus` path ambiguity

**Owner:** Mapper (research + write decision), Claude/Legion (countersign).

**Decision required:** Pick **one** of:
1. Adopt `project_nexus/project-nexus/` as the canonical path; mark the parent flat copy as deprecated and add a top-level `project_nexus/STALE.md` pointing at the nested clone.
2. Flatten by deleting the parent's stale duplicates of files that exist in the nested clone (only after a per-file diff confirms identity or a justified merge).

**Files (option 1 — recommended, less destructive):**
- Create `project_nexus/STALE.md` with: "This folder is a stale snapshot. The live Nexus clone is `project_nexus/project-nexus/`. Do not edit files here."
- Update `agents/kb/legion-swarm.md` "Known Issues / Gotchas" with a one-line warning.
- Update `~/.claude/memory/legion-swarm.md` "Codex Integration" section with the canonical path.

**Acceptance criteria:**
- [ ] Canonical path is documented in exactly one place per consumer (KB, memory, Nerve Center config).
- [ ] `STALE.md` lands in `project_nexus/` (or deletion plan is executed under option 2 with mapper countersignature).
- [ ] Grep for `project_nexus/` (without the nested suffix) across `legion-swarm/` and `~/.claude/` returns no consumer-facing references that resolve to the parent stale tree.

**Verification:**
```powershell
Get-Content C:\Users\OriShavit\Documents\GitHub\project_nexus\STALE.md
# rg -n "project_nexus[/\\](?!project-nexus)" -- legion-swarm and ~/.claude
```

**Addresses:** G2, R1.

---

### Task 11.3 — Single ownership map page

**Owner:** Documenter (write), Claude/Legion (countersign), Mapper (link from vault).

**Goal:** One page that says, in 1 screen, who writes what and where the contracts live. This becomes the canonical answer to G4 ("who writes Monday").

**Files:**
- Create `docs/ownership-map.md` covering: TaskSpec + dispatch (Legion); swarm-state.json (Legion sole writer); Monday for Legion tasks (Legion, one write per task); `.codex/state/*` per repo (Codex); Nexus packet verification + Monday for Nexus packets (Monitor); vault project pages (Mapper); watchdog STOP sentinel (Claude hook today; Codex addressed in Task 11.4).
- Reference this page from `~/.claude/CLAUDE.md` ("Reference Files" table) — do **not** rewrite that table here; this task only lands the page.

**Acceptance criteria:**
- [ ] `docs/ownership-map.md` exists and lists every concern from the §2.3 table in the review.
- [ ] Page declares the rule: "Legion writes Monday for Legion-driven items. Monitor writes Monday for Nexus packets. Never both for the same item."
- [ ] No edits to `~/.claude/CLAUDE.md` in this task — that lands as the final pointer in Task 11.6.

**Verification:** human review — Claude reads the page and either approves or returns line-numbered comments.

**Addresses:** G4.

---

### Task 11.4 — Codex process-level watchdog

**Owner:** Coder/Codex (build), Tester (verify), Claude/Legion (review).

**Problem:** `~/.claude/hooks/context-watchdog.js` only sees Claude. If Claude posts STOP, Codex keeps spending.

**Approach:** Codex reads `.watchdog/STOP` (per repo) at the top of each step in its 9-step session protocol. If present, it stops cleanly: writes BLOCKED, runs `codex-handoff.ps1` with `-Status blocked -Technical "watchdog STOP detected" -Summary "Paused — system-wide usage limit reached"`, emits `LEGION_COMPLETE: status=blocked verification=pending notes="watchdog STOP"`, exits.

**Files:**
- Update `agents/codex.md` Step 0 (new): "Check `.watchdog/STOP`. If present, immediately BLOCKED-stop." Insert before Step 1 (KB read).
- Update `agents/codex.md` Steps 5, 8, 9 with a one-line "re-check `.watchdog/STOP`" reminder.
- Add `scripts/codex-watchdog-check.ps1` returning exit code 0 when no STOP, 1 when STOP, with stdout describing the action Codex must take.
- Update `skills/watchdog/SKILL.md` "Responding to STOP Sentinel" table to include Codex as a sentinel reader.

**Acceptance criteria:**
- [ ] `scripts/codex-watchdog-check.ps1` exists and is referenced from `agents/codex.md` Step 0.
- [ ] Smoke test: create `.watchdog/STOP` in a scratch repo, run the check, confirm exit code 1 and the documented message.
- [ ] Smoke test: remove the file, re-run, confirm exit code 0.

**Verification:**
```powershell
New-Item -ItemType Directory -Path .watchdog -Force | Out-Null
"system-wide usage limit reached" | Out-File .watchdog\STOP
.\scripts\codex-watchdog-check.ps1; $LASTEXITCODE
Remove-Item .watchdog\STOP
.\scripts\codex-watchdog-check.ps1; $LASTEXITCODE
```

**Addresses:** G3, R3.

---

### Task 11.5 — Sprint-file location convention

**Owner:** Documenter (write), Claude/Legion (decide + countersign).

**Decision:** Adopt `docs/sprints/` as canonical. Update `~/.claude/docs/legion-dispatch.md` Pre-Dispatch Checklist line 27 to match. `.codex/sprints/` is removed from any reference.

**Files:**
- Update `~/.claude/docs/legion-dispatch.md` (Claude-side, requires Shepard-Commander unblock if self-modification gate fires per memory note).
- Update `agents/codex.md` Step 4 to phrase the rule explicitly: "Sprint file path is provided in the TaskSpec under `sprint_file`. Convention: `docs/sprints/YYYY-MM-DD-<repo>-sprint-NN-<slug>.md`."

**Acceptance criteria:**
- [ ] `~/.claude/docs/legion-dispatch.md` no longer references `.codex/sprints/`.
- [ ] `agents/codex.md` Step 4 reads as above.
- [ ] `agents/kb/KB-TEMPLATE.md` is updated if it referenced the old path (it currently does not — confirm no-op or update accordingly).

**Verification:** `rg -n "\.codex/sprints" -- ~/.claude legion-swarm` returns no hits.

**Addresses:** G5, R6.

---

### Task 11.6 — Wire the new ownership map into the Reference Files table

**Owner:** Documenter (write), Claude/Legion (manual paste if self-modification gate fires).

**Files:**
- Add a single row to `~/.claude/CLAUDE.md` "Reference Files" table:
  | Topic | File |
  |---|---|
  | Ownership map (who writes what, where) | `legion-swarm/docs/ownership-map.md` |

**Acceptance criteria:**
- [ ] Row appears under "Reference Files" exactly once.
- [ ] No other edits to `~/.claude/CLAUDE.md`.

**Verification:** `rg -n "ownership-map" -- ~/.claude/CLAUDE.md` returns the new line.

**Addresses:** G4, R4 (closes the loop opened in 11.3).

---

### Sprint 11 Done Criteria

- [ ] All 6 tasks countersigned in order.
- [ ] No regression on Sprint 08 (Nerve Center v1) — its packet trail is untouched.
- [ ] `~/.claude/swarm-state.json` shows 6 tasks with `verification: passed`.
- [ ] No outstanding `BLOCKED` for these tasks.

---

## Sprint 12 — End-to-End Proof

### Goal

One small, complete loop closes — *with* the Sprint 11 hardening in place — so we can certify the contract works rather than just describing it.

### Sequencing Rule

12.1 → 12.2 → 12.3 → 12.4 → 12.5. The proof is invalidated if any task is reordered.

### Task 12.1 — Pick a no-op proof task

**Owner:** Claude/Legion.

**Goal:** Choose the minimum task that exercises the full pipeline without changing product code. Recommended candidate: append a one-line entry to `legion-swarm/CHANGELOG.md` ("Sprint 12 proof") on a dedicated branch.

**Acceptance criteria:**
- [ ] Task fits in a single commit, no code changes outside CHANGELOG.
- [ ] Task has explicit AC and a verification command (e.g. `git log --oneline -1` matches expected message).
- [ ] TaskSpec is written and acceptance_criteria are listed.

---

### Task 12.2 — Dispatch with full contract

**Owner:** Claude/Legion (dispatch), Codex (execute).

**Goal:** Run the canonical dispatch loop end-to-end:
1. Pre-Dispatch Checklist (per dispatch doc).
2. Write TaskSpec to `~/.claude/swarm-state.json` with `status: active`.
3. Spawn Codex subagent.
4. Codex Steps 1–9 including watchdog check (Task 11.4).
5. Codex emits `LEGION_COMPLETE: status=passed`.
6. Legion reads `.codex/state/MONDAY_UPDATE.md` and posts to the Monday item.
7. Legion updates swarm-state with `completed_at`, `dispatch_to_verified_ms`, `verification: passed`.

**Acceptance criteria:**
- [ ] Each numbered step above leaves a verifiable artifact (state file, commit, Monday update id, swarm-state row).
- [ ] `MONDAY_UPDATE.md` contains both `[TECHNICAL]` and `[SUMMARY]` blocks per the contract.

---

### Task 12.3 — Monitor verification on a Nexus packet (parallel proof)

**Owner:** Monitor + Claude/Legion (operator).

**Goal:** Same shape as 12.2, but using a `project_nexus/project-nexus/.agent-harness/inbox/` packet to prove the **monitor** path also closes correctly without colliding with Legion's Monday writes.

**Acceptance criteria:**
- [ ] A small Nexus task packet runs end-to-end: inbox → execution → outbox + artifact + countersignature.
- [ ] Monitor posts the Done/Stuck status to the **Nexus** Monday item.
- [ ] Legion does not write to that Nexus item (proves the ownership rule from Task 11.3).

---

### Task 12.4 — Mapper refreshes vault project pages

**Owner:** Mapper, Claude/Legion (countersign).

**Goal:** With the live state from 12.2 + 12.3, dispatch the Mapper to refresh:
- `legion-wiki/projects/legion-swarm/index.md` (clear stale "Mac port" current sprint, set actual current sprint).
- `legion-wiki/projects/project_nexus/index.md` (correct "no local clone yet" claim, set the canonical path from Task 11.2).

**Acceptance criteria:**
- [ ] Both pages show `updated: 2026-05-05` (or later if 12.4 runs on a later date).
- [ ] Both pages reflect the current sprint and canonical paths.
- [ ] No vault writes happened before this task — earlier tasks honored the "do not edit vault directly" rule.

---

### Task 12.5 — Sprint summary

**Owner:** Claude/Legion.

**Goal:** Generate the Sprint Summary Report from `~/.claude/docs/legion-workflow.md` "Sprint Summary Report" template, drawing from `swarm-state.json` for Sprint 11 + Sprint 12 tasks combined. Post once to Shepard-Commander via Google Chat per dispatch doc.

**Acceptance criteria:**
- [ ] Report includes per-role `dispatch_to_verified_ms` averages.
- [ ] Verification failures, if any, are listed with their `notes`.
- [ ] One Google Chat ping is sent on completion (Status: DONE).

---

### Sprint 12 Done Criteria

- [ ] One Legion task and one Nexus packet have closed end-to-end with no protocol violations logged in swarm-state.
- [ ] Vault project pages are current.
- [ ] No Monday item received writes from both Legion and Monitor.
- [ ] Sprint summary posted.

---

## Out of Scope for Sprints 11 + 12

- Removing the stale `project_nexus/` parent tree by deletion (defer until at least one full sprint cycle confirms STALE.md + KB warnings are sufficient).
- New features in `legion/` (Nerve Center) — that lives in Sprint 08 and any future Sprint 09/10 packet trails.
- Cross-machine watchdog or Codex-to-Codex dialogue. Codex remains repo-scoped.
- Changing the Monday board schema or column ids.

## Verification (this plan)

- [ ] `docs/plans/2026-05-05-codex-integration-execution-plan.md` exists.
- [ ] Title and date present in H1 + frontmatter quote.
- [ ] Two sprints with explicit task list, AC, ownership, and verification.
- [ ] Each task names exactly one owner.
- [ ] No vault edits performed by writing this plan.
- [ ] No Monday writes performed by writing this plan.
- [ ] No commits created by writing this plan.
