# Language and CI contract invariants

This reference defines every diagnostic emitted by the language-server registration and CI contract. Run `uv run poe check-contract` for the complete local gate, or `uv run python -m scripts.lsp_contract explain <ID>` for the short form of one entry.

A waiver is an explicit, reviewed record for a known current mismatch. Only entries marked waivable below accept one; `C-WAIVE-001` rejects stale, incomplete, or mis-scoped waivers.

## C-EXTR-001

### Meaning

A repository source changed shape in a way the structural extractor cannot interpret safely.

### Typical fix

Update the source to the supported shape or extend the named extractor and its drift tests before changing declarations.

### Waiver guidance

Non-waivable. Extractor drift exits with code 2 because evaluating the contract on guessed facts would be unsafe.

## C-REG-001

### Meaning

Backend declarations and `LanguageServerId` members must be the same set in both directions.

### Typical fix

Add the missing declaration or enum member and complete the remaining registration surfaces.

### Waiver guidance

Waivable only for a reviewed, exact backend subject while the pre-waiver mismatch remains current.

## C-REG-002

### Meaning

Every backend must have a dispatch arm whose module and class match its declaration.

### Typical fix

Align the declaration with `LanguageServerId.get_ls_class()` and the real server class.

### Waiver guidance

Waivable for an exact backend subject; runtime class behavior still requires behavioral evidence.

## C-REG-003

### Meaning

Every backend must resolve to its own matcher arm or an explicitly declared shared matcher arm.

### Typical fix

Add the matcher case or correct `matcher.sharedArmWith`.

### Waiver guidance

Waivable for a narrowly scoped backend while the missing matcher is intentionally unresolved.

## C-REG-004

### Meaning

Declared stable or experimental status must agree with the extracted experimental set.

### Typical fix

Align `backend.status` with `LanguageServerId.is_experimental()`.

### Waiver guidance

Waivable for the exact backend whose status transition is temporarily incomplete.

## C-REG-005

### Meaning

An alternate backend must reuse a language owned by an existing default backend.

### Typical fix

Point the alternate at the correct language and keep the language identity separate from backend identity.

### Waiver guidance

Waivable only for a reviewed backend-specific migration; do not mint a duplicate source language.

## C-REG-006

### Meaning

Each language must have one coherent default backend, or one sole backend when no alternates exist.

### Typical fix

Correct backend roles and the language declaration's `defaultBackend`.

### Waiver guidance

Waivable for the exact language subject during a bounded default-backend transition.

## C-REG-007

### Meaning

The generated project-template language-server list must contain every registered backend identifier.

### Typical fix

Run `uv run python -m scripts.lsp_contract render-template-list` and commit the result.

### Waiver guidance

Waivable only for a current template mismatch; generated-output freshness remains independently non-waivable.

## C-TEST-001

### Meaning

Every tested backend marker must be declared in `pyproject.toml`.

### Typical fix

Declare the marker or correct the backend's `testing.marker`.

### Waiver guidance

Waivable for an exact backend while its marker declaration is intentionally staged.

## C-TEST-002

### Meaning

Every tested backend must resolve to an existing fixture repository.

### Typical fix

Add the fixture under `test/resources/repos/` or correct `fixtureRepo` and `aliasOf`.

### Waiver guidance

Waivable only for the exact backend with a reviewed temporary fixture exception.

## C-TEST-003

### Meaning

Every tested backend must name an existing `test/solidlsp/` directory.

### Typical fix

Add the focused test directory or correct `testing.testDir`.

### Waiver guidance

Waivable for a current, backend-specific test-directory gap.

## C-TEST-004

### Meaning

Every language marker must be owned by a backend unless it is explicitly informational.

### Typical fix

Declare the owning backend or remove the orphan marker.

### Waiver guidance

Waivable only for an exact marker subject with a documented temporary owner gap.

## C-TEST-005

### Meaning

Central fixture aliases and marker mappings must be unique and cover tested alternate backends.

### Typical fix

Remove duplicate keys and add the correct alternate alias and marker mapping in `test/conftest.py`.

### Waiver guidance

Waivable for the exact conflicting or missing alias subject while it remains observable.

## C-TEST-006

### Meaning

Every backend declared untested must have an explicit current waiver.

### Typical fix

Add a meaningful test surface, or register the reviewed untested-backend exception.

### Waiver guidance

Waivable by design, using the exact backend subject and a concrete reason and reference.

