# PROVENANCE (mirror of .provenance/ledger.jsonl; ledger wins)
# written-by: unknown (pre-provenance) | 2026-10-16 | cc1fd7b
# modified-by: codex/gpt-5.6-sol | 2026-10-26 | 4faff49 | provenance block added
# END PROVENANCE
from ai_use_log.cli import _parser


def test_global_options_work_before_or_after_command():
    before = _parser().parse_args(["--log", "before.jsonl", "list"])
    after = _parser().parse_args(["list", "--log", "after.jsonl"])
    assert before.log == "before.jsonl"
    assert after.log == "after.jsonl"
