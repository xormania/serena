"""Deterministic renderers for the two contract-derived repository artifacts."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any, cast

from scripts.lsp_contract.decl_export import export_declared_backends
from scripts.lsp_contract.diagnostics import ExtractionError

REGISTRATION_PATH = Path("contract/REGISTRATION.md")
TEMPLATE_PATH = Path("src/serena/resources/project.template.yml")
_BEGIN_MARKER = "# BEGIN generated language list"
_END_MARKER = "# END generated language list"
_REGEN_REGISTRATION = "uv run python -m scripts.lsp_contract render-registration"
_REGEN_TEMPLATE = "uv run python -m scripts.lsp_contract render-template-list"
_ALL_PLATFORMS = {"linux", "macos", "windows"}
_GROUP_ORDER = (
    "TCP-attach",
    "Bundled server",
    "Source build",
    "Multi-server composite",
    "Project-dependent",
    "Platform-exclusive",
    "CI-provided toolchain",
    "Alternate backend",
    "Standard",
)


def load_backends(root: Path) -> dict[str, dict[str, object]]:
    """Load concrete declarations without evaluating extraction-dependent invariants."""
    return export_declared_backends(root)


def _mapping(value: object) -> Mapping[str, Any]:
    return cast(Mapping[str, Any], value) if isinstance(value, Mapping) else {}


def _integration_traits(backend: Mapping[str, Any]) -> tuple[str, ...]:
    provisioning = _mapping(backend.get("provisioning"))
    platforms = _mapping(backend.get("platforms"))
    owner = _mapping(provisioning.get("owner"))
    testing = _mapping(backend.get("testing"))
    strategy = provisioning.get("strategy")
    overrides = _mapping(platforms.get("provisioningOverrides"))
    traits: list[str] = []

    if strategy == "tcp":
        traits.append("TCP-attach")
    if strategy == "bundled":
        traits.append("Bundled server")
    if strategy == "source-build" or any(_mapping(override).get("strategy") == "source-build" for override in overrides.values()):
        traits.append("Source build")
    if strategy == "composite" or provisioning.get("companions"):
        traits.append("Multi-server composite")
    if owner.get("runtime") == "project":
        traits.append("Project-dependent")
    if set(platforms.get("supported", ())) != _ALL_PLATFORMS:
        traits.append("Platform-exclusive")
    if owner.get("ci") in {"workflow-step", "image"}:
        traits.append("CI-provided toolchain")
    if backend.get("role") == "alternate":
        traits.append("Alternate backend")
    bootstrap = _mapping(testing.get("bootstrap"))
    if bootstrap.get("required") is True:
        traits.append("required fixture bootstrap")
    return tuple(traits or ("Standard",))


def _primary_group(backend: Mapping[str, Any]) -> str:
    traits = _integration_traits(backend)
    return next((group for group in _GROUP_ORDER if group in traits), "Standard")


def _markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def _code_paths(*paths: str) -> str:
    return "<br>".join(f"`{path}`" for path in paths)


def _surface_rows(backend_id: str, backend: Mapping[str, Any]) -> tuple[tuple[int, str, str, str], ...]:
    class_declaration = _mapping(backend.get("class"))
    testing = _mapping(backend.get("testing"))
    module = str(class_declaration.get("module", ""))
    server_path = f"src/solidlsp/language_servers/{module.replace('.', '/')}.py"
    declaration_path = f"contract/declaration_backend_{backend_id}.cue"
    fixture_repo = testing.get("fixtureRepo")
    test_dir = testing.get("testDir")
    fixture_path = _code_paths(f"test/resources/repos/{fixture_repo}/test_repo/") if isinstance(fixture_repo, str) else "—"
    test_paths: list[str] = []
    if isinstance(test_dir, str):
        test_paths.append(f"test/solidlsp/{test_dir}/")
        if _mapping(testing.get("bootstrap")).get("required") is True:
            test_paths.append(f"test/solidlsp/{test_dir}/conftest.py")
    test_path = _code_paths(*test_paths) if test_paths else "—"
    declared_and_extracted = "contract-authoritative + declared<br>code-authoritative + extracted"
    code_extracted = "code-authoritative + extracted"
    mixed_generated = "code-authoritative + extracted<br>contract-derived + generated"

    return (
        (
            1,
            _code_paths(declaration_path, server_path),
            declared_and_extracted,
            "C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001",
        ),
        (2, _code_paths("src/solidlsp/ls_config.py#LanguageServerId"), code_extracted, "C-REG-001"),
        (
            3,
            _code_paths("src/solidlsp/ls_config.py#get_source_fn_matcher"),
            code_extracted,
            "C-REG-003, B-REG-001",
        ),
        (
            4,
            _code_paths("src/solidlsp/ls_config.py#get_ls_class"),
            code_extracted,
            "C-REG-002, B-REG-002",
        ),
        (
            5,
            _code_paths(
                "src/solidlsp/ls_config.py#is_experimental",
                "src/solidlsp/ls_config.py#is_programming_language",
                "src/solidlsp/ls_config.py#get_priority",
            ),
            code_extracted,
            "C-REG-004",
        ),
        (
            6,
            _code_paths("pyproject.toml#tool.pytest.ini_options.markers"),
            code_extracted,
            "C-TEST-001, C-TEST-004",
        ),
        (7, fixture_path, code_extracted, "C-TEST-002, C-TEST-006"),
        (
            8,
            test_path,
            code_extracted,
            "C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003",
        ),
        (
            9,
            _code_paths("test/conftest.py", "test/serena/test_serena_agent.py"),
            code_extracted,
            "C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001",
        ),
        (
            10,
            _code_paths(
                ".github/workflows/pytest.yml",
                "README.md",
                "docs/01-about/020_programming-languages.md",
                "CHANGELOG.md",
                "src/serena/resources/project.template.yml",
            ),
            mixed_generated,
            "C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007",
        ),
    )


def render_registration_text(backends: Mapping[str, Mapping[str, Any]]) -> str:
    """Render the complete backend-by-surface registration table."""
    grouped: dict[str, list[str]] = {group: [] for group in _GROUP_ORDER}
    for backend_id in sorted(backends):
        grouped[_primary_group(backends[backend_id])].append(backend_id)

    lines = [
        f"<!-- DO NOT EDIT: run `{_REGEN_REGISTRATION}` -->",
        "# Language-server registration surfaces",
        "",
        "This table is derived from the CUE declarations. Each backend appears exactly once and has all ten required integration surfaces.",
        "",
    ]
    for group in _GROUP_ORDER:
        if not grouped[group]:
            continue
        lines.extend((f"## Integration class: {group}", ""))
        for backend_id in grouped[group]:
            backend = backends[backend_id]
            traits = ", ".join(_integration_traits(backend))
            lines.extend(
                (
                    f"### `{backend_id}` — {traits}",
                    "",
                    "| Surface | Path | Authority | Enforced by |",
                    "|---:|---|---|---|",
                )
            )
            for surface, path, authority, invariants in _surface_rows(backend_id, backend):
                lines.append(f"| {surface} | {_markdown_cell(path)} | {_markdown_cell(authority)} | {_markdown_cell(invariants)} |")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _backend_ids(backends: Mapping[str, object] | Iterable[str]) -> list[str]:
    values = backends.keys() if isinstance(backends, Mapping) else backends
    return sorted(set(values))


def render_template_block(backends: Mapping[str, object] | Iterable[str]) -> str:
    """Render the canonical marked template language-server block."""
    lines = [
        f"{_BEGIN_MARKER} — DO NOT EDIT; run `{_REGEN_TEMPLATE}`",
        *(f"# - {backend_id}" for backend_id in _backend_ids(backends)),
        _END_MARKER,
    ]
    return "\n".join(lines) + "\n"


def _marker_indices(lines: list[str], marker: str) -> list[int]:
    return [index for index, line in enumerate(lines) if marker in line]


def render_template_text(text: str, backends: Mapping[str, object] | Iterable[str]) -> str:
    """Replace or migrate the generated template block without changing authored text."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.splitlines(keepends=True)
    starts = _marker_indices(lines, _BEGIN_MARKER)
    ends = _marker_indices(lines, _END_MARKER)
    marker_path = TEMPLATE_PATH

    if starts or ends:
        if len(starts) != 1 or len(ends) != 1:
            raise ExtractionError(marker_path, 1, "expected exactly one BEGIN and one END generated language list marker")
        if starts[0] >= ends[0]:
            raise ExtractionError(marker_path, starts[0] + 1, "END generated language list marker must follow BEGIN")
        rendered = "".join(lines[: starts[0]]) + render_template_block(backends) + "".join(lines[ends[0] + 1 :])
    else:
        list_start = next((index for index, line in enumerate(lines) if "choose from:" in line), None)
        if list_start is None:
            raise ExtractionError(marker_path, 1, "missing BEGIN generated language list marker and legacy list anchor")
        authored_start = next(
            (index for index in range(list_start + 1, len(lines)) if lines[index].startswith("# For some languages")),
            None,
        )
        if authored_start is None:
            raise ExtractionError(marker_path, list_start + 1, "missing legacy language-list terminator")
        current_source = "# Current identifiers are LanguageServerId values from src/solidlsp/ls_config.py.\n"
        rendered = "".join(lines[: list_start + 1]) + render_template_block(backends) + current_source + "".join(lines[authored_start:])

    rendered = rendered.replace("values of Language enum", "LanguageServerId values")
    return rendered.rstrip("\n") + "\n"


