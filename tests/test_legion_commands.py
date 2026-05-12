import subprocess
from pathlib import Path

from legion import commands


def _init_repo(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=p, check=True)
    return p


def test_drop_packet_writes_file(tmp_path):
    repo = _init_repo(tmp_path / "r")
    (repo / ".agent-harness" / "inbox").mkdir(parents=True)
    res = commands.drop_packet(repo, "TASK-9", "# Task Packet: TASK-9\nbody\n")
    assert res.ok
    assert (repo / ".agent-harness" / "inbox" / "TASK-9.task.md").exists()


def test_drop_packet_rejects_bad_id(tmp_path):
    repo = _init_repo(tmp_path / "r")
    (repo / ".agent-harness" / "inbox").mkdir(parents=True)
    res = commands.drop_packet(repo, "bad id with spaces", "x")
    assert not res.ok


def test_drop_packet_no_inbox(tmp_path):
    repo = _init_repo(tmp_path / "r")
    res = commands.drop_packet(repo, "TASK-1", "x")
    assert not res.ok
    assert "inbox" in res.message.lower()


def test_drop_packet_refuses_overwrite(tmp_path):
    repo = _init_repo(tmp_path / "r")
    inbox = repo / ".agent-harness" / "inbox"
    inbox.mkdir(parents=True)
    (inbox / "TASK-1.task.md").write_text("existing", encoding="utf-8")
    res = commands.drop_packet(repo, "TASK-1", "new")
    assert not res.ok


def test_open_claude_md_missing(tmp_path):
    repo = _init_repo(tmp_path / "r")
    res = commands.open_claude_md(repo, editor="echo")
    assert not res.ok


def test_git_push_no_remote(tmp_path):
    repo = _init_repo(tmp_path / "r")
    (repo / "f.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t.t"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "t"], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "x"], check=True)
    res = commands.git_push(repo)
    assert not res.ok
