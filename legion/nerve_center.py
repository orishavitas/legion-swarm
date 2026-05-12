"""Legion Nerve Center — read-only live TUI dashboard. v1."""

from __future__ import annotations

import argparse
import sys
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Deque, List

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from legion import agent_state, commands, ndjson_tail, repo_scan
from legion.config import Config, ConfigError, load_config

DEFAULT_CONFIG = Path(__file__).parent / "config.json"


def _read_key_nonblocking() -> str | None:
    try:
        import msvcrt  # type: ignore[import-not-found]
    except ImportError:
        return None
    if msvcrt.kbhit():
        return msvcrt.getwch()
    return None


def _repo_grid(snapshots: List[repo_scan.RepoSnapshot]) -> Panel:
    table = Table(expand=True, show_lines=False, header_style="bold magenta")
    table.add_column("Repo", style="bold", no_wrap=True)
    table.add_column("Branch", no_wrap=True)
    table.add_column("Δ", justify="center")
    table.add_column("↑/↓", justify="right")
    table.add_column("Age", justify="right")
    table.add_column("Nx", justify="center")
    table.add_column("Active Task", no_wrap=True)
    table.add_column("Phase", overflow="fold")

    for s in snapshots:
        if s.error:
            table.add_row(s.name, Text(f"err: {s.error[:40]}", style="red"), "", "", "", "", "", "")
            continue
        dirty = Text("●", style="yellow") if s.dirty else Text("·", style="dim")
        ab_style = "red" if s.behind else ("green" if s.ahead else "dim")
        nexus = Text("N", style="cyan") if s.is_nexus else Text("·", style="dim")
        active = Text(s.active_task, style="cyan bold") if s.active_task else Text("—", style="dim")
        table.add_row(
            s.name, s.branch, dirty,
            Text(f"{s.ahead}/{s.behind}", style=ab_style),
            s.last_commit_age, nexus, active,
            Text(s.phase_status, style="dim"),
        )
    return Panel(table, title="[bold]Repo Grid[/]", border_style="magenta")


def _feed_panel(events: Deque[dict]) -> Panel:
    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column(no_wrap=True, style="dim")
    table.add_column(no_wrap=True, style="cyan")
    table.add_column(no_wrap=True)
    table.add_column(no_wrap=True)
    table.add_column(overflow="fold")
    for e in list(events):
        ts = e.get("ts", "")[11:19]
        ev = e.get("event", "")
        ev_style = "green" if "pass" in ev or "ok" in ev else ("red" if "fail" in ev or "error" in ev else "white")
        table.add_row(ts, e.get("repo", ""), Text(ev, style=ev_style), e.get("task_id", ""), e.get("message", ""))
    return Panel(table, title="[bold]Activity Feed[/]", border_style="cyan")


def _agent_panel(claude: agent_state.ClaudeState, codex: list) -> Panel:
    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column(style="bold")
    table.add_column(overflow="fold")
    if not claude.present:
        table.add_row("Claude", Text("no state file", style="dim"))
    else:
        pct = claude.context_pct_used or 0
        ctx_style = "red" if pct > 75 else ("yellow" if pct > 50 else "green")
        label = f"{pct}%" + (" (stale)" if claude.stale else "")
        table.add_row("Claude ctx", Text(label, style=ctx_style))
        if claude.current_repo:
            table.add_row("Claude repo", claude.current_repo)
        if claude.model:
            table.add_row("model", Text(claude.model, style="dim"))
    if codex:
        for repo_name, task_id in codex:
            table.add_row(f"Codex@{repo_name}", Text(task_id, style="cyan"))
    else:
        table.add_row("Codex", Text("idle", style="dim"))
    return Panel(table, title="[bold]Agents[/]", border_style="green")


def _command_panel(last_result: str, last_refresh: datetime) -> Panel:
    body = Text.from_markup(
        "[bold]q[/] quit  [bold]r[/] refresh  [bold]p[/] push  [bold]e[/] edit CLAUDE.md  [bold]t[/] drop packet\n"
        f"[dim]refreshed: {last_refresh:%H:%M:%S}  last: {last_result or '—'}[/]"
    )
    return Panel(body, title="[bold]Commands[/]", border_style="yellow")


