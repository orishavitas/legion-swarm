---
name: watchdog
description: Teaches agents how to launch the watchdog subagent at session start and respond to watchdog signals. Loaded by all 11 agents and Legion.
---

# Watchdog Skill

## Overview

Every agent session launches a watchdog subagent at startup. The watchdog polls context and API usage every 5 tool uses and takes protective action at thresholds. The parent agent session continues working — the watchdog operates independently.

## How to Launch (Session Start Step 5)

At session start, after reading the quartet and your Monday task:

1. Read `skills/watchdog/watchdog-prompt.md`
2. Replace `{{AGENT_ROLE}}` with your role name (e.g. `coder`, `planner`, etc.)
3. Launch via `Task` tool with the substituted prompt content
4. Do not await the result — the watchdog runs as a background subagent

## Your Responsibilities vs the Watchdog's

| Event | Who acts |
|-------|----------|
| Context ≥ 80% | Watchdog (auto compact) |
| Context ≥ 95% | Watchdog (graceful stop + Monday update) |
| Usage ≥ 95% | Watchdog (writes STOP sentinel, pings Shepard-Commander) |
| STOP sentinel detected | **You** — see below |

## Responding to STOP Sentinel

### Claude agents (PostToolUse hook)

After **every** tool use, your PostToolUse hook checks for `.watchdog/STOP`. If found:

1. Run `/quartet-update` immediately
2. Write to your Monday board item: `Last Update = "[YYYY-MM-DD HH:MM] Paused — system-wide usage limit reached"`, `Status = Blocked`, `Ping Required = true`
3. Stop your session

Do not continue working after detecting the STOP sentinel. Do not wait for the watchdog to contact you.

### Codex agents (Step 0 check)

Codex CLI does not run Claude Code hooks. Instead, Codex runs `scripts/codex-watchdog-check.ps1` as **Step 0** of its session protocol — before reading the KB, before any build work.

- Exit 0 (no STOP) → proceed normally.
- Exit 1 (STOP detected) → update sprint task to `blocked`, run `codex-handoff.ps1`, emit `LEGION_COMPLETE: status=blocked`, exit.

Codex also re-checks between Steps 7 and 8 (between pre-flight and execution) to catch a STOP that arrived while Codex was reading state files.

## What You Do NOT Do

- Do not restart the watchdog if it stops — one watchdog per session
- Do not read `status.json` directly — the hook handles sentinel detection
- Do not delete the STOP sentinel — only Shepard-Commander removes it to resume
