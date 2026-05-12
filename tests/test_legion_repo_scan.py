import subprocess
from pathlib import Path

from legion import repo_scan


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _init_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "-q", "-b", "main")
    _git(path, "config", "user.email", "t@t.t")
    _git(path, "config", "user.name", "t")
    (path / "f.txt").write_text("hi", encoding="utf-8")
    _git(path, "add", ".")
    _git(path, "commit", "-q", "-m", "init")
    return path


def test_scan_basic(tmp_path):
    repo = _init_repo(tmp_path / "demo")
    snap = repo_scan.scan_repo(repo)
    assert snap.name == "demo"
    assert snap.branch == "main"
    assert snap.dirty is False
    assert snap.ahead == 0
    assert snap.behind == 0
    assert snap.is_nexus is False
    assert snap.active_task == ""
    assert snap.error == ""


def test_scan_dirty(tmp_path):
    repo = _init_repo(tmp_path / "demo")
    (repo / "f.txt").write_text("changed", encoding="utf-8")
    snap = repo_scan.scan_repo(repo)
    assert snap.dirty is True


def test_scan_nexus_with_active_task(tmp_path):
    repo = _init_repo(tmp_path / "demo")
    inbox = repo / ".agent-harness" / "inbox"
    inbox.mkdir(parents=True)
    (inbox / "TASK-42.task.md").write_text("# Task Packet: TASK-42\n", encoding="utf-8")
    snap = repo_scan.scan_repo(repo)
    assert snap.is_nexus is True
    assert snap.active_task == "TASK-42"


def test_scan_phase_status_from_claude_md(tmp_path):
    repo = _init_repo(tmp_path / "demo")
    (repo / "CLAUDE.md").write_text(
        "# CLAUDE.md\n\nActive phase: Phase 7 — Nerve Center build\nmore text\n",
        encoding="utf-8",
    )
    snap = repo_scan.scan_repo(repo)
    assert "Phase 7" in snap.phase_status


def test_scan_missing_repo_records_error(tmp_path):
    snap = repo_scan.scan_repo(tmp_path / "nope")
    assert snap.error != ""
    assert snap.name == "nope"


def test_scan_non_git_directory_records_error(tmp_path):
    p = tmp_path / "plain"
    p.mkdir()
    snap = repo_scan.scan_repo(p)
    assert snap.error != ""


def test_last_commit_age_format(tmp_path):
    repo = _init_repo(tmp_path / "demo")
    snap = repo_scan.scan_repo(repo)
    assert snap.last_commit_age and " " not in snap.last_commit_age
