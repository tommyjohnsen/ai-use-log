# PROVENANCE (mirror of .provenance/ledger.jsonl; ledger wins)
# written-by: unknown (pre-provenance) | 2026-10-16 | cc1fd7b
# modified-by: codex/gpt-5.6-sol | 2026-10-26 | 4faff49 | provenance block added
# reviewed-by: claude-code/claude-opus-5-5 | 2026-10-26 | APPROVE
# END PROVENANCE
import json

import pytest

from ai_use_log.schema import SchemaError, load_schema, validate_entry


def test_default_schema_and_allowed_values():
    schema = load_schema()
    entry = {
        "ts": "2026-10-16T12:00:00+00:00",
        "tool": "Example Tool",
        "task": "code",
        "confidential_input": False,
    }
    validate_entry(entry, schema)
    entry["task"] = "unsupported"
    with pytest.raises(SchemaError, match="unsupported value"):
        validate_entry(entry, schema)


def test_custom_schema_adds_and_drops_optional_fields(tmp_path):
    path = tmp_path / "schema.json"
    path.write_text(
        json.dumps(
            {
                "fields": {
                    "approval_ref": None,
                    "purpose": {"rename": "reason"},
                    "audience": {"type": "string", "required": True, "allowed": ["internal"]},
                }
            }
        ),
        encoding="utf-8",
    )
    schema = load_schema(path)
    assert "approval_ref" not in schema["fields"]
    assert "purpose" not in schema["fields"]
    assert schema["fields"]["reason"]["type"] == "string"
    assert schema["fields"]["audience"]["required"] is True


def test_custom_schema_cannot_remove_confidential_field(tmp_path):
    path = tmp_path / "schema.json"
    path.write_text('{"fields":{"confidential_input":null}}', encoding="utf-8")
    with pytest.raises(SchemaError, match="cannot drop required field"):
        load_schema(path)
