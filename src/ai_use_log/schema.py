"""Schema loading and entry validation."""

from __future__ import annotations

import copy
import json
from importlib.resources import files
from pathlib import Path
from typing import Any


class SchemaError(ValueError):
    """Raised for an invalid schema or entry."""


def _read_json(path: Path | None) -> dict[str, Any]:
    source = path if path is not None else files("ai_use_log").joinpath("default_schema.json")
    try:
        with source.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise SchemaError(f"cannot read schema: {exc}") from exc
    if not isinstance(value, dict):
        raise SchemaError("schema must be a JSON object")
    return value


def load_schema(path: str | Path | None = None) -> dict[str, Any]:
    """Load the default schema, optionally applying a user field overlay."""
    base = _read_json(None)
    if path is None:
        schema = base
    else:
        custom = _read_json(Path(path))
        if "fields" not in custom:
            raise SchemaError("schema must contain a fields object")
        schema = copy.deepcopy(base)
        custom_fields = custom["fields"]
        if not isinstance(custom_fields, dict):
            raise SchemaError("schema fields must be an object")
        fields = schema["fields"]
        for name, rule in custom_fields.items():
            if rule is None:
                if name not in fields:
                    raise SchemaError(f"cannot drop unknown field: {name}")
                if fields[name].get("required") or name == "confidential_input":
                    raise SchemaError(f"cannot drop required field: {name}")
                del fields[name]
            elif isinstance(rule, dict) and "rename" in rule:
                target = rule["rename"]
                if name not in fields:
                    raise SchemaError(f"cannot rename unknown field: {name}")
                if fields[name].get("required") or name == "confidential_input":
                    raise SchemaError(f"cannot rename required field: {name}")
                if not isinstance(target, str) or not target or target in fields:
                    raise SchemaError(f"invalid renamed field: {target}")
                renamed = fields.pop(name)
                renamed.update({key: value for key, value in rule.items() if key != "rename"})
                fields[target] = renamed
            elif name in fields and isinstance(rule, dict):
                fields[name].update(rule)
            else:
                fields[name] = rule
        for key, value in custom.items():
            if key != "fields":
                schema[key] = value
    _validate_schema(schema)
    return schema


def _validate_schema(schema: dict[str, Any]) -> None:
    fields_value = schema.get("fields")
    if not isinstance(fields_value, dict) or not fields_value:
        raise SchemaError("schema fields must be a non-empty object")
    valid_types = {"string", "boolean", "number", "integer", "array", "object"}
    for name, rule in fields_value.items():
        if not isinstance(name, str) or not name or not isinstance(rule, dict):
            raise SchemaError("each field must have a name and an object rule")
        if rule.get("type") not in valid_types:
            raise SchemaError(f"field {name} has an invalid type")
        if "required" in rule and not isinstance(rule["required"], bool):
            raise SchemaError(f"field {name} required must be boolean")
        if "allowed" in rule and not isinstance(rule["allowed"], list):
            raise SchemaError(f"field {name} allowed must be an array")
    confidential = fields_value.get("confidential_input")
    if not isinstance(confidential, dict) or confidential.get("type") != "boolean":
        raise SchemaError("confidential_input must be a boolean field")


def validate_entry(entry: dict[str, Any], schema: dict[str, Any]) -> None:
    """Validate an entry, including the non-configurable confidentiality rule."""
    if entry.get("confidential_input") is True:
        raise SchemaError("confidential_input must be false")
    fields_value = schema["fields"]
    unknown = set(entry) - set(fields_value)
    if unknown and not schema.get("allow_unknown_fields", False):
        raise SchemaError(f"unknown field(s): {', '.join(sorted(unknown))}")
    missing = [name for name, rule in fields_value.items() if rule.get("required") and name not in entry]
    if missing:
        raise SchemaError(f"missing required field(s): {', '.join(missing)}")
    types = {
        "string": str,
        "boolean": bool,
        "number": (int, float),
        "integer": int,
        "array": list,
        "object": dict,
    }
    for name, value in entry.items():
        rule = fields_value.get(name)
        if rule is None:
            continue
        expected = types[rule["type"]]
        if not isinstance(value, expected) or rule["type"] in {"number", "integer"} and isinstance(value, bool):
            raise SchemaError(f"field {name} must be {rule['type']}")
        if "allowed" in rule and value not in rule["allowed"]:
            raise SchemaError(f"field {name} has an unsupported value")
