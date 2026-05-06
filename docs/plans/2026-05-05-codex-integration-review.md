# Codex Integration — Review (Evidence Packet)

> **Date:** 2026-05-05
> **Author:** Recon pass; not yet countersigned by Legion.
> **Companion plan:** `docs/plans/2026-05-05-codex-integration-execution-plan.md`
> **Status of this file:** For Claude/Legion review. **Do not act on Sprint 11/12 yet.**

This document is a focused evidence packet for the Codex ↔ Legion ↔ Nexus seam — what is actually wired, what is loose, and where the system is silently lying to us. It is *not* a Sprint 08 audit; Sprint 08 (Nerve Center v1) has its own packet trail in `docs/plans/2026-05-05-legion-nerve-center.md` and `docs/plans/2026-05-05-legion-nerve-center-operative.md`.

---

## 1. Locations Reviewed

| Location | What it is | What we read |
|---|---|---|
| `~/.claude/` (global) | Claude Code user dotfiles + Legion identity | `CLAUDE.md`, `docs/legion-{dispatch,workflow,intelligence,invariants}.md`, `swarm-state.json`, `memory/legion-swarm.md`, `hooks/context-watchdog.js` |
| `legion-swarm/.codex/` | Repo-local Codex runtime | `config.toml`, `state/{TASK_STATE,LAST_RUN,DECISIONS}.md` |
| `legion-swarm/agents/` | Agent identity + KB files | `codex.md`, `kb/{KB-TEMPLATE,legion-swarm,helm-dashboard}.md` |
| `legion-swarm/scripts/` | Codex IPC shell | `codex-handoff.ps1`, `codex-dialogue-check.ps1`, `claude-dialogue-log.ps1`, `sync-vault-hard-truths.ps1` |
| `legion-swarm/docs/` | Plans, sprints, dialogue spec | `dialogue-format.md`, `sprints/2026-05-05-legion-swarm-sprint-08-nerve-center-v1.md`, `plans/2026-05-05-legion-nerve-center*.md` |
| `project_nexus/` (parent) + `project_nexus/project-nexus/` (nested) | Nexus methodology + monitor harness | `CLAUDE.md`, `monitor/`, `.agent-harness/`, sprints, sessions |
| Obsidian vault | Cross-repo wiki + skills | `legion-vault/projects/{legion-swarm,project_nexus,...}/index.md`, `legion-vault/system/skills/{wiki-ingest,wiki-query,wiki-lint}.md` |

The user's prompt referenced `C:\Users\OriShavit\Documents\legion-vault\system\skills`; that path exists on this machine and is the local vault skill source read by this review. Older `legion-wiki` references in Legion Swarm docs should be treated as stale path language unless a specific task deliberately targets the older/shared-drive vault.

## 2. Discoveries (Ground Truth)

### 2.1 `project_nexus/` parent folder is stale; the nested `project_nexus/project-nexus/` is the live repo

```
project_nexus/               ← stale flat copy (no .git/)
  CLAUDE.md, AGENTS.md, CHANGELOG.md, TODO.md
  monitor/, docs/, .agent-harness/, sessions/, memory/
project_nexus/project-nexus/ ← live clone
  .git/, monitor/, docs/, .agent-harness/, ...
```

Both trees contain the **same filenames and largely the same content**. The vault project page (`legion-wiki/projects/project_nexus/index.md`, `updated: 2026-04-28`) still says *"no local GitHub clone yet"* — that is no longer true. The nested `project-nexus/` has `.git/` plus active artifacts (e.g. `.agent-harness/inbox/T-20260504-vault-loop-guide.md`, `.agent-harness/logs/task_loop.ndjson`, `.agent-harness/state/task_loop.json`).

**Risk:** any tool, doc, or KB that points at `C:/Users/OriShavit/Documents/GitHub/project_nexus/...` instead of `.../project_nexus/project-nexus/...` is operating on a stale snapshot. The legion Nerve Center plan (`docs/plans/2026-05-05-legion-nerve-center.md`, line 49) hard-codes the deeper path correctly: `"claude_state_file": "C:/Users/OriShavit/Documents/GitHub/project_nexus/project-nexus/legion/state/claude.json"`. Other consumers may not.

### 2.2 Vault project pages are stale summaries, not live truth

| Vault page | `updated:` | Claim that is now wrong |
|---|---|---|
| `projects/project_nexus/index.md` | 2026-04-28 | "No local GitHub clone yet" — clone exists at the nested path. |
| `projects/legion-swarm/index.md` | 2026-04-28 | "Current Sprint = Mac port" — actual current sprint is Sprint 08 Nerve Center v1 (file dated 2026-05-05). |

`scripts/sync-vault-hard-truths.ps1` only syncs `~/.claude/{CLAUDE,CHANGELOG,TODO}.md` and `~/.claude/memory/*.md` into `legion-wiki/03-hard-truths/`. It does **not** touch `legion-wiki/projects/*/index.md`. The mapper agent is the named writer for project pages, but there is no scheduled mapper run. Result: project pages drift silently.

### 2.3 Ownership map (as wired today)

