# PROVENANCE (mirror of .provenance/ledger.jsonl; ledger wins)
# written-by: unknown (pre-provenance) | 2026-10-16 | cc1fd7b
# modified-by: codex/gpt-5.6-sol | 2026-10-26 | 4faff49 | provenance block added
# END PROVENANCE
"""Append-only JSON Lines storage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator


class MalformedLineError(ValueError):
    def __init__(self, line_number: int, detail: str) -> None:
        self.line_number = line_number
        super().__init__(f"line {line_number}: {detail}")


def append_entry(path: str | Path, entry: dict[str, Any]) -> None:
    """Append one compact JSON object and never inspect or rewrite prior data."""
    with Path(path).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":"), sort_keys=True))
        handle.write("\n")


def read_entries(path: str | Path) -> Iterator[dict[str, Any] | MalformedLineError]:
    with Path(path).open("r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            try:
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError("entry is not a JSON object")
            except (json.JSONDecodeError, ValueError) as exc:
                yield MalformedLineError(number, str(exc))
            else:
                yield value
