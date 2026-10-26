# PROVENANCE (mirror of .provenance/ledger.jsonl; ledger wins)
# written-by: unknown (pre-provenance) | 2026-10-16 | 1b4c1e3
# modified-by: codex/gpt-5.6-sol | 2026-10-26 | 4faff49 | added linked-output regression tests; provenance block added
# END PROVENANCE
import json
import os
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


def test_export_refuses_symlink_to_log_without_truncating_it(tmp_path, capsys):
    path = tmp_path / "uses.jsonl"
    output = tmp_path / "appendix.md"
    original = '{"tool":"Example Tool"}\n'
    path.write_text(original, encoding="utf-8")
    output.symlink_to(path)

    assert main(["export", "--log", str(path), "--out", str(output)]) == 2
    assert path.read_text(encoding="utf-8") == original
    assert "output must differ" in capsys.readouterr().err


def test_export_refuses_hard_link_to_log_without_truncating_it(tmp_path, capsys):
    path = tmp_path / "uses.jsonl"
    output = tmp_path / "appendix.md"
    original = '{"tool":"Example Tool"}\n'
    path.write_text(original, encoding="utf-8")
    os.link(path, output)

    assert main(["export", "--log", str(path), "--out", str(output)]) == 2
    assert path.read_text(encoding="utf-8") == original
    assert "output must differ" in capsys.readouterr().err
