# Obsidian Vault Setup — Legion Wiki

## One-Time Human Steps

1. Open Obsidian → "Open folder as vault" → select `C:/Users/OriShavit/obsidian/legion-wiki/`
2. Install plugins (Settings → Community plugins):
   - **Dataview** — for querying frontmatter across project pages
   - **Smart Connections** (optional) — semantic search for larger vaults
3. Obsidian Web Clipper (browser extension) — optional, for capturing articles to `raw/`

## How Legion Uses This Vault

- **Session start**: reads `wiki/index.md` only — 1 file, all project states
- **When scoped to a repo**: reads `wiki/projects/[repo].md` for full context
- **After each sprint**: dispatches Mapper to ingest updated quartet → updates project page + index

## Vault Structure

```
legion-wiki/
├── CLAUDE.md              ← wiki agent instructions
├── raw/repos/[repo]/      ← immutable quartet copies per repo
├── wiki/
│   ├── index.md           ← Legion reads this at session start
│   ├── log.md             ← append-only ingest history
│   ├── projects/          ← one page per repo
│   └── decisions/         ← cross-repo architectural decisions
└── skills/                ← wiki operation instructions
```

## Triggering a Wiki Update Manually

Tell Legion: "update wiki for [repo]"
Legion will dispatch Mapper with the ingest task.

## Vault Location

`C:/Users/OriShavit/obsidian/legion-wiki/`