## C-PROV-001

### Meaning

Provisioning declarations must satisfy the closed shape for their selected strategy.

### Typical fix

Add the required pin, checksum, executable, package, ownership, or composite fields.

### Waiver guidance

Non-waivable. An invalid provisioning declaration cannot be interpreted reliably.

## C-PROV-002

### Meaning

Source-build declarations and extracted Cargo install commands must agree and use lock discipline.

### Typical fix

Declare the source-build leaf and retain `--locked` in each `cargo install` command.

### Waiver guidance

Waivable only for an exact backend with reviewed evidence explaining the temporary lock-discipline gap.

## C-PROV-003

### Meaning

Default-version downloads require checksum evidence aligned with the declared download strategy.

### Typical fix

Add immutable checksum or integrity evidence, or align the declaration with the actual source path.

### Waiver guidance

Waivable for an exact download or checksum-opacity subject when static proof is genuinely unavailable.

## C-PROV-004

### Meaning

Package-manager provisioning must be pinned or carry a current matching waiver.

### Typical fix

Pin the package-manager version and its cache input, or document the moving-version exception.

### Waiver guidance

Waivable for the exact backend whose package-manager pin cannot yet be made immutable.

## C-PROV-005

### Meaning

Declared platform support must agree with provable or explicitly opaque provisioning paths.

### Typical fix

Add structured platform evidence, correct supported platforms, or identify the opaque path precisely.

### Waiver guidance

Waivable for exact `backend:coverage-opaque` subjects backed by a source reference.

## C-PROV-006

### Meaning

Provisioning ownership must name one runtime owner and one CI owner.

### Typical fix

Declare both `provisioning.owner.runtime` and `provisioning.owner.ci` from repository evidence.

### Waiver guidance

Non-waivable. Ambiguous ownership makes provisioning and failure responsibility unknowable.

## C-PLAT-001

### Meaning

Supported and excluded platforms must form an exact Linux, macOS, and Windows partition with reasons.

### Typical fix

Place each OS exactly once and provide a non-empty reason for every exclusion.

### Waiver guidance

Waivable for a precise backend/platform transition with an evidence-backed reason.

## C-CI-001

### Meaning

Tested backends must agree with their declared workflow batch or carry a current never-run waiver.

### Typical fix

Correct the marker batch, enable the backend in CI, or register the exact reviewed exception.

### Waiver guidance

Waivable for an exact backend that is intentionally not scheduled in the current matrix.

## C-CI-002

### Meaning

CI batch declarations are restricted to the workflow matrix batch enum.

### Typical fix

Use a declared batch that is present in the workflow matrix.

### Waiver guidance

Non-waivable. Unknown batch identity cannot be scheduled or checked.

## C-CI-003

### Meaning

A test marker may occur in at most one named workflow batch group.

### Typical fix

Remove the duplicate marker from the incorrect workflow expression.

### Waiver guidance

Non-waivable. Duplicate ownership makes matrix selection ambiguous.

## C-CI-004

### Meaning

Catch-all backend markers must not also occur in a named workflow group.

### Typical fix

Remove the marker from named groups or declare its actual named batch.

### Waiver guidance

Non-waivable. The catch-all partition must remain deterministic.

## C-CI-005

### Meaning

CI provisioning ownership must resolve to one non-opaque install step covering the declared batch and OS set.

### Typical fix

Correct `ci.installStep` and its workflow gates, or declare runtime or image ownership from evidence.

### Waiver guidance

Non-waivable. A CI-expected toolchain must have a visible provisioning owner.

## C-CI-006

### Meaning

Declared batch OS intent must equal the effective matrix and remain within backend platform support.

### Typical fix

Correct `ci.os`, batch intent, matrix exclusions, or the platform declaration.

### Waiver guidance

Non-waivable. Unsupported or missing matrix placement would silently misstate coverage.

## C-CI-007

### Meaning

Every workflow job must declare a positive timeout.

### Typical fix

Add a positive `timeout-minutes` value to the job.

### Waiver guidance

Non-waivable. Bounded CI execution is a gate integrity requirement.

## C-CACHE-001

### Meaning

Every declared cache must cover its backend provisioning inputs with key tokens and matching execution gates.

### Typical fix

Bind the correct cache and include every pin, lockfile, or install-step input in its key.

### Waiver guidance

Waivable for an exact cache or backend subject when the current cache remains intentionally static.

