"""P8 workflow gate and reporting contract tests."""

from __future__ import annotations

import json
import subprocess
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


def _git_tracked_paths(root: Path) -> frozenset[str]:
    completed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached"],
        check=True,
        capture_output=True,
    )
    return frozenset(path.decode("utf-8") for path in completed.stdout.split(b"\0") if path)


def _initialize_reference_repository(root: Path, tracked_paths: tuple[str, ...]) -> None:
    subprocess.run(["git", "init", "--quiet", str(root)], check=True, capture_output=True)
    for relative_path in tracked_paths:
        evidence_path = root / relative_path
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text("review evidence\n", encoding="utf-8")
    if tracked_paths:
        subprocess.run(["git", "-C", str(root), "add", "--", *tracked_paths], check=True, capture_output=True)


def _run_waiver_reference_validation(
    monkeypatch: pytest.MonkeyPatch,
    root: Path,
    references: tuple[str, ...],
    *,
    github_summary: bool = False,
) -> int:
    extracted_path = root / "extracted.json"
    extracted_path.write_text('{"extracted": {}}\n', encoding="utf-8")
    waivers = {f"W-REFERENCE-{index}": {"reference": reference} for index, reference in enumerate(references)}

    monkeypatch.setattr(contract_cli, "write_extracted", lambda _root, _output: extracted_path)
    monkeypatch.setattr(contract_cli, "_vet_schema", lambda _root: 0)
    monkeypatch.setattr(
        contract_cli.CueRuntime,
        "run",
        lambda _self, _args, _input_files=(): (0, json.dumps({"waivers": waivers}), ""),
    )
    arguments = ["validate", "--root", str(root)]
    if github_summary:
        arguments.append("--github-summary")
    return contract_cli.main(arguments)


@pytest.mark.parametrize("reference", ["docs/evidence.md", "docs/evidence.md#review-anchor"])
def test_waiver_reference_accepts_tracked_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    reference: str,
) -> None:
    _initialize_reference_repository(tmp_path, ("docs/evidence.md",))

    assert _run_waiver_reference_validation(monkeypatch, tmp_path, (reference,)) == 0


def test_waiver_reference_rejects_missing_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _initialize_reference_repository(tmp_path, ("docs/evidence.md",))
    summary_path = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_path))

    assert _run_waiver_reference_validation(monkeypatch, tmp_path, ("docs/missing.md",), github_summary=True) == 1
    stderr = capsys.readouterr().err
    assert "C_WAIVE_001" in stderr
    assert "W-REFERENCE-0" in stderr
    assert "docs/missing.md" in stderr
    summary = summary_path.read_text(encoding="utf-8")
    assert "C-WAIVE-001" in summary
    assert "W-REFERENCE-0" in summary
    assert DIAGNOSTICS["C-WAIVE-001"].fix in summary


def test_waiver_reference_rejects_existing_untracked_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _initialize_reference_repository(tmp_path, ("docs/evidence.md",))
    (tmp_path / "local-only.md").write_text("unavailable to reviewers\n", encoding="utf-8")

    assert _run_waiver_reference_validation(monkeypatch, tmp_path, ("local-only.md",)) == 1
    stderr = capsys.readouterr().err
    assert "C_WAIVE_001" in stderr
    assert "local-only.md" in stderr


@pytest.mark.parametrize("reference", ["", "/outside.md", "../outside.md", "C:\\outside.md"])
def test_waiver_reference_rejects_empty_absolute_or_escaping_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    reference: str,
) -> None:
    _initialize_reference_repository(tmp_path, ("docs/evidence.md",))

    assert _run_waiver_reference_validation(monkeypatch, tmp_path, (reference,)) == 1


def test_waiver_reference_accepts_only_tracked_directories(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _initialize_reference_repository(tmp_path, ("docs/review/evidence.md",))
    (tmp_path / "empty").mkdir()

    assert _run_waiver_reference_validation(monkeypatch, tmp_path, ("docs/review",)) == 0
    assert _run_waiver_reference_validation(monkeypatch, tmp_path, ("empty",)) == 1


def test_waiver_reference_fails_loudly_without_git_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert _run_waiver_reference_validation(monkeypatch, tmp_path, ("evidence.md",)) == 2
    stderr = capsys.readouterr().err
    assert "C_WAIVE_001" in stderr
    assert "Git" in stderr


def test_live_waiver_references_resolve_to_tracked_evidence() -> None:
    returncode, stdout, stderr = CueRuntime().run(
        [
            "export",
            str(ROOT / "contract" / "schema_waiver.cue"),
            str(ROOT / "contract" / "declaration_waivers.cue"),
            "-e",
            "waivers",
            "--out",
            "json",
        ]
    )
    assert returncode == 0, stderr
    waivers = cast(dict[str, dict[str, str]], json.loads(stdout))
    tracked_paths = _git_tracked_paths(ROOT)
    invalid_references: dict[str, str] = {}
    for waiver_id, waiver in waivers.items():
        reference_path = waiver["reference"].split("#", 1)[0]
        tracked = reference_path in tracked_paths or any(path.startswith(f"{reference_path.rstrip('/')}/") for path in tracked_paths)
        if not tracked:
            invalid_references[waiver_id] = waiver["reference"]

    assert len(waivers) == 81
    assert invalid_references == {}


def test_committed_waiver_references_do_not_use_local_plan() -> None:
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(ROOT),
            "grep",
            "-n",
            "-F",
            "proj/cue/plan.md",
            "--",
            "contract",
            "test/contract/fixtures/invariants",
        ],
        check=False,
        capture_output=True,
    )

    assert completed.returncode == 1, completed.stdout.decode("utf-8")
