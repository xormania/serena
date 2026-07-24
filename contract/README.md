# Language and CI contract

This directory contains Serena's executable contract for language-server registration, provisioning, tests, CI placement, cache invalidation, skip behavior, fixture bootstrap, generated artifacts, and user-facing language lists. It makes repository drift fail cheaply before the multi-platform test matrix starts.

## Two different uses of CUE

Serena's runtime CUE language server is a user-facing language integration pinned at `v0.16.1` in [`src/solidlsp/language_servers/cue_language_server.py`](../src/solidlsp/language_servers/cue_language_server.py).

The contract compiler is an independent development tool pinned at `v0.17.1` in [`contract/cue-version.json`](cue-version.json). Its installer verifies a committed platform-specific SHA-256 before extracting into the user-local Serena tool directory. Changing one pin does not change the other.

## Authority and evidence

The contract deliberately joins several authority classes instead of pretending one file owns every fact:

- **code-authoritative + extracted**: the Python enum, matcher and dispatch arms, server implementation, pytest configuration, fixture layout, central skip guards, workflow, caches, and documentation lists are parsed into normalized facts.
- **contract-authoritative + declared**: one CUE backend declaration records intent that code alone cannot express reliably, including provisioning ownership, platform support, CI expectation, skip category, bootstrap policy, and cache inputs.
- **contract-derived + generated**: [`REGISTRATION.md`](REGISTRATION.md) and the marked language-server list in `project.template.yml` are deterministic committed outputs.
- **behavioral evidence**: pytest exercises matcher equality, concrete dispatch classes, skip-policy state matrices, workflow topology, and every named rejection fixture.

CUE proves that declared intent is coherent and agrees with statically extractable repository structure. It does not prove that a package registry, remote download, language server, or hosted runner will work at runtime; the existing per-language suites and cold-path rehearsals own those behaviors.

## Run the gate

Install or locate the pinned compiler:

```shell
uv run python -m scripts.lsp_contract install-cue
```

Run the static CUE contract gate:

```shell
uv run poe check-contract
# equivalent validation command
uv run python -m scripts.lsp_contract validate
```

Run the behavioral conformance, rejection fixtures, workflow checks, and documentation coverage that complete the local contract:

```shell
uv run pytest test/contract -q
```

Inspect one diagnostic:

```shell
uv run python -m scripts.lsp_contract explain C-REG-001
```

The command contract is stable:

- **Exit code 0**: schemas and invariants are green.
- **Exit code 1**: one or more contract/schema checks rejected the repository. Managed CUE resolution failures are exit 1 process failures and remain visible rather than falling back to another binary.
- **Exit code 2**: extractor structure drift, invalid successful CUE output, or requested summary-output failure prevented a trustworthy result; repository facts were not guessed.

The complete invariant catalogue and remediation guidance is in [`INVARIANTS.md`](INVARIANTS.md).

## Fix loop

1. Read the invariant id, subject, and one-line remediation printed by `validate`.
2. Decide which authority is wrong: code/extracted facts, declaration intent, or a generated output.
3. Fix the source rather than weakening an invariant or hiding a failed provisioning step.
4. Run the focused language or contract tests.
5. Run `uv run poe check-contract` until it reports zero violations.

For registration work, use [`REGISTRATION.md`](REGISTRATION.md) as the ten-surface map and the [language-addition guide](../.serena/memories/adding_new_language_support_guide.md) as the contributor workflow.

## Generated outputs

Exactly two outputs are generated and drift-gated:

```shell
uv run python -m scripts.lsp_contract render-registration
uv run python -m scripts.lsp_contract render-template-list
```

Both commands are deterministic, produce LF-terminated text, and name themselves in their generated headers. Validation regenerates in memory and byte-compares; it never rewrites the worktree.

## Waivers

Waivers live in [`declaration_waivers.cue`](declaration_waivers.cue). A valid waiver names one supported invariant, one exact subject, a non-empty reason, an evidence reference, and an added date. `C-WAIVE-001` checks the pre-waiver violation set so a waiver cannot justify itself or survive after its underlying mismatch disappears.

Not every invariant is waivable. Schema integrity, ambiguous ownership, generated drift, gate topology, extractor drift, and most behavioral checks must be fixed. See each entry's **Waiver guidance** in [`INVARIANTS.md`](INVARIANTS.md) before adding anything to the register. Every waiver review must identify the underlying mismatch and explain why fixing the source is worse than waiving it.

## Known-issue register

These runtime or review-quality facts are intentionally not modeled as CUE invariants or waivers. They require executable evidence, external systems, or future source fixes.

1. **Haxe download bypass.** [`src/solidlsp/language_servers/haxe_language_server.py`](../src/solidlsp/language_servers/haxe_language_server.py) can fall back to `urllib` download behavior, and non-default extension versions do not have committed checksum evidence. A declaration can record the intent but cannot make that dynamic path verifiable.
2. **SystemVerilog override checksum coupling.** [`src/solidlsp/language_servers/systemverilog_server.py`](../src/solidlsp/language_servers/systemverilog_server.py) accepts a `verible_version` override and derives the asset URL from it, while its SHA table represents the default release assets. Runtime override correctness remains an integration concern.
3. **ty pin skew.** [`src/solidlsp/language_servers/ty_server.py`](../src/solidlsp/language_servers/ty_server.py) launches `0.0.25`, while [`pyproject.toml`](../pyproject.toml) currently includes `ty==0.0.24` for development. The paths have different owners and should be reconciled deliberately.
4. **Jedi is PATH-provided.** [`src/solidlsp/language_servers/jedi_server.py`](../src/solidlsp/language_servers/jedi_server.py) launches the external command directly and has no Serena-owned installation path. Availability remains the user's responsibility.
5. **Svelte companion TypeScript skew.** [`src/solidlsp/language_servers/svelte_language_server.py`](../src/solidlsp/language_servers/svelte_language_server.py) pins companion TypeScript `6.0.3`, while [`src/solidlsp/language_servers/typescript_language_server.py`](../src/solidlsp/language_servers/typescript_language_server.py) pins standalone TypeScript `5.9.3`. Compatibility needs runtime coverage, not a false equality invariant.
6. **Lua CI install directory is not separately cached.** [`.github/workflows/pytest.yml`](../.github/workflows/pytest.yml) installs the Lua toolchain outside the static language-server cache. Cold and warm workflow evidence remains the proof surface.
7. **Zig has test-file-level Windows skips.** [`test/solidlsp/zig/test_zig_basic.py`](../test/solidlsp/zig/test_zig_basic.py) contains skips outside the central extracted guard. They remain visible in the known-issue register until centralized or modeled.
8. **Scala has a module-level skip.** [`test/solidlsp/scala/test_scala_language_server.py`](../test/solidlsp/scala/test_scala_language_server.py) skips the suite because fixture compilation is not yet practical. This is intentionally not disguised as contract coverage.

When one of these facts is fixed, update this register in the same change and add the behavioral regression that proves the new state.