## C-CACHE-002

### Meaning

Cache schema-version tokens must occur in the primary key and every restore prefix.

### Typical fix

Carry the same version token through the key and all `restore-keys` prefixes.

### Waiver guidance

Waivable for the exact cache while a reviewed restore-prefix migration remains outstanding.

## C-SKIP-001

### Meaning

Skip-policy declarations must include the fields required by their category.

### Typical fix

Add `loudOn` for category 2, or the required reason and waiver for categories 1 and 5.

### Waiver guidance

Waivable only through the category-specific exact subject and current rationale.

## C-SKIP-002

### Meaning

A backend expected in CI may not silently skip when its precondition is absent.

### Typical fix

Use a loud category 2 or unconditional category 4 policy, or fix CI provisioning.

### Waiver guidance

Waivable for an exact backend with a reviewed temporary silent-skip exception.

## C-FIX-001

### Meaning

Fixture bootstrap steps must be structured and evidenced; opaque shell execution needs explicit review.

### Typical fix

Declare structured bootstrap steps and extracted evidence instead of an opaque shell command.

### Waiver guidance

Waivable for an exact bootstrap subject whose shell step cannot yet be structured.

## C-FIX-002

### Meaning

Required fixture bootstrap may not mask failures on CI.

### Typical fix

Fail loudly on CI and retain visible provisioning output and postconditions.

### Waiver guidance

Waivable for an exact fixture while the known fail-masking path remains current.

## C-FIX-003

### Meaning

A required bootstrap declaration must name at least one produced artifact.

### Typical fix

Add a concrete `testing.bootstrap.produces` postcondition checked by the fixture.

### Waiver guidance

Non-waivable. Required bootstrap without a postcondition has no verifiable success state.

## C-CAP-001

### Meaning

Verified implementation-support claims must exactly match the extracted evidence set.

### Typical fix

Align the declaration with `_VERIFIED_IMPLEMENTATION_LANGUAGES` and its behavioral tests.

### Waiver guidance

Non-waivable. Capability claims must remain evidence-backed.

## C-GEN-001

### Meaning

The two committed generated artifacts must match deterministic regeneration byte for byte.

### Typical fix

Run both `render-registration` and `render-template-list`, review, and commit the outputs.

### Waiver guidance

Non-waivable. Generated drift is mechanically repairable and must never be normalized as debt.

## C-DOC-001

### Meaning

Stable default and sole languages must appear in the README and authored language-guide lists.

### Typical fix

Add each missing `docLabel` to the reported authored document.

### Waiver guidance

Waivable per exact document path for a reviewed, temporary authored-list gap.

## C-WAIVE-001

### Meaning

Every waiver must identify a current pre-waiver violation and carry complete rationale and reference data.

### Typical fix

Remove stale waivers or repair the id, invariant, subject, reason, and reference.

### Waiver guidance

Non-waivable. This invariant is the integrity check for the waiver mechanism itself.

## B-REG-001

### Meaning

The real matcher extension set must equal the declared extension set for every backend.

### Typical fix

Align the CUE matcher declaration with `get_source_fn_matcher()` and its computed arm.

### Waiver guidance

Non-waivable. This behavioral equality is exercised directly by pytest.

## B-REG-002

### Meaning

Every dispatched language-server class must be concrete and instantiable at the class level.

### Typical fix

Implement missing abstract methods or correct the dispatch class.

### Waiver guidance

Waivable for an exact backend only while the Python staleness mirror continues to prove the failure exists.

## B-SKIP-001

### Meaning

The live disabled-language guard must implement each declared skip category across OS, CI, and tool-presence states.

### Typical fix

Align `test/conftest.py` guard logic and the backend skip-policy declaration.

### Waiver guidance

Non-waivable. The simulation matrix must match executable behavior.

## B-GATE-001

### Meaning

Every named invalid fixture must fail with its intended invariant id and offending subject.

### Typical fix

Repair the invariant, diagnostic mapping, or fixture so the expected rejection is explicit.

### Waiver guidance

Non-waivable. Negative-contract behavior is part of the gate's acceptance proof.

## B-GATE-002

### Meaning

The cheap contract job must run before, and gate, every expensive CPU matrix job with the exact local commands.

### Typical fix

Restore the contract job shape, command order, cache, timeout, and `needs` edge in the workflow.

### Waiver guidance

Non-waivable. The upstream cost-control and fail-fast topology is a gate invariant.
