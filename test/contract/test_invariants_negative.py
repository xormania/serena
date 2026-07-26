"""Rejection diagnostics for registration, testing, and waiver invariants."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from scripts.lsp_contract.diagnostics import diagnostic_ids, diagnostic_subjects, render_cue_diagnostics
from test.contract.invariant_support import FIXTURES, InvariantCase, discover_cases, load_case, validate_fixture
from test.contract.test_invariants_positive import VALID_CASES

INVALID_CASES = [
    "c-reg-001-missing-decl",
    "c-reg-001-orphan-decl",
    "c-reg-002-dispatch-missing",
    "c-reg-003-matcher-missing",
    "c-reg-004-status-drift",
    "c-reg-005-alt-as-language",
    "c-reg-006-two-defaults",
    "c-reg-007-template-stale",
    "c-test-001-marker-missing",
    "c-test-002-fixture-missing",
    "c-test-003-testdir-missing",
    "c-test-004-orphan-marker",
    "c-test-005-dup-alias",
    "c-test-006-untested-unwaived",
    "c-prov-001-shape",
    "c-prov-002-cargo-unlocked",
    "c-prov-002-command-missing",
    "c-prov-002-command-undeclared",
    "c-prov-003-sha-missing",
    "c-prov-003-sha-opaque",
    "c-prov-003-omnisharp-integrity-missing",
    "c-prov-003-no-evidence",
    "c-prov-004-unpinned",
    "c-prov-005-platform-no-path",
    "c-prov-005-path-outside-support",
    "c-prov-006-owner-ambiguous",
    "c-plat-001-unexcluded",
    "c-plat-001-overlap",
    "c-plat-001-reason-missing",
    "c-ci-001-batch-mismatch",
    "c-ci-002-invalid-batch",
    "c-ci-003-duplicate-batch",
    "c-ci-004-catchall-conflict",
    "c-ci-005-step-missing",
    "c-ci-006-os-outside-batch",
    "c-ci-007-no-timeout",
    "c-cache-001-input-uncovered",
    "c-cache-001-source-drift",
    "c-cache-001-waiver-scope",
    "c-cache-002-restore-prefix",
    "c-cache-002-waiver-scope",
    "c-cache-002-token-omitted-waived",
    "c-skip-001-malformed",
    "c-skip-002-ci-silent-skip",
    "c-fix-001-opaque-shell",
    "c-fix-001-missing-evidence",
    "c-fix-002-masked-bootstrap",
    "c-fix-003-no-postcondition",
    "c-cap-001-claim-no-evidence",
    "c-cap-001-evidence-no-claim",
    "c-gen-001-stale-output",
    "c-doc-001-doclabel-missing",
    "c-waive-001-stale",
]

CATEGORIES = {
    "C_REG": "registration",
    "C_TEST": "testing",
    "C_PROV": "provisioning",
    "C_PLAT": "platform",
    "C_CI": "ci placement",
    "C_CACHE": "cache",
    "C_SKIP": "skip policy",
    "C_FIX": "fixture bootstrap",
    "C_CAP": "capability",
    "C_GEN": "generated output",
    "C_DOC": "documentation",
    "C_WAIVE": "waiver hygiene",
}


CASE_MANIFEST_NAME = "declarations.json"
CASE_SECTIONS = ("declarations", "extracted", "expected")
PRE_MIGRATION_INVENTORY_DIGEST = "ee5564b801bfff605cf65580b000141e2f15b042aaed910785e2a33abb34831d"
PRE_MIGRATION_OUTCOME_DIGEST = "613045dcb5d52422e50575ebe5bada97b5160cab03411ceea4d5ec18ff97334f"


def _case_manifest(
    *,
    declarations: dict[str, Any] | None = None,
    extracted: dict[str, Any] | None = None,
    expected: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "declarations": declarations if declarations is not None else {"operations": []},
        "extracted": extracted if extracted is not None else {"operations": []},
        "expected": expected if expected is not None else {"result": "accepted"},
    }


def _write_case_manifest(case_dir: Path, payload: dict[str, Any] | str) -> Path:
    case_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = case_dir / CASE_MANIFEST_NAME
    text = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    manifest_path.write_text(text + "\n", encoding="utf-8", newline="\n")
    return manifest_path


def _load_case(case_dir: Path) -> InvariantCase:
    return load_case(case_dir)


def _discover_cases(root: Path) -> tuple[InvariantCase, ...]:
    return discover_cases(root)


def _inventory_digest(cases: tuple[InvariantCase, ...]) -> str:
    digest = hashlib.sha256()
    for case in cases:
        record = {
            "id": case.case_id,
            "declarations": case.declarations,
            "extracted": case.extracted,
            "expected": case.expected,
        }
        encoded = json.dumps(record, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def _outcome_snapshot(cases: tuple[InvariantCase, ...]) -> tuple[str, tuple[int, int, int, int]]:
    digest = hashlib.sha256()
    accepted = 0
    rejected = 0
    diagnostic_count = 0
    subject_count = 0
    for case in cases:
        returncode, stdout, stderr = validate_fixture(case.case_dir)
        ids = diagnostic_ids(stderr)
        diagnostics = [{"id": diagnostic_id, "subjects": diagnostic_subjects(stderr, diagnostic_id)} for diagnostic_id in ids]
        record = {
            "id": case.case_id,
            "returncode": returncode,
            "stdout": json.loads(stdout) if stdout else None,
            "diagnostics": diagnostics,
        }
        encoded = json.dumps(record, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
        accepted += returncode == 0
        rejected += returncode == 1
        diagnostic_count += len(diagnostics)
        subject_count += sum(len(diagnostic["subjects"]) for diagnostic in diagnostics)
    return digest.hexdigest(), (accepted, rejected, diagnostic_count, subject_count)


@pytest.mark.parametrize("case_name", INVALID_CASES, ids=lambda case: case.replace("-", "_"))
def test_invalid_fixture_is_rejected_with_stable_diagnostic(case_name: str) -> None:
    case_dir = FIXTURES / "invalid" / case_name
    expected = load_case(case_dir).expected
    returncode, _, stderr = validate_fixture(case_dir)

    diagnostic = expected["diagnostic"]
    prefix = diagnostic.rsplit("_", 1)[0]
    assert expected["category"] == CATEGORIES[prefix]
    assert returncode == 1, f"expected rejection {diagnostic}, got exit {returncode}:\n{stderr}"

    raw_path = expected.get("raw_path")
    if raw_path is not None:
        assert raw_path in stderr
        diagnostic_output = render_cue_diagnostics(stderr)
    else:
        diagnostic_output = stderr
    assert diagnostic in diagnostic_output
    assert expected["subject"] in diagnostic_output


def test_all_named_rejection_fixture_files_exist() -> None:
    for kind, case_names in (("valid", VALID_CASES), ("invalid", INVALID_CASES)):
        for case_name in case_names:
            case_dir = FIXTURES / kind / case_name
            assert case_dir.is_dir()
            assert {path.name for path in case_dir.iterdir()} == {CASE_MANIFEST_NAME}


def test_documentation_labels_do_not_accept_substring_only_matches(tmp_path: Path) -> None:
    declarations = {
        "operations": [{"op": "set", "path": ["languages", "ruby", "docLabel"], "value": "R"}],
    }
    _write_case_manifest(tmp_path, _case_manifest(declarations=declarations))

    returncode, _, stderr = validate_fixture(tmp_path)

    assert returncode == 1
    assert "C_DOC_001" in stderr
    assert "README.md" in stderr


class TestInvariantCaseManifest:
    def test_loads_sections_without_semantic_transformation(self, tmp_path: Path) -> None:
        declarations = {
            "operations": [
                {"op": "set", "path": ["languages", "ruby", "docLabel"], "value": "Rüby"},
            ],
        }
        extracted = {
            "operations": [
                {"op": "append", "path": ["pythonEnum"], "value": "ruby"},
            ],
        }
        expected = {
            "diagnostic": "C_TEST_001",
            "subject": "ruby",
            "nested": {"values": [1, False, None, "naïve"]},
        }
        _write_case_manifest(
            tmp_path,
            _case_manifest(declarations=declarations, extracted=extracted, expected=expected),
        )

        case = _load_case(tmp_path)

        assert case.declarations == declarations
        assert case.extracted == extracted
        assert case.expected == expected

    @pytest.mark.parametrize(
        ("payload", "message"),
        [
            (
                {"declarations": {"operations": []}, "extracted": {"operations": []}},
                "missing.*expected",
            ),
            (
                {**_case_manifest(), "notes": {}},
                "unknown.*notes",
            ),
            (
                '{"declarations":{"operations":[]},"extracted":{"operations":[]},"expected":',
                "malformed",
            ),
            (
                ('{"declarations":{"operations":[]},"extracted":{"operations":[]},"expected":{},"expected":{"duplicate":true}}'),
                "duplicate.*expected",
            ),
            (
                {**_case_manifest(), "extracted": []},
                "extracted.*object",
            ),
        ],
        ids=["missing", "unknown", "malformed", "duplicate", "wrong-type"],
    )
    def test_rejects_incomplete_or_ambiguous_manifests(
        self,
        tmp_path: Path,
        payload: dict[str, Any] | str,
        message: str,
    ) -> None:
        _write_case_manifest(tmp_path, payload)

        with pytest.raises(ValueError, match=message):
            _load_case(tmp_path)

    def test_discovers_every_case_once_with_stable_ids_and_order(self, tmp_path: Path) -> None:
        for relative_path in ("valid/zeta", "valid/alpha", "invalid/beta"):
            _write_case_manifest(tmp_path / relative_path, _case_manifest())

        cases = _discover_cases(tmp_path)

        assert tuple(case.case_id for case in cases) == ("valid/alpha", "valid/zeta", "invalid/beta")
        assert len({case.case_dir for case in cases}) == 3

    def test_discovery_cannot_silently_skip_an_invalid_case(self, tmp_path: Path) -> None:
        _write_case_manifest(tmp_path / "valid" / "good", _case_manifest())
        (tmp_path / "invalid" / "broken").mkdir(parents=True)

        with pytest.raises(ValueError, match="broken.*manifest"):
            _discover_cases(tmp_path)

    def test_live_inventory_matches_the_pre_migration_snapshot(self) -> None:
        cases = _discover_cases(FIXTURES)
        expected_ids = (
            *(f"valid/{case_name}" for case_name in sorted(VALID_CASES)),
            *(f"invalid/{case_name}" for case_name in sorted(INVALID_CASES)),
        )
        observed_ids = tuple(case.case_id for case in cases)

        assert observed_ids == expected_ids
        assert len(observed_ids) == 75
        assert len(set(observed_ids)) == 75
        assert _inventory_digest(cases) == PRE_MIGRATION_INVENTORY_DIGEST

    def test_live_outcomes_match_the_pre_migration_snapshot(self) -> None:
        snapshot, counts = _outcome_snapshot(_discover_cases(FIXTURES))

        assert counts == (22, 53, 66, 97)
        assert snapshot == PRE_MIGRATION_OUTCOME_DIGEST
