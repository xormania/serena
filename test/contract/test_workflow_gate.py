"""P8 workflow gate and reporting contract tests."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any, cast

import pytest

import scripts.lsp_contract.__main__ as contract_cli
from scripts.lsp_contract.cue_runtime import CueRuntime
from scripts.lsp_contract.diagnostics import DIAGNOSTICS, ExtractionError, render_github_failure_summary
from scripts.lsp_contract.extract.workflow_yaml import extract_workflow

ROOT = Path(__file__).parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "pytest.yml"
PYPROJECT = ROOT / "pyproject.toml"


def _workflow_document() -> dict[str, Any]:
    returncode, stdout, stderr = CueRuntime().run(["export", "--out", "json"], [WORKFLOW])
    assert returncode == 0, stderr
    return cast(dict[str, Any], json.loads(stdout))


def _poe_tasks() -> dict[str, object]:
    document = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    return cast(dict[str, object], document["tool"]["poe"]["tasks"])


def test_contract_job_gates_the_cpu_matrix() -> None:
    extracted = extract_workflow(WORKFLOW)
    jobs = {str(job["name"]): job for job in cast(list[dict[str, object]], extracted["jobs"])}

    assert "contract" in jobs, "expected job 'contract' in workflow"
    assert jobs["contract"]["timeoutMinutes"] == 10
    assert jobs["cpu"]["needs"] == ["contract"]


def test_contract_job_has_the_exact_cheap_platform_shape() -> None:
    contract_job = _workflow_document()["jobs"]["contract"]
    steps = contract_job["steps"]

    assert contract_job["name"] == "contract (language/CI declarations)"
    assert contract_job["runs-on"] == "ubuntu-latest"
    assert contract_job["timeout-minutes"] == 10
    assert steps[0] == {"uses": "actions/checkout@v4"}
    assert steps[1]["uses"] == "actions/setup-python@v4"
    assert steps[1]["with"] == {"python-version": "3.11"}
    assert all("uv sync" not in str(step.get("run", "")) for step in steps)
    assert all("setup-uv" not in str(step.get("uses", "")) for step in steps)


def test_contract_job_caches_the_pinned_cue_toolchain() -> None:
    contract_steps = _workflow_document()["jobs"]["contract"]["steps"]
    cache = next(step for step in contract_steps if step.get("name") == "Cache CUE toolchain")

    assert cache["uses"] == "actions/cache@v3"
    assert cache["with"]["path"] == "~/.serena/dev_tools/cue"
    assert cache["with"]["key"] == "cue-toolchain-${{ runner.os }}-${{ hashFiles('contract/cue-version.json') }}"


def test_contract_job_runs_install_then_validate_exactly_once() -> None:
    contract_steps = _workflow_document()["jobs"]["contract"]["steps"]
    run_commands = [step.get("run") for step in contract_steps if step.get("run")]

    assert run_commands == [
        "python -m scripts.lsp_contract install-cue",
        "python -m scripts.lsp_contract validate --github-summary",
    ]


def test_poe_contract_tasks_match_the_plan() -> None:
    tasks = _poe_tasks()

    assert tasks["_contract_install"] == "python -m scripts.lsp_contract install-cue"
    assert tasks["_contract_validate"] == "python -m scripts.lsp_contract validate"
    assert tasks["check-contract"] == ["_contract_install", "_contract_validate"]


def test_local_and_ci_gate_commands_are_semantically_identical() -> None:
    tasks = _poe_tasks()
    local_commands = [tasks["_contract_install"], tasks["_contract_validate"]]
    contract_steps = _workflow_document()["jobs"]["contract"]["steps"]
    ci_commands = [step["run"] for step in contract_steps if step.get("run")]

    assert ci_commands[0] == local_commands[0]
    assert ci_commands[1].removesuffix(" --github-summary") == local_commands[1]


def test_explain_prints_registered_meaning_and_fix(capsys: pytest.CaptureFixture[str]) -> None:
    assert contract_cli.main(["explain", "C-REG-001"]) == 0

    output = capsys.readouterr().out
    assert DIAGNOSTICS["C-REG-001"].meaning in output
    assert DIAGNOSTICS["C-REG-001"].fix in output


def test_explain_covers_extractor_drift(capsys: pytest.CaptureFixture[str]) -> None:
    assert contract_cli.main(["explain", "C-EXTR-001"]) == 0

    output = capsys.readouterr().out
    assert DIAGNOSTICS["C-EXTR-001"].meaning in output
    assert DIAGNOSTICS["C-EXTR-001"].fix in output


def test_explain_rejects_an_unknown_invariant(capsys: pytest.CaptureFixture[str]) -> None:
    assert contract_cli.main(["explain", "C-NOT-REAL"]) == 2
    assert "unknown invariant: C-NOT-REAL" in capsys.readouterr().err


def test_github_summary_reports_contract_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    summary_path = tmp_path / "summary.md"
    extracted_path = tmp_path / "extracted.json"
    extracted_path.write_text('{"extracted": {}}\n', encoding="utf-8")
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_path))
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_REPOSITORY", "xormania/serena")
    monkeypatch.setenv("GITHUB_SHA", "deadbeef")
    monkeypatch.setattr(contract_cli, "write_extracted", lambda _root, _output: extracted_path)
    monkeypatch.setattr(contract_cli, "_vet_schema", lambda _root: 0)
    monkeypatch.setattr(
        contract_cli.CueRuntime,
        "run",
        lambda _self, _args, _files=(): (
            1,
            "",
            'C_REG_001.python: conflicting values false and "backend declaration is missing"\n',
        ),
    )

    assert contract_cli.main(["validate", "--github-summary", "--root", str(ROOT)]) == 1
    summary = summary_path.read_text(encoding="utf-8")
    expected_row = (
        f"| C-REG-001 | {DIAGNOSTICS['C-REG-001'].meaning} | python | {DIAGNOSTICS['C-REG-001'].fix} | "
        "[details](https://github.com/xormania/serena/blob/deadbeef/contract/INVARIANTS.md#c-reg-001) |"
    )
    assert expected_row in summary
    assert summary in capsys.readouterr().err


def test_github_summary_extracts_subject_for_schema_mapped_diagnostic() -> None:
    summary = render_github_failure_summary("backends.python.testing.bootstrap.produces: incomplete value []\n")

    expected_row = (
        f"| C-FIX-003 | {DIAGNOSTICS['C-FIX-003'].meaning} | python | {DIAGNOSTICS['C-FIX-003'].fix} | "
        "[details](contract/INVARIANTS.md#c-fix-003) |"
    )
    assert expected_row in summary


def test_github_summary_distinguishes_extractor_drift(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    summary_path = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_path))

    def drift(_root: Path, _output: Path | None) -> Path:
        raise ExtractionError(ROOT / "pyproject.toml", 17, "unknown marker shape")

    monkeypatch.setattr(contract_cli, "write_extracted", drift)

    assert contract_cli.main(["validate", "--github-summary", "--root", str(ROOT)]) == 2
    summary = summary_path.read_text(encoding="utf-8")
    assert "C-EXTR-001" in summary
    assert "repo structure changed" in summary
    assert "pyproject.toml:17" in summary
    assert "fix scripts/lsp_contract/extract" in summary
    assert summary in capsys.readouterr().err
