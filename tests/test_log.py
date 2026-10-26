# PROVENANCE (mirror of .provenance/ledger.jsonl; ledger wins)
# written-by: unknown (pre-provenance) | 2026-10-16 | cc1fd7b
# modified-by: codex/gpt-5.6-sol | 2026-10-26 | 4faff49 | provenance block added
# END PROVENANCE
import json

from ai_use_log.cli import main


def test_add_appends_without_changing_existing_bytes(tmp_path, capsys):
    path = tmp_path / "uses.jsonl"
    original = '{"old":"entry"}\n'
    path.write_text(original, encoding="utf-8")
    result = main(["add", "--log", str(path), "--tool", "Example", "--task", "edit"])
    assert result == 0
    contents = path.read_text(encoding="utf-8")
    assert contents.startswith(original)
    assert len(contents.splitlines()) == 2
    assert json.loads(contents.splitlines()[1])["confidential_input"] is False
    capsys.readouterr()


def test_confidential_input_is_rejected_without_write(tmp_path, capsys):
    path = tmp_path / "uses.jsonl"
    result = main(
        [
            "add",
            "--log",
            str(path),
            "--tool",
            "Example",
            "--task",
            "research",
            "--field",
            "confidential_input=true",
        ]
    )
    assert result == 1
    assert not path.exists()
    assert "must be false" in capsys.readouterr().err


def test_list_reports_malformed_lines_and_prints_valid_entries(tmp_path, capsys):
    path = tmp_path / "uses.jsonl"
    path.write_text(
        '{"ts":"2026-01-02T00:00:00+00:00","task":"code"}\nnot-json\n',
        encoding="utf-8",
    )
    result = main(["list", "--log", str(path)])
    captured = capsys.readouterr()
    assert result == 2
    assert json.loads(captured.out)["task"] == "code"
    assert "line 2" in captured.err


def test_list_filters_by_date_and_task(tmp_path, capsys):
    path = tmp_path / "uses.jsonl"
    rows = [
        {"ts": "2026-01-01T00:00:00+00:00", "task": "edit"},
        {"ts": "2026-02-01T00:00:00+00:00", "task": "code"},
    ]
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    assert main(["list", "--log", str(path), "--since", "2026-01-15", "--task", "code"]) == 0
    assert json.loads(capsys.readouterr().out)["task"] == "code"
