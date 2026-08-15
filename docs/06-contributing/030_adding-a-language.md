# Adding Language Support

The most common substantial contribution, and the one `CONTRIBUTING.md` singles out as
welcome without an issue first: an isolated addition that extends the system along existing
lines. Some sixty languages have walked this path, the maintainers' answer to "would you
accept this?" has consistently been yes, and language servers that follow the template
routinely merge within hours.

The authority is the project's own guide,
[`adding_new_language_support_guide.md`](https://github.com/oraios/serena/blob/main/.serena/memories/adding_new_language_support_guide.md)
— read it in full before starting. This page is the human walk through it.

## What you will build

Five artifacts, each with its own section below:

1. a language-server class,
2. its registration,
3. a fixture repository,
4. a test suite and a pytest marker,
5. the paper trail.

## 1. The language-server class

Your class lives under `src/solidlsp/language_servers/` and follows the
`DependencyProvider` pattern: the launch command comes from a dependency provider rather
than being assembled inline. Pass `None` for `process_launch_info` in `super().__init__()`
and implement `_create_dependency_provider()` to return an inner `DependencyProvider`.

### Choose a base class

Take the most specific one that fits, and read at least one existing implementation of it
before writing your own:

| base class | fits when | reference |
|:--|:--|:--|
| `LanguageServerDependencyProviderUvx` | the server is a PyPI package run on demand via `uvx` — no install step to implement; instantiate with package name, pinned version and entrypoint | `PyrightServer` |
| `LanguageServerDependencyProviderBaseCommand` | the common case: the launch command builds from a *base command* the user can override in custom settings | — |
| `LanguageServerDependencyProviderSinglePath` | one core dependency (an executable, a JAR) that is not itself the base command | `TypeScriptLanguageServer`, `Intelephense`, `ClojureLSP`, `ClangdLanguageServer` |
| `LanguageServerDependencyProvider` (root) | multiple dependencies or custom setup; implement `create_launch_command()` directly — no automatic user override support | `EclipseJDTLS`, `CSharpLanguageServer`, `MatlabLanguageServer` |

Two implementation notes from the guide: override `create_launch_command_env` if the launch
needs environment variables, and never call `subprocess.run` directly — use the
`subprocess_run` helper from `solidlsp.util.subprocess_util`.

### Downloads are declared and verified

Anything your provider downloads goes through `DownloadedDependency`
(`solidlsp.dependency_provider`), which bundles the URL, archive type, allowed hosts and
checksum verification behind a single `download_to()` call. The checksums live in a
URL-keyed database, `src/solidlsp/resources/downloaded_dependency_hashes.json`.

The consequences for your class:

- build each dependency in a factory classmethod (`_create_dep_*`) that takes an optional
  version and falls back to a pinned `DEFAULT_*` constant;
- add an `update_dep_hashes()` classmethod that constructs every dependency and updates the
  database, and hook it into `scripts/update_downloaded_dependency_hashes.py`;
- after bumping any pinned version, re-run that script and commit the JSON — a stale
  database means unverified downloads locally and a CI failure;
- pass `verified=False` only for dependencies whose hash cannot be pinned by design.

The reference implementation is `EclipseJDTLS.DependencyProvider`. Several older servers
still hard-code hashes in constants and call the download helper directly — the guide is
explicit that this legacy shape is not to be copied.

### Initialization parameters

Override `_create_base_initialize_params` to return **only** the server-specific keys —
typically `capabilities` and `initializationOptions`. The common keys (`processId`,
`rootPath`, `rootUri`, `clientInfo`, `workspaceFolders`) are set centrally by the
`InitializeParamsBuilder`, and your override must not touch them.

Two edge cases the builder handles: a server that needs the folder list *nested inside*
`initializationOptions` (as `EclipseJDTLS` and `KotlinLanguageServer` do) sets it there
explicitly — only the top-level `workspaceFolders` is builder-managed; and suppressing the
top-level key entirely goes through `_create_initialize_params_builder` with
`set_workspace_folders=False`.

If the server needs to wait for notifications before it is ready, that logic belongs in
`_start_server` — `EclipseJDTLS._start_server` is the example.

## 2. Registration

One entry in the `LanguageServerId` enum in `src/solidlsp/ls_config.py`, plus two `match`
arms: `get_source_fn_matcher()` returns the file extensions your language claims, and
`get_ls_class()` imports and returns your server class.

## 3. The fixture repository

A minimal but real project under `test/resources/repos/<language>/test_repo/`. Its source
files are what your tests assert against, so they should demonstrate: classes or types (for
symbol lookup), functions with callers (for reference finding), imports (for cross-file
operations), and nesting (for hierarchical symbols).

## 4. Tests and the marker

In the guide's own words: the tests will form the main part of the review. Create
`test/solidlsp/<language>/test_<language>_basic.py`, modelled on
`test/solidlsp/php/test_php_basic.py`, covering at minimum: finding symbols, within-file
references, and cross-file references.

Three rules are firm:

1. assert on the actual symbol and reference names — "a list came back" is not a test;
2. never skip, except on package availability or an unsupported OS;
3. the tests must run in CI — check whether a GitHub action exists for installing the
   toolchain.

Declare the language's marker under `[tool.pytest.ini_options].markers` in
`pyproject.toml`, and run your suite locally with `uv run poe test -m <marker>`.

## 5. The paper trail

Four updates close the contribution:

- **README.md** — add the language to the list;
- **`docs/01-about/020_programming-languages.md`** — add it with any special notes
  (required installations, compatibility);
- **`src/serena/resources/project.template.yml`** — regenerate the commented
  language-server list with `uv run python scripts/print_language_list.py` and paste it
  over the old one, stripping the trailing spaces the script pads with;
- **CHANGELOG.md** — one concise entry.

## Running in CI

Your marker lands in one of the batched jobs — `jvm`, `native`, `other-langs` or `niche` —
according to the lists in `.github/workflows/pytest.yml`; there is nothing to configure
beyond declaring it. On machines without your toolchain the tests skip rather than fail,
centrally, via `test/conftest.py`.

## The precedent

The recent record is encouraging: language servers that follow this template merge fast and
with little friction — Nextflow ([#1815](https://github.com/oraios/serena/pull/1815)),
Gleam ([#1765](https://github.com/oraios/serena/pull/1765)), Deno
([#1778](https://github.com/oraios/serena/pull/1778)) and BasedPyright
([#1705](https://github.com/oraios/serena/pull/1705)) all landed this way. Gleam landed on
its third attempt — persistence with the template works.
