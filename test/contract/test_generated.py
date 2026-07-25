"""Generated contract artifact and drift-gate tests."""

from __future__ import annotations

import importlib
import json
import re
import subprocess
from pathlib import Path
from typing import cast

import pytest

from scripts.lsp_contract import __main__ as contract_cli
from scripts.lsp_contract.diagnostics import ExtractionError
from scripts.lsp_contract.extract.assemble import extract_repository
from scripts.lsp_contract.extract.docs_presence import extract_docs
from test.contract.invariant_support import FIXTURES, validate_fixture

ROOT = Path(__file__).parents[2]
REGISTRATION = ROOT / "contract" / "REGISTRATION.md"
TEMPLATE = ROOT / "src" / "serena" / "resources" / "project.template.yml"
BEGIN_MARKER = "# BEGIN generated language list"
END_MARKER = "# END generated language list"


def _render_module():
    return importlib.import_module("scripts.lsp_contract.render")


def test_registration_renderer_is_complete_deterministic_and_ordered() -> None:
    render = _render_module()
    backends = render.load_backends(ROOT)

    first = render.render_registration_text(backends)
    second = render.render_registration_text(backends)

    assert first == second
    assert first.endswith("\n")
    assert "\r" not in first
    assert "DO NOT EDIT" in first
    assert "python -m scripts.lsp_contract render-registration" in first

    pairs: list[tuple[str, int]] = []
    group_names: list[str] = []
    backend_ids: list[str] = []
    current_backend: str | None = None
    prior_surface = 0
    for line in first.splitlines():
        if line.startswith("## Integration class: "):
            group_names.append(line.removeprefix("## Integration class: "))
            current_backend = None
        elif match := re.fullmatch(r"### `([a-z][a-z0-9_]*)`(?: — .+)?", line):
            current_backend = match.group(1)
            backend_ids.append(current_backend)
            prior_surface = 0
        elif match := re.match(r"\| (10|[1-9]) \|", line):
            assert current_backend is not None
            surface = int(match.group(1))
            assert surface == prior_surface + 1
            prior_surface = surface
            pairs.append((current_backend, surface))

    assert len(backends) == 69
    assert len(group_names) == len(set(group_names))
    assert backend_ids == list(dict.fromkeys(backend_ids))
    assert set(pairs) == {(backend_id, surface) for backend_id in backends for surface in range(1, 11)}
    assert len(pairs) == len(backends) * 10
    for exemplar in ("gdscript", "msl", "hlsl", "svelte", "ruby", "qml", "swift", "python_basedpyright"):
        assert exemplar in backend_ids
    assert "src/solidlsp/language_servers/elixir_tools/elixir_tools.py" in first
    assert "contract-authoritative + declared" in first
    assert "contract-derived + generated" in first
    assert "C-REG-005" in first
    assert "C-REG-006" in first


def test_template_renderer_migrates_legacy_block_and_is_idempotent() -> None:
    render = _render_module()
    backends = render.load_backends(ROOT)
    original = TEMPLATE.read_text(encoding="utf-8")

    first = render.render_template_text(original, backends)
    second = render.render_template_text(first, backends)

    assert first == second
    assert first.count(BEGIN_MARKER) == 1
    assert first.count(END_MARKER) == 1
    assert "# - qml\n" in first
    assert "# - python_basedpyright\n" in first
    assert "LanguageServerId" in first
    assert "values of Language enum" not in first
    start = first.index(BEGIN_MARKER)
    end = first.index(END_MARKER)
    generated_lines = first[start:end].splitlines()[1:]
    assert generated_lines == [f"# - {backend_id}" for backend_id in sorted(backends)]


def test_template_renderer_preserves_text_outside_markers_and_rejects_bad_markers() -> None:
    render = _render_module()
    source = "prefix\n# BEGIN generated language list\n# - stale\n# END generated language list\nsuffix\n"
    rendered = render.render_template_text(source, {"qml": {}, "ada": {}})
    assert rendered.startswith("prefix\n")
    assert rendered.endswith("suffix\n")
    assert "# - ada\n# - qml\n" in rendered

    malformed = "prefix\n# BEGIN generated language list\n# - ada\n"
    with pytest.raises(ExtractionError, match="END generated language list"):
        render.render_template_text(malformed, {"ada": {}})

    duplicated = source.replace("prefix\n", f"prefix\n{BEGIN_MARKER}\n")
    with pytest.raises(ExtractionError, match="exactly one"):
        render.render_template_text(duplicated, {"ada": {}})


def test_committed_generated_artifacts_are_byte_current() -> None:
    render = _render_module()
    backends = render.load_backends(ROOT)
    assert REGISTRATION.read_bytes() == render.render_registration_text(backends).encode("utf-8")
    assert TEMPLATE.read_bytes() == render.render_template_text(TEMPLATE.read_text(encoding="utf-8"), backends).encode("utf-8")
    assert render.artifact_freshness(ROOT, backends=backends) == {
        "registrationCurrent": True,
        "templateCurrent": True,
    }


