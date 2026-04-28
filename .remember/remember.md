# Handoff

## State
Design spec for `legion-swarm-mac` approved and committed to `legion-swarm`: `docs/superpowers/specs/2026-04-28-legion-swarm-mac-design.md`.
Obsidian vault live at `Shared drives/R&D Department/AI Research and knowledge base/Obsidian/legion-wiki/` — GDrive shared, cross-machine, Dataview installed, index.md has live query.
Graphify skill installed: `~/.claude/skills/graphify/SKILL.md` + `graphifyy` Python package + registered in `~/.claude/CLAUDE.md`.
`legion-swarm-mac` repo does NOT exist yet — implementation plan not written.

## Next
1. Invoke `superpowers:writing-plans` on `docs/superpowers/specs/2026-04-28-legion-swarm-mac-design.md` to produce implementation plan.
2. Create `legion-swarm-mac` repo and scaffold it per the plan.
3. Run `scripts/verify-monday.ts` to confirm Monday API live before first Legion session.

## Context
- tmux session name: `legion`. Agent windows named `role-8hexchars`.
- `OBSIDIAN_VAULT` for `.env.example`: `GDrive Shared drives/R&D Department/AI Research and knowledge base/Obsidian/legion-wiki`
- Graphify held for future Mapper ingest sprint — not part of legion-mac v1.
- Nexus (project_nexus on GDrive) separate effort — not integrated into legion-mac.
- `file-management-agent` has `todo.review` with 30 items — paused, not abandoned.