| Concern | Owner | Where it's enforced |
|---|---|---|
| TaskSpec construction, dispatch, retries | Claude/Legion | `~/.claude/CLAUDE.md`, `docs/legion-dispatch.md` |
| `~/.claude/swarm-state.json` (timing ledger) | Claude/Legion (sole writer) | `docs/legion-dispatch.md` step 4/8; `memory/legion-swarm.md` "Sprint 08" section |
| Monday item updates for *Legion* tasks | Claude/Legion | `docs/legion-dispatch.md` "Monday Update Protocol"; one write per task on done |
| Repo-local execution + `.codex/state/` writes | Codex | `agents/codex.md` Steps 1–9 |
| `.codex/state/{TASK_STATE,DECISIONS}.md` (Legion-authored side) | Claude/Legion | Codex KB tables + dispatch checklist |
| `.codex/state/{LAST_RUN,DIALOGUE,TURN,HANDOFF_*,MONDAY_UPDATE}.md` | Codex | `agents/codex.md`, `scripts/codex-handoff.ps1` |
| Nexus packet verification (countersignature) + Monday Done/Stuck for Nexus tasks | Nexus monitor | `project_nexus/project-nexus/monitor/monitor.py`, `docs/specs/nexus-spec-v1.md` |
| Watchdog (context + usage) | Claude global hook + per-agent skill | `~/.claude/hooks/context-watchdog.js`, `legion-swarm/skills/watchdog/SKILL.md` |

### 2.4 Codex watchdog is still Claude-derived

`~/.claude/hooks/context-watchdog.js` is a **Claude Code Stop hook**. It reads the Claude session transcript and computes Claude context-window usage. Codex CLI is a separate process and does not feed this hook.

`legion-swarm/skills/watchdog/SKILL.md` describes a watchdog *subagent* launched at session start. The "STOP sentinel" pattern is referenced as `.watchdog/STOP`, intended to be observed by every agent's `PostToolUse` hook. In practice today, only Claude has the Stop hook implementation; the Codex side has no equivalent process-level watchdog and no `.watchdog/STOP` reader.

**Practical effect:** if API usage hits 95% mid-Codex-session, Claude's watchdog will write the sentinel, but Codex will keep running until its own loop ends. This is a real, currently-live gap.

### 2.5 Legion handoff script was missing `MONDAY_UPDATE.md` generation — now patched locally

The user reports this was fixed in the working copy. We confirmed `scripts/codex-handoff.ps1` (lines 92–103) now writes both `HANDOFF_[ts].md` and `MONDAY_UPDATE.md` with `[TECHNICAL]` and `[SUMMARY]` sections matching the contract in `~/.claude/docs/legion-dispatch.md` "Monday Update Protocol" (line 92+). `agents/codex.md` Step 9 also wires `-Technical` and `-Summary` parameters into the call.

This patch is **uncommitted** at the time of writing. Current working-tree evidence shows the handoff script under the untracked `scripts/` directory and repo-local `.codex/state` artifacts are also untracked. Before any new sprint relies on `MONDAY_UPDATE.md`, the script and matching docs need to land and smoke-test handoff outputs must be removed or marked test-only.

### 2.6 Sprint location convention is split

Two locations are referenced in shipping documents:

- `~/.claude/docs/legion-dispatch.md` (Pre-Dispatch Checklist, line 27): `[repo_path]/.codex/sprints/SPRINT_NNN.md`
- All actual sprint files live at `docs/sprints/...`. The active one is `docs/sprints/2026-05-05-legion-swarm-sprint-08-nerve-center-v1.md`, and `agents/codex.md` Step 4 says "the active sprint file path is specified in the TaskSpec under `sprint_file`" — i.e. it punts the convention to the TaskSpec.

There is no `.codex/sprints/` directory in this repo. Either the dispatch reference is aspirational and should be aligned with `docs/sprints/`, or sprint files should be mirrored. Today, neither is true.

## 3. What Works

- **Identity + KB chain:** `agents/codex.md` ←→ `agents/kb/{repo}.md` ←→ Obsidian project page reference. Codex KBs for `legion-swarm` and `helm-dashboard` are present and coherent. KB-TEMPLATE is current.
- **Codex Step protocol (1–9):** matches the dispatch contract Claude uses. BLOCKED protocol is well-specified end-to-end.
- **`codex-handoff.ps1` (post-patch):** writes both files, matches the [TECHNICAL]/[SUMMARY] format Claude/Legion expects.
- **Dialogue protocol:** `docs/dialogue-format.md` + `scripts/codex-dialogue-check.ps1` + `scripts/claude-dialogue-log.ps1` form a consistent triangle. `TURN.md` ownership rules are unambiguous.
- **swarm-state.json schema:** valid JSON, documented `_schema` block, sole-writer rule is enforced by dispatch doc.
- **Sprint 08 packet trail (Nerve Center v1):** plan, sprint file, operative handoff, KB, and Codex task string are all aligned. Task 1 has been physically launched (terminal `coder-1777980950822`, `pending` sign-in per operative file).
- **Nexus harness contracts:** `task_packet.md`, `result.md`, `review.md`, `manifest/schema.yaml` exist in both `project_nexus/.agent-harness/config/` trees. Monitor `task_loop.py` + `monitor.py` plus `tests/test_task_loop.py` exist and target the live `.agent-harness/{inbox,outbox,artifacts,logs,state}/`.

