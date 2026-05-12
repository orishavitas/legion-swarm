"""Load and validate legion/config.json."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


class ConfigError(Exception):
    pass


@dataclass
class Config:
    repos_root: Path
    repo_paths: List[Path] = field(default_factory=list)
    refresh_seconds: int = 30
    feed_max_lines: int = 200
    claude_state_file: Path | None = None
    editor: str = "code"


def _autodiscover(root: Path) -> List[Path]:
    return sorted(
        child for child in root.iterdir()
        if child.is_dir() and (child / ".git").exists()
    )


def load_config(path: Path) -> Config:
    path = Path(path)
    if not path.exists():
        raise ConfigError(f"config not found: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON in {path}: {exc}") from exc

    repos_root = Path(raw.get("repos_root", "")).resolve()
    if not repos_root.is_dir():
        raise ConfigError(f"repos_root does not exist: {repos_root}")

    repo_list = raw.get("repos", [])
    repo_paths = (
        [(repos_root / r).resolve() for r in repo_list]
        if repo_list
        else _autodiscover(repos_root)
    )

    claude_state_file = raw.get("claude_state_file")
    return Config(
        repos_root=repos_root,
        repo_paths=repo_paths,
        refresh_seconds=int(raw.get("refresh_seconds", 30)),
        feed_max_lines=int(raw.get("feed_max_lines", 200)),
        claude_state_file=Path(claude_state_file).resolve() if claude_state_file else None,
        editor=raw.get("editor", "code"),
    )
