import json
from pathlib import Path

import pytest

from legion import config as legion_config


def _write(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_load_minimal(tmp_path):
    repos_root = tmp_path / "ghub"
    (repos_root / "a").mkdir(parents=True)
    cfg_path = _write(tmp_path / "c.json", {
        "repos_root": str(repos_root),
        "repos": ["a"],
    })
    cfg = legion_config.load_config(cfg_path)
    assert cfg.repos_root == repos_root
    assert cfg.repo_paths == [repos_root / "a"]
    assert cfg.refresh_seconds == 30
    assert cfg.feed_max_lines == 200
    assert cfg.editor == "code"


def test_autodiscover_when_repos_empty(tmp_path):
    root = tmp_path / "g"
    (root / "alpha" / ".git").mkdir(parents=True)
    (root / "beta" / ".git").mkdir(parents=True)
    (root / "gamma").mkdir(parents=True)  # no .git, must be skipped
    cfg_path = _write(tmp_path / "c.json", {
        "repos_root": str(root),
        "repos": [],
    })
    cfg = legion_config.load_config(cfg_path)
    names = sorted(p.name for p in cfg.repo_paths)
    assert names == ["alpha", "beta"]


def test_missing_repos_root_raises(tmp_path):
    cfg_path = _write(tmp_path / "c.json", {
        "repos_root": str(tmp_path / "does-not-exist"),
        "repos": [],
    })
    with pytest.raises(legion_config.ConfigError):
        legion_config.load_config(cfg_path)


def test_missing_file_raises(tmp_path):
    with pytest.raises(legion_config.ConfigError):
        legion_config.load_config(tmp_path / "nope.json")


def test_missing_repo_path_recorded(tmp_path):
    root = tmp_path / "g"
    root.mkdir()
    cfg_path = _write(tmp_path / "c.json", {
        "repos_root": str(root),
        "repos": ["ghost"],
    })
    cfg = legion_config.load_config(cfg_path)
    assert cfg.repo_paths == [root / "ghost"]
