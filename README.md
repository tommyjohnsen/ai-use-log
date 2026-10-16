# ai-use-log

`ai-use-log` is a small, local command-line tool for keeping an append-only JSON Lines record of AI-tool use and producing a deterministic Markdown disclosure appendix. It uses rule-based parsing and validation; it does not call a model API, capture prompts, or upload anything.

Fields are configurable to map to any institution's or client's AI-use policy. The included default schema is generic: it records the timestamp, tool, model version, task, purpose, treatment of the output, affected sections, human check, approval reference, and whether confidential input was supplied. A custom JSON schema can add fields, rename or remove optional fields, change allowed values, and change required flags. The safety rule rejecting `confidential_input: true` cannot be disabled.

All output needs human verification before use. The tool records only what the user enters.

## Install

Python 3.11 or newer is required.

```console
pip install .
```

## Usage

The log defaults to `./ai-use-log.jsonl`. Set `AIL_LOG` or pass `--log` to select another file. Set `AIL_SCHEMA` or pass `--schema` to use a custom schema. Global options may appear before or after the command.

```console
ail add --tool "Example Tool" --task edit \
  --field purpose="Improve clarity" \
  --field output_use=modified \
  --field sections=Introduction \
  --field human_check="Compared with source notes"
ail list --task edit --since 2026-01-01
ail export --out disclosure.md --title "AI Use Disclosure"
ail schema
```

`ail add` accepts repeatable `--field key=value` options. Values that are valid JSON become their JSON types; other values remain strings. Entries are appended and existing bytes are never rewritten. `ail list` emits JSON Lines. `ail export` emits Markdown to standard output unless `--out` is supplied; rows are sorted by timestamp and canonical entry content, columns follow schema order, and section notes have stable headings.

A short synthetic session might add this record:

```json
{"confidential_input":false,"human_check":"Compared with source notes","purpose":"Improve clarity","sections":"Introduction","task":"edit","tool":"Example Tool","ts":"2026-10-16T12:00:00+00:00"}
```

The corresponding appendix contains a Markdown table row and an `Introduction` note describing the recorded human check.

## Exit codes

- `0`: command completed successfully.
- `1`: a new entry failed schema validation and was not written.
- `2`: command input was invalid, or a schema, log, or output file could not be read or written. Malformed existing log lines are reported rather than silently dropped.

## Limits

- The record is self-reported; the tool does not detect AI use, capture prompts, or verify that an entry is complete or accurate.
- Schema checks are structural and rule-based. They do not determine whether use complies with a policy or whether an output is correct.
- Markdown export is a disclosure aid, not a final filing format; rendering and policy requirements can vary, so a person must review it.

## Dependencies and licenses

The installed program has no third-party runtime package dependencies. It uses Python 3.11 or newer and its standard library, distributed under the Python Software Foundation License; that permissive license is compatible with distribution of this Apache-2.0 project. It makes no network requests, uses no external service, and fetches no external data, so there are no service or data terms to accept for normal operation.

Build and development tooling is not included in the installed runtime:

- `setuptools` (MIT License) builds the package. Its permissive terms are compatible with Apache-2.0 distribution.
- `pytest` (MIT License) runs the test suite. Its permissive terms are compatible with Apache-2.0 distribution.
- `uv` (Apache-2.0 and MIT dual license) creates the isolated test environment used by the documented project checks. Either permissive option is compatible with Apache-2.0 distribution.

The project itself is licensed under Apache-2.0; see `LICENSE` and `NOTICE`.
