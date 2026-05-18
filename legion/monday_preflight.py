"""Durable Monday MCP write-access preflight records."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

Status = Literal["available", "missing"]
PREFLIGHT_RELATIVE_PATH = Path(".codex") / "state" / "MONDAY_MCP_PREFLIGHT.md"


@dataclass(frozen=True)
class MondayPreflight:
    repo: str
    board_id: str
    status: Status
    evidence: str
    generated_at: datetime


def preflight_path(repo_root: Path) -> Path:
    return Path(repo_root) / PREFLIGHT_RELATIVE_PATH


def record_monday_preflight(repo_root: Path, preflight: MondayPreflight) -> Path:
    target = preflight_path(repo_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_render(preflight), encoding="utf-8")
    return target


def load_monday_preflight(repo_root: Path) -> MondayPreflight | None:
    target = preflight_path(repo_root)
    if not target.is_file():
        return None

    fields: dict[str, str] = {}
    for line in target.read_text(encoding="utf-8").splitlines():
        if ": " not in line:
            continue
        key, value = line.split(": ", 1)
        fields[key.strip()] = value.strip()

    required = {"Repo", "Board ID", "Status", "Generated", "Evidence"}
    if not required.issubset(fields):
        return None
    status = fields["Status"]
    if status not in {"available", "missing"}:
        return None

    return MondayPreflight(
        repo=fields["Repo"],
        board_id=fields["Board ID"],
        status=status,  # type: ignore[arg-type]
        evidence=fields["Evidence"],
        generated_at=datetime.fromisoformat(fields["Generated"]),
    )


def _render(preflight: MondayPreflight) -> str:
    return (
        "# Monday MCP Preflight\n\n"
        f"Repo: {preflight.repo}\n"
        f"Board ID: {preflight.board_id}\n"
        f"Status: {preflight.status}\n"
        f"Generated: {preflight.generated_at.isoformat()}\n"
        f"Evidence: {preflight.evidence}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record Monday MCP write-access preflight evidence."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--board-id", required=True, help="Monday board ID")
    parser.add_argument(
        "--status", choices=["available", "missing"], required=True
    )
    parser.add_argument("--evidence", required=True, help="Observed tool/access evidence")
    args = parser.parse_args()

    path = record_monday_preflight(
        Path(args.repo_root),
        MondayPreflight(
            repo=args.repo,
            board_id=args.board_id,
            status=args.status,
            evidence=args.evidence,
            generated_at=datetime.now(timezone.utc),
        ),
    )
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
