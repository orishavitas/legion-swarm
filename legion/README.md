# Legion Nerve Center

Cross-repo live TUI dashboard for the Nexus methodology.

## Run

```powershell
pip install -r legion/requirements.txt
python -m legion
```

## Config

Edit `legion/config.json`:
- `repos_root` - folder containing all repos
- `repos` - list of repo paths relative to `repos_root`. Empty = auto-discover.
- `refresh_seconds` - repo grid refresh interval (default 30)
- `claude_state_file` - path Claude writes its state to (optional)
- `editor` - command to open files (default `code`)

## Keys

`q` quit | `r` force refresh | `p` push repo | `e` edit CLAUDE.md | `t` drop task packet
