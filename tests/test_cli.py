# PROVENANCE (mirror of .provenance/ledger.jsonl; ledger wins)
# written-by: unknown (pre-provenance) | 2026-10-16 | cc1fd7b
# modified-by: codex/gpt-5.6-sol | 2026-10-26 | 4faff49 | provenance block added
# reviewed-by: claude-code/claude-opus-5-5 | 2026-10-26 | APPROVE
# END PROVENANCE
import json

from ai_use_log.cli import main


def test_schema_command_prints_active_custom_schema(tmp_path, capsys):
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(
        json.dumps({"fields": {"purpose": {"required": True}}}),
        encoding="utf-8",
    )
    assert main(["schema", "--schema", str(schema_path)]) == 0
    assert json.loads(capsys.readouterr().out)["fields"]["purpose"]["required"] is True


def test_bad_field_syntax_is_bad_input(capsys):
    try:
        main(["add", "--tool", "Example", "--task", "code", "--field", "broken"])
    except SystemExit as exc:
        assert exc.code == 2
    assert "key=value" in capsys.readouterr().err
