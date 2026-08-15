# Adding language support

The most common substantial contribution, and the one `CONTRIBUTING.md` singles out as welcome
without an issue first: an isolated addition that extends the system along existing lines. Some
sixty languages have walked this path, so the trail is well marked.

The authority is the project's own guide,
[`adding_new_language_support_guide.md`](https://github.com/oraios/serena/blob/main/.serena/memories/adding_new_language_support_guide.md)
— read it in full before starting. The map, so you know what you are in for:

1. **A language-server class** under `src/solidlsp/language_servers/`, built on the
   `DependencyProvider` pattern. Four base classes cover the usual shapes — run via `uvx`, run
   a command, run a single downloaded binary, or the general case — and the guide names a
   reference implementation for each (`PyrightServer`, `Intelephense`, `EclipseJDTLS`, …).
   Anything downloaded is verified against the URL-keyed checksum database in
   `src/solidlsp/resources/downloaded_dependency_hashes.json`; some older servers hard-code
   hashes in constants instead, and the guide is explicit that this legacy shape is not to be
   copied.
2. **Registration** in the `LanguageServerId` enum in `src/solidlsp/ls_config.py`, wiring up
   the file matcher and the server class.
3. **A fixture repository** under `test/resources/repos/<language>/test_repo/` — a small, real
   project for the tests to run against.
4. **Tests** under `test/solidlsp/<language>/`, modelled on
   `test/solidlsp/php/test_php_basic.py`, plus a pytest marker declared in `pyproject.toml`.
   The guide's three test rules are firm: assert on actual symbol and reference names; never
   skip except for package availability or OS; and the tests must run in CI.
5. **The paper trail**: the README, `docs/01-about/020_programming-languages.md`, the
   regenerated language list in `src/serena/resources/project.template.yml`
   (`uv run python scripts/print_language_list.py`), and a `CHANGELOG.md` entry.

In CI, the new marker lands in one of the batched jobs — `jvm`, `native`, `other-langs` or
`niche` — according to the lists in `.github/workflows/pytest.yml`; there is nothing to
configure beyond declaring the marker.
