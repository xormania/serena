"""Rejection diagnostics for registration, testing, and waiver invariants."""

from __future__ import annotations

import json

import pytest

from scripts.lsp_contract.diagnostics import render_cue_diagnostics
from test.contract.invariant_support import FIXTURES, validate_fixture

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


@pytest.mark.parametrize("case_name", INVALID_CASES, ids=lambda case: case.replace("-", "_"))
def test_invalid_fixture_is_rejected_with_stable_diagnostic(case_name: str) -> None:
    case_dir = FIXTURES / "invalid" / case_name
    expected = json.loads((case_dir / "expected.json").read_text())
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
    for case_name in INVALID_CASES:
        case_dir = FIXTURES / "invalid" / case_name
        assert case_dir.is_dir()
        assert {path.name for path in case_dir.iterdir()} == {
            "declarations.json",
            "expected.json",
            "extracted.json",
        }