def test_contract_sources_and_generated_artifacts_checkout_as_lf() -> None:
    relative_paths = sorted(path.relative_to(ROOT).as_posix() for path in (ROOT / "contract").rglob("*.cue"))
    relative_paths.extend([REGISTRATION.relative_to(ROOT).as_posix(), TEMPLATE.relative_to(ROOT).as_posix()])
    completed = subprocess.run(
        ["git", "check-attr", "eol", "--", *relative_paths],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    attributes = dict(line.rsplit(": eol: ", 1) for line in completed.stdout.splitlines())
    assert attributes == dict.fromkeys(relative_paths, "lf")


def test_render_cli_subcommands_write_requested_outputs(tmp_path: Path) -> None:
    registration = tmp_path / "REGISTRATION.md"
    template = tmp_path / "project.template.yml"

    assert contract_cli.main(["render-registration", "--root", str(ROOT), "--output", str(registration)]) == 0
    assert contract_cli.main(["render-template-list", "--root", str(ROOT), "--output", str(template)]) == 0
    assert registration.read_text(encoding="utf-8").startswith("<!-- DO NOT EDIT")
    assert BEGIN_MARKER in template.read_text(encoding="utf-8")


def test_validate_stages_external_extracted_facts_for_cue(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    extracted_path = (tmp_path / "facts.json").resolve()
    extracted_path.write_text('{"extracted": {}}\n', encoding="utf-8")
    assert not extracted_path.is_relative_to(ROOT)

    monkeypatch.setattr(contract_cli, "write_extracted", lambda _root, _output: extracted_path)
    monkeypatch.setattr(contract_cli, "_vet_schema", lambda _root: 0)
    observed_inputs: list[Path] = []

    def recording_run(_self, args, _input_files=()):
        cue_input = Path(args[2]).resolve()
        observed_inputs.append(cue_input)
        assert cue_input != extracted_path
        assert cue_input.is_relative_to(ROOT)
        assert cue_input.read_bytes() == extracted_path.read_bytes()
        return 1, "", 'C_GEN_001.registration: conflicting values false and "generated artifact is stale"\n'

    monkeypatch.setattr(contract_cli.CueRuntime, "run", recording_run)

    assert contract_cli.main(["validate", "--root", str(ROOT), "--output", str(extracted_path)]) == 1
    assert extracted_path.exists()
    assert len(observed_inputs) == 1
    assert not observed_inputs[0].exists()


def test_tampered_registration_is_stale_and_validate_rejects_it(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    render = _render_module()
    backends = render.load_backends(ROOT)
    tampered = tmp_path / "REGISTRATION.md"
    tampered.write_text(render.render_registration_text(backends) + "tampered\n", encoding="utf-8")
    freshness = render.artifact_freshness(ROOT, backends=backends, registration_path=tampered)
    assert freshness["registrationCurrent"] is False

    def stale_write(root: Path, output_path: Path | None = None, *, include_freshness: bool = True) -> Path:
        assert include_freshness is True
        destination = output_path or tmp_path / "extracted.json"
        document = extract_repository(root, include_freshness=False)
        extracted = cast(dict[str, object], document["extracted"])
        extracted["freshness"] = freshness
        destination.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return destination

    monkeypatch.setattr(contract_cli, "write_extracted", stale_write)
    assert contract_cli.main(["validate", "--root", str(ROOT), "--output", str(tmp_path / "facts.json")]) == 1
    captured = capsys.readouterr()
    assert "C_GEN_001" in captured.err
    assert "contract/REGISTRATION.md" in captured.err


@pytest.mark.parametrize(
    ("case_name", "diagnostic", "subject"),
    [
        ("c-gen-001-stale-output", "C_GEN_001", "contract/REGISTRATION.md"),
        ("c-doc-001-doclabel-missing", "C_DOC_001", "README.md"),
    ],
)
def test_generated_rejection_fixtures(case_name: str, diagnostic: str, subject: str) -> None:
    returncode, _, stderr = validate_fixture(FIXTURES / "invalid" / case_name)
    assert returncode == 1
    assert diagnostic in stderr
    assert subject in stderr


@pytest.mark.parametrize(
    ("field", "required"),
    [
        (
            "readmeLabels",
            {"Pascal", "QML", "Rego", "SystemVerilog", "Terraform", "Vue"},
        ),
        (
            "docsLabels",
            {"MATLAB", "PowerShell", "Rego", "SystemVerilog", "Terraform", "TOML"},
        ),
    ],
)
def test_od2_authored_language_lists_include_missing_labels(
    field: str,
    required: set[str],
) -> None:
    actual = extract_docs(ROOT)[field]
    assert isinstance(actual, list)
    missing = {label for label in required if not any(label.casefold() in str(item).casefold() for item in actual)}
    assert missing == set()


def test_legacy_print_helper_is_explicitly_deprecated() -> None:
    source = (ROOT / "scripts" / "print_language_list.py").read_text(encoding="utf-8")
    assert "deprecated" in source.lower()
    assert "render-template-list" in source
