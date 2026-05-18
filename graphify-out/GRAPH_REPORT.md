# Graph Report - C:\Users\OriShavit\Documents\GitHub\legion-swarm  (2026-05-18)

## Corpus Check
- 28 files · ~65,031 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 113 nodes · 194 edges · 15 communities detected
- Extraction: 73% EXTRACTED · 27% INFERRED · 0% AMBIGUOUS · INFERRED: 52 edges (avg confidence: 0.79)
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
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]

## God Nodes (most connected - your core abstractions)
1. `main()` - 18 edges
2. `scan_repo()` - 13 edges
3. `load_config()` - 10 edges
4. `MultiTailer` - 9 edges
5. `drop_packet()` - 7 edges
6. `_init_repo()` - 7 edges
7. `_init_repo()` - 7 edges
8. `read_claude()` - 6 edges
9. `closeAgent()` - 5 edges
10. `_write()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `read_claude()` --calls--> `main()`  [INFERRED]
  C:\Users\OriShavit\Documents\GitHub\legion-swarm\legion\agent_state.py → C:\Users\OriShavit\Documents\GitHub\legion-swarm\legion\nerve_center.py
- `read_claude()` --calls--> `test_read_claude_missing_returns_empty()`  [INFERRED]
  C:\Users\OriShavit\Documents\GitHub\legion-swarm\legion\agent_state.py → C:\Users\OriShavit\Documents\GitHub\legion-swarm\tests\test_legion_agent_state.py
- `read_claude()` --calls--> `test_read_claude_fresh()`  [INFERRED]
  C:\Users\OriShavit\Documents\GitHub\legion-swarm\legion\agent_state.py → C:\Users\OriShavit\Documents\GitHub\legion-swarm\tests\test_legion_agent_state.py
- `read_claude()` --calls--> `test_read_claude_stale()`  [INFERRED]
  C:\Users\OriShavit\Documents\GitHub\legion-swarm\legion\agent_state.py → C:\Users\OriShavit\Documents\GitHub\legion-swarm\tests\test_legion_agent_state.py
- `codex_active()` --calls--> `main()`  [INFERRED]
  C:\Users\OriShavit\Documents\GitHub\legion-swarm\legion\agent_state.py → C:\Users\OriShavit\Documents\GitHub\legion-swarm\legion\nerve_center.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.19
Nodes (11): closeAgent(), getAgentStatus(), parseStatusUpdate(), launchAgent(), listAll(), listByRole(), lookup(), register() (+3 more)

### Community 1 - "Community 1"
Cohesion: 0.22
Nodes (16): _humanize_age(), Probe a repo for git state + Nexus harness state. Pure, never raises., _read_active_task(), _read_phase_status(), RepoSnapshot, _run_git(), scan_repo(), _git() (+8 more)

### Community 2 - "Community 2"
Cohesion: 0.25
Nodes (13): _autodiscover(), Config, ConfigError, load_config(), Load and validate legion/config.json., Exception, Legion Nerve Center — read-only live TUI dashboard. v1., test_autodiscover_when_repos_empty() (+5 more)

### Community 3 - "Community 3"
Cohesion: 0.25
Nodes (11): _agent_panel(), build_layout(), _command_panel(), _feed_panel(), main(), _pick_repo(), _prompt(), _read_key_nonblocking() (+3 more)

### Community 4 - "Community 4"
Cohesion: 0.3
Nodes (12): CommandResult, drop_packet(), git_push(), open_claude_md(), v1 command-bar actions. Local only — no network beyond plain git push., _init_repo(), test_drop_packet_no_inbox(), test_drop_packet_refuses_overwrite() (+4 more)

### Community 5 - "Community 5"
Cohesion: 0.35
Nodes (8): MultiTailer, Multi-file NDJSON tailer — stateful, polling, never raises., _append(), test_first_poll_reads_existing_lines(), test_malformed_line_is_skipped_not_raised(), test_missing_file_is_skipped(), test_subsequent_poll_returns_only_new(), test_truncation_resets_offset()

### Community 6 - "Community 6"
Cohesion: 0.29
Nodes (8): ClaudeState, codex_active(), Read agent status: Claude state file + Codex inbox snapshots., read_claude(), test_codex_active_lists_inbox(), test_read_claude_fresh(), test_read_claude_missing_returns_empty(), test_read_claude_stale()

### Community 7 - "Community 7"
Cohesion: 1.0
Nodes (1): Legion Nerve Center - cross-repo live TUI dashboard. v1 read-only.

### Community 8 - "Community 8"
Cohesion: 1.0
Nodes (0):

### Community 9 - "Community 9"
Cohesion: 1.0
Nodes (0):

### Community 10 - "Community 10"
Cohesion: 1.0
Nodes (0):

### Community 11 - "Community 11"
Cohesion: 1.0
Nodes (0):

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (0):

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (0):

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (0):

## Knowledge Gaps
- **6 isolated node(s):** `Read agent status: Claude state file + Codex inbox snapshots.`, `v1 command-bar actions. Local only — no network beyond plain git push.`, `Load and validate legion/config.json.`, `Multi-file NDJSON tailer — stateful, polling, never raises.`, `Probe a repo for git state + Nexus harness state. Pure, never raises.` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 7`** (2 nodes): `__init__.py`, `Legion Nerve Center - cross-repo live TUI dashboard. v1 read-only.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 8`** (2 nodes): `sync-vault-hard-truths.ps1`, `Sync-File()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 9`** (1 nodes): `__main__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 10`** (1 nodes): `index.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (1 nodes): `claude-dialogue-log.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (1 nodes): `codex-dialogue-check.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (1 nodes): `codex-handoff.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (1 nodes): `codex-watchdog-check.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `Community 3` to `Community 2`, `Community 4`, `Community 5`, `Community 6`?**
  _High betweenness centrality (0.262) - this node is a cross-community bridge._
- **Why does `load_config()` connect `Community 2` to `Community 3`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Why does `MultiTailer` connect `Community 5` to `Community 3`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `main()` (e.g. with `load_config()` and `MultiTailer`) actually correct?**
  _`main()` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `scan_repo()` (e.g. with `test_scan_basic()` and `test_scan_dirty()`) actually correct?**
  _`scan_repo()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `load_config()` (e.g. with `main()` and `test_load_minimal()`) actually correct?**
  _`load_config()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `MultiTailer` (e.g. with `main()` and `test_first_poll_reads_existing_lines()`) actually correct?**
  _`MultiTailer` has 6 INFERRED edges - model-reasoned connections that need verification._
