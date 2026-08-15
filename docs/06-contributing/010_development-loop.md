# The development loop

Environment setup is three commands, described in
[CONTRIBUTING.md](https://github.com/oraios/serena/blob/main/CONTRIBUTING.md): create a
virtualenv with `uv`, activate it, `uv sync --extra dev`. Everything below assumes that.

## The four commands

Every change runs through the same four [poe](https://github.com/nat-n/poethepoet) tasks,
defined in `pyproject.toml`:

| command | what it does |
|:--|:--|
| `uv run poe format` | rewrites: `ruff check --fix`, then `ruff format`, over `src`, `scripts` and `test` |
| `uv run poe lint` | the same two ruff passes, checking only — this is what CI runs |
| `uv run poe type-check` | [`ty`](https://github.com/astral-sh/ty) over the sources and the tests |
| `uv run poe test` | `pytest test -vv` — see the markers below before running it bare |

Format before pushing: the lint gate is the first thing CI executes, so one unformatted file
fails the whole matrix in its first minute.

## Tests and markers

Core tests are unmarked and always run. Every supported language has a pytest marker (`python`,
`go`, `java`, … — the full list, with the language server each one uses, is in `pyproject.toml`
under `[tool.pytest.ini_options]`), so `poe test -m "python or go"` selects accordingly. A
language whose server or toolchain is not installed locally is skipped, not failed — and that
decision lives in exactly one place, `test/conftest.py`, rather than per test file. Two markers
are not languages: `snapshot` (snapshot tests for the symbolic editing operations, via syrupy)
and `slow`.

Language-server tests run against small, real fixture repositories under
`test/resources/repos/<language>/test_repo/`.

## What CI runs against a pull request

The test workflow batches the markers into five jobs — `jvm`, `native`, `other-langs`, `niche`,
and a `catch-all` for everything unmarked — across Linux, macOS and Windows. `poe lint` and
`poe type-check` run once per OS, in the catch-all batch. The docs build (`poe doc-build`,
Sphinx with warnings as errors) and a spell check run alongside. The reasoning behind the
batching — and why the suite deliberately does not use xdist — is written down in the header
comment of `.github/workflows/pytest.yml`, worth reading before touching anything CI-adjacent.

## Generated files: regenerate, never edit

Some files in the tree are outputs, and hand edits to them are undone by the next generation
run:

- `src/serena/generated/generated_prompt_factory.py` — after changing prompt templates,
  regenerate with `uv run python scripts/gen_prompt_factory.py`, re-format, and commit the
  result.
- The commented language list in `src/serena/resources/project.template.yml` — regenerate with
  `uv run python scripts/print_language_list.py`.
- `docs/01-about/000_intro.md`, `025_features.md` and `035_tools.md` — written by
  `docs/autogen_docs.py` during `poe doc-build`: the first two from the README, the tool list
  from the tool registry.
- The download-verification hashes in
  `src/solidlsp/resources/downloaded_dependency_hashes.json` — via
  `uv run python scripts/update_downloaded_dependency_hashes.py` after a server version bump.

## Running tools without an LLM

A tool is an ordinary Python object and does not need an agent attached:
`scripts/demo_run_tools.py` executes Serena's tools against this repository directly, and its
siblings (`demo_diagnostics.py`, `demo_find_defining_symbol.py`, …) do the same for narrower
surfaces. This is the fastest loop for tool work — no MCP client, no model, no waiting.

Last, before the pull request: a concise entry in `CHANGELOG.md` under the matching section.
The PR template asks for exactly two things, and that is one of them; the other is the scope
rule in `CONTRIBUTING.md`.
