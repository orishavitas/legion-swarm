# Sprint 03 — Codebase Mapper Skill

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans

**Goal:** Build the `codebase-mapping` skill that teaches the Mapper agent how to generate and maintain `CODEBASE_MAP.md`. The skill is also loaded by the Documenter.

**Spec:** `docs/specs/2026-04-05-legion-swarm-design.md` — Section 3

---

### Task 1: Create skill directory

- Create `legion-swarm/skills/codebase-mapping/` directory
- Add `.gitkeep` placeholder (no content yet — populated in Task 2)
- Commit: `chore: scaffold codebase-mapping skill directory`
- **Verify:** directory exists in repo

---

### Task 2: Write SKILL.md

- File: `legion-swarm/skills/codebase-mapping/SKILL.md`
- Frontmatter: `name: codebase-mapping`, description that surfaces for both Mapper and Documenter loadouts
- **Overview section:** what the skill teaches — generating a token-efficient, polyglot-aware codebase index that any agent can read to locate anything without opening files
- **When to use section:** three triggers — (1) no `CODEBASE_MAP.md` exists for this repo, (2) a sprint changed the repo's module structure, entry points, or zone layout, (3) Mapper is explicitly dispatched by Legion
- **Core pattern section — four named steps:**
  1. Detect ownership: determine if this is our repo or a guest repo. Guest repos get a Monday doc — zero files touched in their repo.
  2. Detect zones: scan root-level directories and config files (package.json, pyproject.toml, Cargo.toml, go.mod, etc.) to identify language/runtime boundaries. Each distinct runtime is a zone with an ID, path, and responsibility.
  3. Build the map: populate all five sections in order — Zones, Entry Points, Modules, Conventions, Agent Notes. IDs must be short and uppercase (e.g. WEB, API, WORKER). Module paths are relative. Key exports are comma-separated, no prose.
  4. Deliver: our repo — write `CODEBASE_MAP.md` to repo root, mirror content to Monday doc, commit. Guest repo — write Monday doc only, confirm zero repo changes.
- **Updating an existing map section:** how to check whether a sprint's file changes require a map update (structure changed = yes, logic-only change = no), how to update in place (update Last updated line, add Agent Note entry, revise only the affected rows), and when to regenerate from scratch (major refactor, zone added or removed)
- **Guest vs owner behavior table:** four scenarios from spec Section 3 — our repo with map, our repo without map, guest repo with map, guest repo without map
- **CODEBASE_MAP.md format section:** exact template with all five section headers and column definitions — agents must reproduce this exactly, no variations
- **Common mistakes section:** five entries — (1) writing to a guest repo, (2) using prose in table cells instead of identifiers, (3) listing every file as a module instead of grouping by responsibility, (4) forgetting to mirror to Monday after writing the file, (5) regenerating the full map when only one module changed
- Commit: `feat: add codebase-mapping skill`
- **Verify:** file has frontmatter, five major sections, guest/owner table, format template, common mistakes — all present and complete

---

### Task 3: Wire skill into Mapper and Documenter settings

- File: `legion-swarm/agents/settings/mapper-settings.json`
- File: `legion-swarm/agents/settings/documenter-settings.json`
- Add `"codebase-mapping"` to the skills array in each file (Mapper: only skill; Documenter: alongside existing skills per spec)
- Commit: `feat: wire codebase-mapping skill into mapper and documenter loadouts`
- **Verify:** both JSON files reference `"codebase-mapping"`, Mapper has it as its sole skill, Documenter has it alongside `"simplify"`

---

### Task 4: Update Mapper agent identity

- File: `legion-swarm/agents/mapper.md`
- Ensure the Skills Loaded section references `codebase-mapping` (the skill built in this sprint, not a placeholder)
- Add one sentence to the Identity section: Mapper is the only agent with write access to `CODEBASE_MAP.md` — all other agents read only
- Add to You Never Do: "Touches production code or modifies any file other than `CODEBASE_MAP.md` and its Monday mirror"
- Commit: `feat: finalize mapper agent identity with codebase-mapping skill`
- **Verify:** mapper.md reflects sole ownership of `CODEBASE_MAP.md`, skill is linked

---

### Task 5: Push and validate

- Push branch to GitHub
- Confirm `legion-swarm/skills/codebase-mapping/SKILL.md` renders correctly on GitHub
- Confirm `mapper-settings.json` and `documenter-settings.json` are valid JSON
- **Verify:** `git log --oneline -5` shows all four commits from this sprint in order
