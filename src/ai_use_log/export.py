# PROVENANCE (mirror of .provenance/ledger.jsonl; ledger wins)
# written-by: unknown (pre-provenance) | 2026-10-16 | 1b4c1e3
# modified-by: codex/gpt-5.6-sol | 2026-10-26 | 4faff49 | provenance block added
# END PROVENANCE
"""Deterministic Markdown disclosure export."""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Any, Iterable


DEFAULT_TITLE = "AI Use Disclosure Appendix"


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return str(value)


def _cell(value: Any) -> str:
    return _text(value).replace("\\", "\\\\").replace("|", "\\|").replace("\r\n", "<br>").replace("\r", "<br>").replace("\n", "<br>")


def _heading(value: Any) -> str:
    return " ".join(_text(value).split()).replace("#", "\\#")


def _label(name: str) -> str:
    return name.replace("_", " ").strip().title()


def _sort_key(entry: dict[str, Any]) -> tuple[str, str]:
    timestamp = entry.get("ts")
    return (
        timestamp if isinstance(timestamp, str) else "",
        json.dumps(entry, ensure_ascii=False, separators=(",", ":"), sort_keys=True),
    )


def render_markdown(
    entries: Iterable[dict[str, Any]],
    schema: dict[str, Any],
    title: str = DEFAULT_TITLE,
) -> str:
    """Render entries in stable timestamp/content order as Pandoc-friendly Markdown."""
    rows = sorted(entries, key=_sort_key)
    fields = list(schema["fields"])
    lines = [f"# {_heading(title)}", "", "## Recorded uses", ""]
    lines.append("| " + " | ".join(_label(field) for field in fields) + " |")
    lines.append("| " + " | ".join("---" for _ in fields) + " |")
    for entry in rows:
        lines.append("| " + " | ".join(_cell(entry.get(field)) for field in fields) + " |")

    lines.extend(["", "## Per-section notes", ""])
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in rows:
        section = entry.get("sections")
        if section not in (None, "", []):
            grouped[_text(section)].append(entry)
    if not grouped:
        lines.append("No section-specific notes recorded.")
    else:
        for section in sorted(grouped, key=lambda value: (value.casefold(), value)):
            lines.extend([f"### {_heading(section)}", ""])
            for entry in grouped[section]:
                tool = _text(entry.get("tool")) or "Unspecified tool"
                detail = _text(entry.get("human_check")) or "No human-check note recorded."
                lines.append(f"- **{_cell(tool)}:** {_cell(detail)}")
            lines.append("")
        lines.pop()
    return "\n".join(lines) + "\n"
