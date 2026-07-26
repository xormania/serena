"""Semantic conformance checks that exercise the imported Python implementation."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import pytest

import scripts.lsp_contract.decl_export as decl_export
import test.conftest as guard
from scripts.lsp_contract.decl_export import export_backends, export_waived_subjects
from scripts.lsp_contract.extract.assemble import write_extracted as assemble_write_extracted
from solidlsp.ls_config import LanguageServerId

_OS_SYSTEM = {"linux": "Linux", "macos": "Darwin", "windows": "Windows"}
_HELPER_PROBES: dict[str, str] = {
    "clojure": "is_clojure_cli_available",
    "MATLAB": "_is_matlab_available",
    "R:languageserver": "_is_r_language_server_available",
    "opam:ocaml-lsp-server": "_is_ocaml_lsp_available",
    "Perl::LanguageServer": "_is_perl_language_server_available",
}
_FLAG_PROBES: dict[str, str] = {
    "erlang_ls": "ERLANG_LS_UNAVAILABLE",
    "expert": "EXPERT_UNAVAILABLE",
}


@dataclass(frozen=True)
class _GuardCell:
    backend: str
    os_name: str
    ci: bool
    present: bool

    @property
    def id(self) -> str:
        return f"b_skip_001__{self.backend}__{self.os_name}__ci_{int(self.ci)}__tool_{int(self.present)}"


def _declared_extensions(
    backend_id: str,
    backends: Mapping[str, Mapping[str, Any]],
    seen: frozenset[str] = frozenset(),
) -> set[str]:
    assert backend_id not in seen, f"matcher sharing cycle at {backend_id}"
    matcher = backends[backend_id]["matcher"]
    shared_arm = matcher.get("sharedArmWith")
    if shared_arm is not None:
        return _declared_extensions(str(shared_arm), backends, seen | {backend_id})
    return {str(extension) for extension in matcher["extensions"]}


def _patch_guard(
    monkeypatch: pytest.MonkeyPatch,
    *,
    os_name: str,
    ci: bool,
    target_probe: str | None = None,
    present: bool = True,
    missing_commands: frozenset[str] = frozenset(),
) -> None:
    monkeypatch.setattr(guard, "is_ci", ci)
    monkeypatch.setattr(guard, "is_linux", os_name == "linux")
    monkeypatch.setattr(guard, "is_macos", os_name == "macos")
    monkeypatch.setattr(guard, "is_windows", os_name == "windows")
    monkeypatch.setattr(guard.platform, "system", lambda: _OS_SYSTEM[os_name])
    if ci:
        monkeypatch.setenv("CI", "true")
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
    else:
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)

    for helper_name in _HELPER_PROBES.values():
        monkeypatch.setattr(guard, helper_name, lambda: True)
    for flag_name in _FLAG_PROBES.values():
        monkeypatch.setattr(guard, flag_name, False)

    if target_probe in _HELPER_PROBES:
        helper_name = _HELPER_PROBES[target_probe]
        monkeypatch.setattr(guard, helper_name, lambda: present)
    elif target_probe in _FLAG_PROBES:
        unavailable = not present or (target_probe == "erlang_ls" and os_name == "windows")
        monkeypatch.setattr(guard, _FLAG_PROBES[target_probe], unavailable)
    elif target_probe is not None and not present:
        missing_commands = frozenset(target_probe.split("|"))

    monkeypatch.setattr(guard._sh, "which", lambda command: None if command in missing_commands else f"/fake/{command}")


def _run_guard(
    monkeypatch: pytest.MonkeyPatch,
    *,
    os_name: str,
    ci: bool,
    target_probe: str | None = None,
    present: bool = True,
    missing_commands: frozenset[str] = frozenset(),
) -> set[str]:
    _patch_guard(
        monkeypatch,
        os_name=os_name,
        ci=ci,
        target_probe=target_probe,
        present=present,
        missing_commands=missing_commands,
    )
    return {language_server.value for language_server in guard._determine_disabled_language_servers()}


def _expected_probe_disabled(policy: Mapping[str, Any], os_name: str, ci: bool, present: bool) -> bool:
    category = policy["category"]
    if category == 2:
        loud_on = policy["loudOn"]
        loud_in_cell = bool(loud_on["ci"] and ci and os_name in loud_on["os"])
        return not present and not loud_in_cell
    if category == 3:
        return not present
    raise AssertionError(f"toolProbe has unsupported skip category {category}")


def test_declaration_export_materializes_temporary_extracted_facts(monkeypatch: pytest.MonkeyPatch) -> None:
    outputs: list[Path] = []

    def recording_write(
        root: Path,
        output_path: Path | None = None,
        *,
        include_freshness: bool = True,
    ) -> Path:
        assert output_path is not None
        assert include_freshness is False
        outputs.append(output_path)
        return assemble_write_extracted(root, output_path, include_freshness=include_freshness)

    monkeypatch.setattr(decl_export, "write_extracted", recording_write, raising=False)
    decl_export.export_backends.cache_clear()
    try:
        assert decl_export.export_backends()
    finally:
        decl_export.export_backends.cache_clear()

    repository_root = Path(__file__).parents[2]
    assert len(outputs) == 1
    assert outputs[0].is_relative_to(repository_root)
    assert not outputs[0].is_relative_to(repository_root / "contract" / "extracted")


@pytest.mark.parametrize("language_server_id", list(LanguageServerId), ids=lambda item: item.value)
def test_b_reg_001_matcher_extensions_match_declarations(language_server_id: LanguageServerId) -> None:
    backends = cast(dict[str, dict[str, Any]], export_backends())
    matcher = language_server_id.get_source_fn_matcher()
    matcher.reset()

    assert set(matcher.file_extensions) == _declared_extensions(language_server_id.value, backends)


@pytest.mark.parametrize("language_server_id", list(LanguageServerId), ids=lambda item: item.value)
def test_b_reg_002_dispatched_classes_are_concrete_or_currently_waived(language_server_id: LanguageServerId) -> None:
    waived = export_waived_subjects("B-REG-002")
    assert waived <= {item.value for item in LanguageServerId}

    language_server_class = language_server_id.get_ls_class()
    abstract_methods = set(getattr(language_server_class, "__abstractmethods__", frozenset()))
    if language_server_id.value in waived:
        assert abstract_methods, f"waiver for {language_server_id.value} is stale"
        with pytest.raises(TypeError, match="abstract"):
            cast(Callable[..., object], language_server_class)(None, None)
    else:
        assert not abstract_methods


def test_b_skip_001_tool_probe_matrix_matches_declared_category(monkeypatch: pytest.MonkeyPatch) -> None:
    backends = cast(dict[str, dict[str, Any]], export_backends())
    cells = [
        _GuardCell(backend_id, os_name, ci, present)
        for backend_id, backend in sorted(backends.items())
        if "toolProbe" in backend["ci"]["skipPolicy"]
        for os_name in _OS_SYSTEM
        for ci in (False, True)
        for present in (False, True)
    ]
    failures: list[str] = []
    for cell in cells:
        backend = backends[cell.backend]
        policy = backend["ci"]["skipPolicy"]
        disabled = _run_guard(
            monkeypatch,
            os_name=cell.os_name,
            ci=cell.ci,
            target_probe=str(policy["toolProbe"]),
            present=cell.present,
        )
        actual = cell.backend in disabled
        expected = cell.os_name not in backend["platforms"]["supported"] or _expected_probe_disabled(
            policy, cell.os_name, cell.ci, cell.present
        )
        if actual != expected:
            failures.append(f"{cell.id}: expected_disabled={expected}, actual_disabled={actual}")

    assert cells
    assert not failures, "\n".join(failures)


@pytest.mark.parametrize(
    ("os_name", "ci", "missing_command"),
    [
        ("linux", False, "qmlls6"),
        ("linux", False, "qmlls"),
        ("linux", True, "qmlls6"),
        ("linux", True, "qmlls"),
        ("windows", True, "qmlls6"),
        ("windows", True, "qmlls"),
    ],
)
def test_b_skip_001_qml_accepts_either_binary(
    monkeypatch: pytest.MonkeyPatch,
    os_name: str,
    ci: bool,
    missing_command: str,
) -> None:
    disabled = _run_guard(
        monkeypatch,
        os_name=os_name,
        ci=ci,
        missing_commands=frozenset({missing_command}),
    )
    assert LanguageServerId.QML.value not in disabled


@pytest.mark.parametrize("ci", [False, True])
@pytest.mark.parametrize(
    ("os_name", "ansible_disabled", "swift_disabled"),
    [
        ("linux", False, True),
        ("macos", False, False),
        ("windows", True, True),
    ],
)
def test_b_skip_001_platform_only_guards(
    monkeypatch: pytest.MonkeyPatch,
    ci: bool,
    os_name: str,
    ansible_disabled: bool,
    swift_disabled: bool,
) -> None:
    disabled = _run_guard(monkeypatch, os_name=os_name, ci=ci)
    assert (LanguageServerId.ANSIBLE.value in disabled) is ansible_disabled
    assert (LanguageServerId.SWIFT.value in disabled) is swift_disabled
