"""Stable diagnostics for contract extraction and validation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExtractionError(RuntimeError):
    """Error raised when a repository source shape cannot be extracted safely."""

    path: Path
    line: int
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


@dataclass(frozen=True)
class ContractDiagnostic:
    """Stable diagnostic metadata shared by validation and troubleshooting views."""

    meaning: str
    fix: str


DIAGNOSTICS: dict[str, ContractDiagnostic] = {
    "C-REG-001": ContractDiagnostic(
        "Backend declarations and LanguageServerId members must be the same set.",
        "Add or remove the declaration so both registration surfaces agree.",
    ),
    "C-REG-002": ContractDiagnostic(
        "Every backend must have a dispatch arm matching its declared module and class.",
        "Update the declaration or LanguageServerId.get_ls_class dispatch arm.",
    ),
    "C-REG-003": ContractDiagnostic(
        "Every backend must resolve to its own or a declared shared matcher arm.",
        "Add the matcher arm or correct matcher.sharedArmWith.",
    ),
    "C-REG-004": ContractDiagnostic(
        "Declared stability must agree with the extracted experimental set.",
        "Align backend.status with LanguageServerId.is_experimental().",
    ),
    "C-REG-005": ContractDiagnostic(
        "Alternate backends must reuse a language owned by an existing default backend.",
        "Point the alternate at the default backend's language.",
    ),
    "C-REG-006": ContractDiagnostic(
        "Each language has exactly one default, while a sole language has one backend.",
        "Correct backend roles or the language defaultBackend declaration.",
    ),
    "C-REG-007": ContractDiagnostic(
        "The project template language-server list must contain every registered backend.",
        "Regenerate the template language-server list.",
    ),
    "C-TEST-001": ContractDiagnostic(
        "Every tested backend marker must be declared in pyproject.toml.",
        "Declare the marker or correct the backend testing marker.",
    ),
    "C-TEST-002": ContractDiagnostic(
        "Every tested backend must resolve to an existing fixture repository.",
        "Add the fixture repository or correct fixtureRepo and aliasOf.",
    ),
    "C-TEST-003": ContractDiagnostic(
        "Every tested backend must name an existing solidlsp test directory.",
        "Add the test directory or correct testing.testDir.",
    ),
    "C-TEST-004": ContractDiagnostic(
        "Every language marker must be owned by a backend unless explicitly informational.",
        "Declare the backend marker or remove the orphan marker.",
    ),
    "C-TEST-005": ContractDiagnostic(
        "Conftest aliases and marker mappings must be unique and cover tested alternates.",
        "Remove duplicate keys and add the alternate alias and marker mapping.",
    ),
    "C-TEST-006": ContractDiagnostic(
        "Every untested backend requires an explicit current waiver.",
        "Add tests or add the reviewed untested-backend waiver.",
    ),
    "C-WAIVE-001": ContractDiagnostic(
        "Every waiver must identify a current violation and carry complete rationale.",
        "Remove stale waivers or repair the id, subject, reason, and reference.",
    ),
    "C-CI-001": ContractDiagnostic(
        "Tested backends must agree with their declared workflow batch or carry a current never-run waiver.",
        "Correct the marker batch, enable the backend in CI, or register the exact reviewed never-run waiver.",
    ),
    "C-CI-002": ContractDiagnostic(
        "CI batch declarations are restricted to the workflow matrix batch enum.",
        "Use a batch present exactly once in the workflow matrix.",
    ),
    "C-CI-003": ContractDiagnostic(
        "A test marker may occur in at most one named workflow batch group.",
        "Remove the duplicate marker from the incorrect workflow group.",
    ),
    "C-CI-004": ContractDiagnostic(
        "Catch-all backend markers must not occur in a named workflow group.",
        "Remove the marker from named groups or declare its actual batch.",
    ),
    "C-CI-005": ContractDiagnostic(
        "CI provisioning ownership must resolve to one exact non-opaque install step covering the declared batch and OS set.",
        "Correct ci.installStep and its workflow gates, or declare runtime or image ownership from evidence.",
    ),
    "C-CI-006": ContractDiagnostic(
        "Declared batch OS intent must equal the effective matrix and remain within backend platform support.",
        "Correct ci.os, ciLayout batch OS intent, matrix exclusions, or platform declarations.",
    ),
    "C-CI-007": ContractDiagnostic(
        "Every workflow job must declare a positive timeout-minutes value.",
        "Add a positive timeout-minutes value to the workflow job.",
    ),
    "C-CACHE-001": ContractDiagnostic(
        "Every declared cache must exactly cover its backend inputs with key tokens and execution gates, unless reviewed and waived.",
        "Bind the exact extracted cache, add every provisioning input and token to its key, or register the current cache waiver.",
    ),
    "C-CACHE-002": ContractDiagnostic(
        "Cache schema version tokens must occur in the key and every restore prefix.",
        "Include the declared version token in the cache key and every restore-keys prefix.",
    ),
    "C-SKIP-001": ContractDiagnostic(
        "Skip-policy declarations must include the fields required by their category.",
        "Add loudOn for category 2 or waiver and reason for categories 1 and 5.",
    ),
    "C-PROV-001": ContractDiagnostic(
        "Provisioning declarations must satisfy their strategy-specific schema.",
        "Add the fields required by the selected provisioning strategy.",
    ),
    "C-PROV-002": ContractDiagnostic(
        "Source-build declarations and Cargo install commands must agree and use lock discipline.",
        "Declare the source-build leaf and retain --locked in every extracted cargo install command.",
    ),
    "C-PROV-003": ContractDiagnostic(
        "Default-version downloads require checksum evidence and an aligned download declaration.",
        "Add the missing sha256 or integrity, or align the provisioning strategy with the source.",
    ),
    "C-PROV-004": ContractDiagnostic(
        "Package-manager provisioning must be pinned or use a current matching waiver.",
        "Pin the package-manager install or register the declaration's exact waiver id and subject.",
    ),
    "C-PROV-005": ContractDiagnostic(
        "Declared platform support must agree with provable or explicitly opaque provisioning paths.",
        "Add structured platform evidence, correct support intent, or register the reviewed opacity waiver.",
    ),
    "C-PROV-006": ContractDiagnostic(
        "Provisioning ownership must name one runtime owner and one CI owner.",
        "Declare both provisioning.owner.runtime and provisioning.owner.ci.",
    ),
    "C-PLAT-001": ContractDiagnostic(
        "Supported and excluded platforms must form an exact three-OS partition with reasons.",
        "Place each OS exactly once and provide a non-empty reason for every exclusion.",
    ),
    "C-FIX-003": ContractDiagnostic(
        "Required bootstrap declarations must name at least one produced artifact.",
        "Add a concrete testing.bootstrap.produces postcondition.",
    ),
}


_SCHEMA_PATH_DIAGNOSTICS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"[.]ci[.]batch(?=[:.]|$)"), "C-CI-002"),
    (re.compile(r"[.]ci[.]skipPolicy(?:[.]|:)"), "C-SKIP-001"),
    (re.compile(r"[.]platforms[.]excluded[.]\d+[.]reason(?=[:.]|$)"), "C-PLAT-001"),
    (re.compile(r"[.]provisioning[.]owner(?:[.]|:)"), "C-PROV-006"),
    (re.compile(r"[.]testing[.]bootstrap[.]produces(?=[:.]|$)"), "C-FIX-003"),
    (
        re.compile(
            r"[.]provisioning[.](?:pin|checksums|hosts|executables|package|packages|manager|host|port|enginePin|primary|companions|lockDiscipline)(?=[:.]|$)"
        ),
        "C-PROV-001",
    ),
)
_INVARIANT_TOKEN = re.compile(r"\bC_([A-Z]+)_(\d{3})\b")


def diagnostic_ids(cue_stderr: str) -> tuple[str, ...]:
    """Return stable dashed diagnostic ids present in raw CUE stderr."""
    found = {f"C-{family}-{number}" for family, number in _INVARIANT_TOKEN.findall(cue_stderr)}
    found.update(diagnostic_id for path_pattern, diagnostic_id in _SCHEMA_PATH_DIAGNOSTICS if path_pattern.search(cue_stderr))
    return tuple(sorted(found))


def render_cue_diagnostics(cue_stderr: str) -> str:
    """Preserve raw CUE evidence and append stable ids with actionable hints."""
    raw = cue_stderr.rstrip()
    rendered = [raw] if raw else []
    for diagnostic_id in diagnostic_ids(cue_stderr):
        cue_field_id = diagnostic_id.replace("-", "_")
        diagnostic = DIAGNOSTICS.get(diagnostic_id)
        if diagnostic is None:
            rendered.append(cue_field_id)
            continue
        rendered.extend(
            (
                f"{cue_field_id} ({diagnostic_id}): {diagnostic.meaning}",
                f"  fix: {diagnostic.fix}",
            )
        )
    return "\n".join(rendered)