## 4. What Is Missing or Loose

| # | Gap | Evidence |
|---|---|---|
| G1 | Vault project pages drift silently — no scheduled mapper / sync. | `sync-vault-hard-truths.ps1` only handles hard truths; project pages last touched 2026-04-28 with claims that are now wrong. |
| G2 | No automated detection of the `project_nexus/` vs `project_nexus/project-nexus/` ambiguity. Any consumer can pick the wrong path. | Both trees coexist on disk; only Nerve Center plan resolves it explicitly. |
| G3 | Codex has no process-level watchdog. STOP sentinel is Claude-only. | `~/.claude/hooks/context-watchdog.js` is a Claude Stop hook; Codex CLI does not invoke it. |
| G4 | Monitor → Monday closure for **Nexus** packets is not described in `~/.claude/docs/legion-dispatch.md`. The dispatch doc only covers Legion-task Monday writes. | Monitor closure rules live only in `project_nexus/project-nexus/docs/specs/nexus-spec-v1.md`. There is no single page that declares "Legion writes Monday for Legion tasks; Monitor writes Monday for Nexus packets — never both." |
| G5 | `.codex/sprints/` vs `docs/sprints/` convention is unresolved. Pre-Dispatch Checklist references the former; reality uses the latter. | See §2.6. |
| G6 | `MONDAY_UPDATE.md` generation patch is uncommitted. | `git status` shows the working tree contains the change but it is not yet in any commit. |
| G7 | No end-to-end "proof" run that exercises: Legion dispatch → Codex execution → `MONDAY_UPDATE.md` → Monday post → swarm-state ledger update → mapper refresh of vault project page, in a single pass with a small no-op task. | Sprint 08 is mid-flight on Task 1 with `signInStatus: pending`; we have not observed a complete loop close. |

## 5. Friction Points

- **`sprint_file` path is per-TaskSpec** but Pre-Dispatch Checklist also asserts a default location. New repos onboarding Codex have to decide which convention to follow with no canonical answer.
- **Two sources of truth for "what Codex does"** — `~/.claude/CLAUDE.md` + `~/.claude/docs/legion-dispatch.md` (Claude-side) and `legion-swarm/agents/codex.md` (Codex-side). They are aligned today, but every change to one has to be mirrored manually. There is no test that asserts they remain in sync.
- **"Heredoc / git commit" classifier issue** documented in `memory/legion-swarm.md` ("Permission Gate Issue 2026-05-03/04") — not a Codex problem per se, but it intermittently blocks the commit step in Step 9 of the protocol. Workaround is documented; root fix is pending.
- **Dialogue + Monday log requires `MONDAY_API_TOKEN`** — `scripts/claude-dialogue-log.ps1` falls back gracefully when missing (logs to stdout) but the operator cannot tell from `DIALOGUE.md` alone whether Monday saw the message.

## 6. Risks

| ID | Risk | Likelihood | Impact |
|---|---|---|---|
| R1 | A future agent reads stale `project_nexus/` parent and writes work that the live `.git/` clone never sees. | Medium | High — silent divergence; Nexus monitor would countersign nothing, swarm-state would show timing for work that does not exist on the actual branch. |
| R2 | Vault project page goes ~6+ weeks without refresh; Shepard-Commander reads it for status and gets a 2026-04-28 picture. | High (already happening) | Medium — wrong mental model; not data loss. |
| R3 | API usage spike during a Codex session — Claude's watchdog writes STOP, Codex keeps spending. | Low | High when it fires — overshoots budget; recovery requires manual stop. |
| R4 | Two Monday writers (Legion vs Monitor) collide for the same item. | Low (paths are disjoint today) | Medium — duplicated/contradicting updates eroding trust in the board. |
| R5 | `MONDAY_UPDATE.md` patch is rolled back accidentally before Sprint 11/12 commits land. | Low | High — silently breaks the dispatch contract; Legion would post `LEGION_COMPLETE notes` only and flag itself a protocol violation per dispatch doc. |
| R6 | Codex picks the wrong sprint-file location convention on a new repo, work is invisible to Pre-Dispatch Checklist. | Medium | Medium — caught at next dispatch but burns a cycle. |

## 7. Out of Scope for This Review

- Editing vault project pages directly (deferred to the mapper task in Sprint 11).
- Posting any of this to Monday (`Pending Monday Update` block in the operative handoff handles current Sprint 08 board state).
- Running Sprint 11 / Sprint 12 tasks. The execution plan is a *proposal* until Claude reviews this packet and approves.

## 8. Verification (this review)

- [x] `docs/plans/2026-05-05-codex-integration-review.md` exists.
- [x] Title and date present in H1 + frontmatter quote.
- [x] Evidence drawn from real files; every claim links to a file path or section.
- [x] No edits made to vault project pages.
- [x] No Monday writes performed.
- [x] No new commits created by this review pass.
