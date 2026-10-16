from ai_use_log.cli import _parser


def test_global_options_work_before_or_after_command():
    before = _parser().parse_args(["--log", "before.jsonl", "list"])
    after = _parser().parse_args(["list", "--log", "after.jsonl"])
    assert before.log == "before.jsonl"
    assert after.log == "after.jsonl"
