"""Multi-file NDJSON tailer — stateful, polling, never raises."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class MultiTailer:
    def __init__(self, sources: Dict[str, Path]) -> None:
        self._sources = {name: Path(path) for name, path in sources.items()}
        self._offsets: Dict[str, int] = {name: 0 for name in self._sources}

    def poll(self) -> List[dict]:
        results: List[dict] = []
        for name, path in self._sources.items():
            if not path.is_file():
                continue
            try:
                size = path.stat().st_size
                offset = self._offsets[name]
                if size < offset:
                    # file was truncated — reset
                    offset = 0
                if size == offset:
                    continue
                with path.open("r", encoding="utf-8", errors="replace") as f:
                    f.seek(offset)
                    chunk = f.read(size - offset)
                    self._offsets[name] = f.tell()
                for line in chunk.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    obj["repo"] = name
                    results.append(obj)
            except OSError:
                pass
        return results
