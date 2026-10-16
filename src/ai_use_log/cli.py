"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from .log import MalformedLineError, append_entry, read_entries
from .schema import SchemaError, load_schema, validate_entry


def _json_value(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _field(text: str) -> tuple[str, Any]:
    if "=" not in text:
        raise argparse.ArgumentTypeError("field must be key=value")
    name, value = text.split("=", 1)
    if not name:
        raise argparse.ArgumentTypeError("field name cannot be empty")
    return name, _json_value(value)


def _parser() -> argparse.ArgumentParser:
    global_options = argparse.ArgumentParser(add_help=False)
    global_options.add_argument("--log", default=os.environ.get("AIL_LOG", "ai-use-log.jsonl"))
    global_options.add_argument("--schema", default=os.environ.get("AIL_SCHEMA"))
    command_options = argparse.ArgumentParser(add_help=False)
    command_options.add_argument("--log", default=argparse.SUPPRESS)
    command_options.add_argument("--schema", default=argparse.SUPPRESS)
    parser = argparse.ArgumentParser(prog="ail", parents=[global_options])
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", parents=[command_options])
    add.add_argument("--tool", required=True)
    add.add_argument("--task", required=True)
    add.add_argument("--field", action="append", type=_field, default=[])
    listing = commands.add_parser("list", parents=[command_options])
    listing.add_argument("--since")
    listing.add_argument("--task")
    commands.add_parser("schema", parents=[command_options])
    return parser


def _parse_since(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        if "T" not in value:
            return datetime.combine(date.fromisoformat(value), datetime.min.time(), timezone.utc)
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise ValueError("--since must be an ISO 8601 date or timestamp") from exc


def _entry_time(entry: dict[str, Any]) -> datetime | None:
    value = entry.get("ts")
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        schema = load_schema(args.schema)
    except SchemaError as exc:
        print(f"ail: {exc}", file=sys.stderr)
        return 2
    if args.command == "schema":
        print(json.dumps(schema, indent=2, sort_keys=True))
        return 0
    if args.command == "add":
        entry: dict[str, Any] = dict(args.field)
        if "tool" in entry or "task" in entry:
            print("ail: --field cannot replace tool or task", file=sys.stderr)
            return 2
        entry.update(tool=args.tool, task=args.task)
        entry.setdefault("ts", datetime.now(timezone.utc).isoformat())
        entry.setdefault("confidential_input", False)
        try:
            validate_entry(entry, schema)
        except SchemaError as exc:
            print(f"ail: validation failed: {exc}", file=sys.stderr)
            return 1
        try:
            append_entry(args.log, entry)
        except OSError as exc:
            print(f"ail: cannot append log: {exc}", file=sys.stderr)
            return 2
        print(json.dumps(entry, sort_keys=True))
        return 0
    try:
        since = _parse_since(args.since)
    except ValueError as exc:
        print(f"ail: {exc}", file=sys.stderr)
        return 2
    malformed = False
    try:
        for item in read_entries(args.log):
            if isinstance(item, MalformedLineError):
                print(f"ail: malformed log {item}", file=sys.stderr)
                malformed = True
                continue
            if args.task is not None and item.get("task") != args.task:
                continue
            timestamp = _entry_time(item)
            if since is not None and (timestamp is None or timestamp < since):
                continue
            print(json.dumps(item, sort_keys=True))
    except OSError as exc:
        print(f"ail: cannot read log: {exc}", file=sys.stderr)
        return 2
    return 2 if malformed else 0


if __name__ == "__main__":
    raise SystemExit(main())