def build_layout() -> Layout:
    root = Layout(name="root")
    root.split_column(Layout(name="top"), Layout(name="bottom", size=6))
    root["top"].split_row(Layout(name="grid", ratio=2), Layout(name="side", ratio=1))
    root["side"].split_column(Layout(name="agents", size=10), Layout(name="feed"))
    root["bottom"].update(Panel(""))
    return root


def _scan_all(paths: list) -> list:
    snaps: list = [None] * len(paths)
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(repo_scan.scan_repo, p): i for i, p in enumerate(paths)}
        for fut in as_completed(futs):
            snaps[futs[fut]] = fut.result()
    return [s for s in snaps if s is not None]


def _prompt(console: Console, question: str) -> str:
    console.print(question, end=" ", style="bold yellow")
    try:
        return input().strip()
    except EOFError:
        return ""


def _pick_repo(console: Console, cfg: Config) -> Path | None:
    name = _prompt(console, "repo name (Enter to cancel):")
    if not name:
        return None
    for p in cfg.repo_paths:
        if p.name == name:
            return p
    console.print(f"[red]no repo named {name!r}[/]")
    return None


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(prog="legion-nerve-center")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--once", action="store_true", help="render one frame and exit (smoke test)")
    args = parser.parse_args(argv)

    try:
        cfg = load_config(args.config)
    except ConfigError as exc:
        print(f"config error: {exc}", file=sys.stderr)
        return 2

    console = Console()
    layout = build_layout()
    feed: Deque[dict] = deque(maxlen=cfg.feed_max_lines)
    tailer = ndjson_tail.MultiTailer({
        p.name: p / ".agent-harness" / "logs" / "monitor.ndjson"
        for p in cfg.repo_paths
    })

    last_scan = 0.0
    last_result = ""
    snapshots: list = []
    last_refresh = datetime.now(timezone.utc)

    if args.once:
        snapshots = _scan_all(cfg.repo_paths)
        layout["grid"].update(_repo_grid(snapshots))
        layout["agents"].update(_agent_panel(agent_state.read_claude(cfg.claude_state_file), agent_state.codex_active(cfg.repo_paths)))
        layout["feed"].update(_feed_panel(feed))
        layout["bottom"].update(_command_panel("", last_refresh))
        return 0

    with Live(layout, console=console, refresh_per_second=4, screen=True) as live:
        while True:
            now = time.monotonic()
            if now - last_scan >= cfg.refresh_seconds or not snapshots:
                snapshots = _scan_all(cfg.repo_paths)
                last_scan = now
                last_refresh = datetime.now(timezone.utc)

            for ev in tailer.poll():
                feed.appendleft(ev)

            claude = agent_state.read_claude(cfg.claude_state_file)
            codex = agent_state.codex_active(cfg.repo_paths)

            layout["grid"].update(_repo_grid(snapshots))
            layout["agents"].update(_agent_panel(claude, codex))
            layout["feed"].update(_feed_panel(feed))
            layout["bottom"].update(_command_panel(last_result, last_refresh))

            key = _read_key_nonblocking()
            if key in ("q", "Q"):
                break
            elif key in ("r", "R"):
                last_scan = 0.0
                last_result = "refresh queued"
            elif key in ("p", "P"):
                live.stop()
                repo = _pick_repo(console, cfg)
                if repo:
                    res = commands.git_push(repo)
                    last_result = f"push {repo.name}: {res.message[:80]}"
                live.start()
            elif key in ("e", "E"):
                live.stop()
                repo = _pick_repo(console, cfg)
                if repo:
                    res = commands.open_claude_md(repo, editor=cfg.editor)
                    last_result = f"edit {repo.name}: {res.message[:80]}"
                live.start()
            elif key in ("t", "T"):
                live.stop()
                repo = _pick_repo(console, cfg)
                if repo:
                    task_id = _prompt(console, "task_id:")
                    body = _prompt(console, "objective:")
                    if task_id and body:
                        packet = (
                            f"# Task Packet: {task_id}\n"
                            f"**Created:** {datetime.now(timezone.utc).date().isoformat()}\n\n"
                            "## Objective\n\n" + body + "\n"
                        )
                        res = commands.drop_packet(repo, task_id, packet)
                        last_result = f"drop {repo.name}/{task_id}: {res.message[:80]}"
                live.start()

            time.sleep(0.25)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
