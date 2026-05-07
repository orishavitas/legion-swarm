# Graph Report - C:\Users\OriShavit\Documents\GitHub\legion-swarm  (2026-05-07)

## Corpus Check
- 14 files · ~53,187 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 27 nodes · 38 edges · 10 communities detected
- Extraction: 76% EXTRACTED · 24% INFERRED · 0% AMBIGUOUS · INFERRED: 9 edges (avg confidence: 0.8)
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
- `test()` --calls--> `launchAgent()`  [INFERRED]
  C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\smoke-test.js → C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\src\tools\launch-agent.ts
- `remove()` --calls--> `closeAgent()`  [INFERRED]
  C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\src\registry.ts → C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\src\tools\close-agent.ts
- `closeAgent()` --calls--> `parseStatusUpdate()`  [INFERRED]
  C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\src\tools\close-agent.ts → C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\src\tools\get-agent-status.ts
- `test()` --calls--> `lookup()`  [INFERRED]
  C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\smoke-test.js → C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\src\registry.ts
- `test()` --calls--> `closeAgent()`  [INFERRED]
  C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\smoke-test.js → C:\Users\OriShavit\Documents\GitHub\legion-swarm\mcp\launcher\src\tools\close-agent.ts

## Communities

### Community 0 - "Community 0"
Cohesion: 0.52
Nodes (0): 

### Community 1 - "Community 1"
Cohesion: 0.33
Nodes (6): closeAgent(), getAgentStatus(), parseStatusUpdate(), lookup(), remove(), test()

### Community 2 - "Community 2"
Cohesion: 1.0
Nodes (2): listAll(), listByRole()

### Community 3 - "Community 3"
Cohesion: 0.67
Nodes (3): launchAgent(), register(), makeTerminalID()

### Community 4 - "Community 4"
Cohesion: 1.0
Nodes (0): 

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

## Knowledge Gaps
- **Thin community `Community 4`** (2 nodes): `sync-vault-hard-truths.ps1`, `Sync-File()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 5`** (1 nodes): `index.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 6`** (1 nodes): `claude-dialogue-log.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 7`** (1 nodes): `codex-dialogue-check.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 8`** (1 nodes): `codex-handoff.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 9`** (1 nodes): `codex-watchdog-check.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `test()` connect `Community 1` to `Community 3`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `lookup()` connect `Community 1` to `Community 2`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `launchAgent()` connect `Community 3` to `Community 0`, `Community 1`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `closeAgent()` (e.g. with `test()` and `lookup()`) actually correct?**
  _`closeAgent()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `test()` (e.g. with `launchAgent()` and `lookup()`) actually correct?**
  _`test()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `lookup()` (e.g. with `test()` and `closeAgent()`) actually correct?**
  _`lookup()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `launchAgent()` (e.g. with `test()` and `makeTerminalID()`) actually correct?**
  _`launchAgent()` has 3 INFERRED edges - model-reasoned connections that need verification._