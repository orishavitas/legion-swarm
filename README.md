# legion-swarm

A persistent, role-specialized AI agent swarm controlled by Legion (meta-orchestrator). Dispatches real Claude Code terminal sessions per agent role, coordinated via Monday.com and Google Chat.

## Purpose

Replace ad-hoc subagent dispatch with a structured, sprint-driven team of 11 specialists — each with a single job, hard role boundaries, and persistent state via Monday.com.

## Architecture

```
Shepard-Commander (you)
    ↓
Legion (meta-orchestrator — always-on PM)
    ↓ reads sprint board from Monday
    ↓ calls launch_agent() via Launcher MCP
    ↓
Agent Launcher MCP Server (spawns Windows Terminal tabs)
    ↓
Physical terminal sessions — each a full Claude Code instance
  Architect | Planner | Coder | Tester | Debugger
  Reviewer | Refactorer | Mapper | Documenter | Frontend | QA
    ↓ each reads/writes Monday, pings Google Chat
```

## Structure

```
agents/           — 11 agent identity files (one per role)
agents/settings/  — per-role skill loadout stubs (Sprint 02: full schema)
meta/             — Legion identity (CLAUDE.md for this repo)
mcp/launcher/     — spawns terminal sessions per agent
mcp/monday-sync/  — Monday board helpers
mcp/google-chat/  — ping integration
skills/           — shared skills (codebase-mapping, etc.)
monday/           — board templates per repo
docs/specs/       — design specs
docs/plans/       — sprint plans
```

## Agent Roles

| Role | Responsibility |
|------|---------------|
| Architect | System design, tech decisions, interface contracts |
| Planner | Breaks specs into tasks, writes plans, owns sprint shape |
| Coder | Implements exactly what the plan says, TDD |
| Tester | Writes + runs tests, enforces TDD, owns test suite health |
| Debugger | Traces root causes, isolates failures |
| Reviewer | Spec compliance + code quality review |
| Refactorer | Cleans, simplifies, reduces complexity |
| Mapper | Owns CODEBASE_MAP.md, updates after every sprint |
| Documenter | Breadcrumbs, changelogs, inline comments |
| Frontend | UI/UX implementation, component design, accessibility |
| QA | End-to-end validation, acceptance criteria, release sign-off |
