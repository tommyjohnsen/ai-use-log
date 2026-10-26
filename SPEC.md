<!--
PROVENANCE (mirror of .provenance/ledger.jsonl; ledger wins)
written-by: unknown (pre-provenance) | 2026-10-16 | 8f848d5
modified-by: codex/gpt-5.6-sol | 2026-10-26 | pending | provenance block added
END PROVENANCE
-->
# ai-use-log: spec

Stdlib-only Python CLI that keeps an append-only JSONL log of AI tool use while producing a document, and exports a Markdown disclosure appendix (Pandoc-friendly).

## Commands (console script `ail`, module `ai_use_log`)
- `ail add --tool ... --task ... [--field key=value ...]` appends one entry. `ts` defaults to now (ISO 8601, UTC offset kept).
- `ail list [--since DATE] [--task TASK]` prints entries.
- `ail export [--out FILE] [--title TITLE]` writes the Markdown appendix (a table plus per-section notes), deterministic order.
- `ail schema` prints the active schema.
- Log path from `--log` or env `AIL_LOG`, default `./ai-use-log.jsonl`. Schema path from `--schema` or env `AIL_SCHEMA`.
- Exit codes: 0 ok, 1 validation failure, 2 bad input or unreadable file.

## Schema (configurable)
- Fields are configurable so they can be mapped to any institution's or client's AI-use policy. A generic default schema ships in the package (JSON). A user schema file (JSON) can add, rename or drop optional fields, set allowed values and required flags.
- Default fields: `ts`, `tool`, `model_version`, `task` (research, outline, edit, cite-check, code), `purpose`, `output_use` (adopted, modified, rejected), `sections`, `human_check`, `approval_ref`, `confidential_input` (bool, must be false).
- Hard rule that no schema can turn off: an entry with `confidential_input` true is rejected (exit 1) and never written.
- Append-only: the tool never rewrites or deletes existing lines. Malformed existing lines are reported, not dropped.

## README must say
- Fields are configurable to map to any institution's or client's AI-use policy; the default schema is generic.
- Output needs human verification. The tool records what the user enters; it does not capture prompts or upload anything.

## Rules for all parts
- Deterministic only: rule-based parsing and exact or fuzzy matching against authoritative sources. No LLM or model makes any pass/fail call, and nothing calls a model API at runtime. Output is a first pass that a human verifies.
- License Apache-2.0 (LICENSE and NOTICE are already here; keep them as they are). pyproject.toml: `license = "Apache-2.0"`, requires-python >=3.11.
- Tests use pytest and must pass with this exact command run from this directory (network is off; the uv cache is pre-warmed):
  `UV_OFFLINE=1 UV_CACHE_DIR=$UVC uv run --no-project --with pytest pytest -q`
  where $UVC is the pre-warmed cache path given in the job prompt. Put `[tool.pytest.ini_options]` with `pythonpath = ["src"]` and `testpaths = ["tests"]` in pyproject.toml. Use a src/ layout.
- All network access in tests is mocked (unittest.mock on the stdlib HTTP layer). No live calls in tests or CI.
- Synthetic fixtures only (synthetic citations and DOIs; no real drafts or notes). No hostnames other than the public API hosts named here, no IPs, local paths, usernames, real emails (use `you@example.com`; contact email only from env `CONTACT_EMAIL` or a config file, never hardcoded), account details, real data or secrets.
- Tokens and contact emails come only from environment variables read at runtime. Never print, log, cache or write their values.
- The README must state that all output needs human verification before use.
- Do not copy text from The Bluebook or any licensed or library source. Do not bundle CSL styles.
- Work only inside this directory. Do not read or copy anything from other directories.
