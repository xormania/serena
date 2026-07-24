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
    "C-CI-002": ContractDiagnostic(
        "CI batch declarations are restricted to the workflow matrix batch enum.",
        "Use a batch present in the workflow matrix.",
    ),
    "C-SKIP-001": ContractDiagnostic(
        "Skip-policy declarations must include the fields required by their category.",
        "Add loudOn for category 2 or waiver and reason for categories 1 and 5.",
    ),
    "C-PROV-001": ContractDiagnostic(
        "Provisioning declarations must satisfy their strategy-specific schema.",
        "Add the fields required by the selected provisioning strategy.",
    ),
    "C-PROV-006": ContractDiagnostic(
        "Provisioning ownership must name one runtime owner and one CI owner.",
        "Declare both provisioning.owner.runtime and provisioning.owner.ci.",
    ),
    "C-FIX-003": ContractDiagnostic(
        "Required bootstrap declarations must name at least one produced artifact.",
        "Add a concrete testing.bootstrap.produces postcondition.",
    ),
}


_SCHEMA_PATH_DIAGNOSTICS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"[.]ci[.]batch(?=[:.]|$)"), "C-CI-002"),
    (re.compile(r"[.]ci[.]skipPolicy(?:[.]|:)"), "C-SKIP-001"),
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
