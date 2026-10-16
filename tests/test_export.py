import json
from pathlib import Path

from ai_use_log.cli import main


def test_export_matches_golden_file_in_deterministic_order(tmp_path, capsys):
    path = tmp_path / "uses.jsonl"
    entries = [
        {
            "ts": "2026-03-02T09:00:00+00:00",
            "tool": "Another Tool",
            "model_version": "2",
            "task": "cite-check",
            "purpose": "Check synthetic references",
            "output_use": "rejected",
            "sections": "References",
            "human_check": "Rechecked each citation",
            "approval_ref": "review-7",
            "confidential_input": False,
        },
        {
            "ts": "2026-03-01T09:00:00+00:00",
            "tool": "Example Tool",
            "model_version": "1",
            "task": "edit",
            "purpose": "Improve clarity",
            "output_use": "modified",
            "sections": "Introduction",
            "human_check": "Compared with source notes",
            "confidential_input": False,
        },
    ]
    path.write_text("".join(json.dumps(entry) + "\n" for entry in entries), encoding="utf-8")

    assert main(["export", "--log", str(path), "--title", "Synthetic Disclosure"]) == 0
    expected = (Path(__file__).parent / "fixtures" / "export.md").read_text(encoding="utf-8")
    assert capsys.readouterr().out == expected


def test_export_writes_file_and_rejects_malformed_log(tmp_path, capsys):
    path = tmp_path / "uses.jsonl"
    output = tmp_path / "appendix.md"
    path.write_text('{"ts":"2026-04-01T00:00:00+00:00","tool":"Example"}\n', encoding="utf-8")
    assert main(["export", "--log", str(path), "--out", str(output)]) == 0
    assert output.read_text(encoding="utf-8").startswith("# AI Use Disclosure Appendix\n")

    path.write_text("not-json\n", encoding="utf-8")
    assert main(["export", "--log", str(path), "--out", str(output)]) == 2
    assert "line 1" in capsys.readouterr().err
