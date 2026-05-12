# Graph Report - C:\Users\OriShavit\Documents\GitHub\legion-swarm  (2026-05-12)

## Corpus Check
- 15 files · ~56,361 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 29 nodes · 39 edges · 11 communities detected
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 9 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]

## God Nodes (most connected - your core abstractions)
1. `closeAgent()` - 5 edges
2. `test()` - 4 edges
3. `lookup()` - 4 edges
4. `launchAgent()` - 4 edges
5. `register()` - 2 edges
6. `remove()` - 2 edges
7. `listAll()` - 2 edges
8. `listByRole()` - 2 edges
9. `makeTerminalID()` - 2 edges
10. `parseStatusUpdate()` - 2 edges

## Surprising Connections (you probably didn't know these)
- `remove()` --calls--> `closeAgent()`  [INFERRED]
  C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\src\registry.ts → C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\src\tools\close-agent.ts
- `test()` --calls--> `launchAgent()`  [INFERRED]
  C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\smoke-test.js → C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\src\tools\launch-agent.ts
- `closeAgent()` --calls--> `parseStatusUpdate()`  [INFERRED]
  C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\src\tools\close-agent.ts → C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\src\tools\get-agent-status.ts
- `test()` --calls--> `lookup()`  [INFERRED]
  C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\smoke-test.js → C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\src\registry.ts
- `test()` --calls--> `closeAgent()`  [INFERRED]
  C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\smoke-test.js → C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\src\tools\close-agent.ts

## Communities

### Community 0 - "Community 0"
Cohesion: 0.38
Nodes (5): closeAgent(), getAgentStatus(), parseStatusUpdate(), lookup(), test()

### Community 1 - "Community 1"
Cohesion: 0.53
Nodes (0): 

### Community 2 - "Community 2"
Cohesion: 0.67
Nodes (3): listAll(), listByRole(), remove()

### Community 3 - "Community 3"
Cohesion: 0.67
Nodes (3): launchAgent(), register(), makeTerminalID()

### Community 4 - "Community 4"
Cohesion: 1.0
Nodes (1): Legion Nerve Center - cross-repo live TUI dashboard. v1 read-only.

### Community 5 - "Community 5"
Cohesion: 1.0
Nodes (0): 

### Community 6 - "Community 6"
Cohesion: 1.0
Nodes (0): 

### Community 7 - "Community 7"
Cohesion: 1.0
Nodes (0): 

### Community 8 - "Community 8"
Cohesion: 1.0
Nodes (0): 

### Community 9 - "Community 9"
Cohesion: 1.0
Nodes (0): 

### Community 10 - "Community 10"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **1 isolated node(s):** `Legion Nerve Center - cross-repo live TUI dashboard. v1 read-only.`
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 4`** (2 nodes): `__init__.py`, `Legion Nerve Center - cross-repo live TUI dashboard. v1 read-only.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 5`** (2 nodes): `sync-vault-hard-truths.ps1`, `Sync-File()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 6`** (1 nodes): `index.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 7`** (1 nodes): `claude-dialogue-log.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 8`** (1 nodes): `codex-dialogue-check.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 9`** (1 nodes): `codex-handoff.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 10`** (1 nodes): `codex-watchdog-check.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `test()` connect `Community 0` to `Community 3`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Why does `lookup()` connect `Community 0` to `Community 2`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `launchAgent()` connect `Community 3` to `Community 0`, `Community 1`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `closeAgent()` (e.g. with `test()` and `lookup()`) actually correct?**
  _`closeAgent()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `test()` (e.g. with `launchAgent()` and `lookup()`) actually correct?**
  _`test()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `lookup()` (e.g. with `test()` and `closeAgent()`) actually correct?**
  _`lookup()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `launchAgent()` (e.g. with `test()` and `makeTerminalID()`) actually correct?**
  _`launchAgent()` has 3 INFERRED edges - model-reasoned connections that need verification._