def artifact_freshness(
    root: Path,
    *,
    backends: Mapping[str, Mapping[str, Any]] | None = None,
    registration_path: Path | None = None,
    template_path: Path | None = None,
) -> dict[str, bool]:
    """Byte-compare the two committed artifacts with deterministic regeneration."""
    root = root.resolve()
    declarations = backends if backends is not None else load_backends(root)
    registration = registration_path or root / REGISTRATION_PATH
    template = template_path or root / TEMPLATE_PATH
    expected_registration = render_registration_text(declarations).encode("utf-8")
    registration_current = registration.is_file() and registration.read_bytes() == expected_registration
    template_current = False
    if template.is_file():
        source = template.read_text(encoding="utf-8")
        expected_template = render_template_text(source, declarations).encode("utf-8")
        template_current = template.read_bytes() == expected_template
    return {
        "registrationCurrent": registration_current,
        "templateCurrent": template_current,
    }


def write_registration(root: Path, output_path: Path | None = None) -> Path:
    """Generate and write REGISTRATION.md."""
    root = root.resolve()
    destination = output_path or root / REGISTRATION_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_registration_text(load_backends(root)), encoding="utf-8", newline="\n")
    return destination


def write_template_list(root: Path, output_path: Path | None = None) -> Path:
    """Generate and write the marked template language-server list."""
    root = root.resolve()
    source = root / TEMPLATE_PATH
    destination = output_path or source
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_template_text(source.read_text(encoding="utf-8"), load_backends(root)),
        encoding="utf-8",
        newline="\n",
    )
    return destination
