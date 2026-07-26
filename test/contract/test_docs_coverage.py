"""Coverage tests for the authored language-contract documentation."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from scripts.lsp_contract.diagnostics import DIAGNOSTICS

ROOT = Path(__file__).parents[2]
INVARIANTS = ROOT / "contract" / "INVARIANTS.md"
CONTRACT_README = ROOT / "contract" / "README.md"
GUIDE = ROOT / ".serena" / "memories" / "adding_new_language_support_guide.md"

BEHAVIORAL_IDS = {
    "B-REG-001",
    "B-REG-002",
    "B-SKIP-001",
    "B-GATE-001",
    "B-GATE-002",
}
EXPECTED_IDS = set(DIAGNOSTICS) | BEHAVIORAL_IDS


def _required_text(path: Path) -> str:
    assert path.is_file(), f"required documentation is missing: {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def test_invariant_reference_has_exact_complete_structured_coverage() -> None:
    text = _required_text(INVARIANTS)
    headings = re.findall(r"^## ([BC]-[A-Z]+-\d{3})$", text, flags=re.MULTILINE)
    counts = Counter(headings)

    assert set(counts) == EXPECTED_IDS
    assert all(count == 1 for count in counts.values())

    matches = list(re.finditer(r"^## ([BC]-[A-Z]+-\d{3})$", text, flags=re.MULTILINE))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[match.end() : end]
        assert "### Meaning" in section, match.group(1)
        assert "### Typical fix" in section, match.group(1)
        assert "### Waiver guidance" in section, match.group(1)

    cue_text = "\n".join(path.read_text(encoding="utf-8") for path in sorted((ROOT / "contract").glob("invariant_*.cue")))
    cue_ids = {match.replace("_", "-") for match in re.findall(r"^(C_[A-Z]+_\d{3}):", cue_text, flags=re.MULTILINE)}
    assert cue_ids <= set(DIAGNOSTICS)
    assert "instantiable at the class level" not in text
    assert "concrete and has no abstract methods" in text


def test_contract_readme_covers_operation_authority_and_known_issues() -> None:
    text = _required_text(CONTRACT_README)
    required = {
        "runtime CUE language server",
        "v0.16.1",
        "contract compiler",
        "v0.17.1",
        "code-authoritative + extracted",
        "contract-authoritative + declared",
        "contract-derived + generated",
        "behavioral evidence",
        "python -m scripts.lsp_contract install-cue",
        "python -m scripts.lsp_contract validate",
        "poe check-contract",
        "uv run pytest test/contract -q",
        "Managed CUE resolution failures are exit 1",
        "fixing the source is worse than waiving",
        "verible_version",
        "python -m scripts.lsp_contract explain",
        "render-registration",
        "render-template-list",
        "Exit code 0",
        "Exit code 1",
        "Exit code 2",
        "Known-issue register",
        "src/solidlsp/language_servers/haxe_language_server.py",
        "src/solidlsp/language_servers/systemverilog_server.py",
        "src/solidlsp/language_servers/ty_server.py",
        "src/solidlsp/language_servers/jedi_server.py",
        "src/solidlsp/language_servers/svelte_language_server.py",
        "src/solidlsp/language_servers/typescript_language_server.py",
        ".github/workflows/pytest.yml",
        "test/solidlsp/zig/test_zig_basic.py",
        "test/solidlsp/scala/test_scala_language_server.py",
    }
    assert required <= set(token for token in required if token in text)
    assert "proj/cue" not in text
    assert "version or URL override" not in text


def test_language_addition_guide_covers_all_surfaces_and_current_paths() -> None:
    text = _required_text(GUIDE)
    required = {
        "src/solidlsp/language_servers/",
        "LanguageServerId",
        "get_source_fn_matcher",
        "get_ls_class",
        "is_experimental",
        "is_programming_language",
        "get_priority",
        "pyproject.toml",
        "test/resources/repos/",
        "test/solidlsp/",
        "test/conftest.py",
        "test/serena/test_serena_agent.py",
        ".github/workflows/pytest.yml",
        "README.md",
        "docs/01-about/020_programming-languages.md",
        "CHANGELOG.md",
        "src/serena/resources/project.template.yml",
        "contract/declaration_backend_<id>.cue",
        "contract/REGISTRATION.md",
        "contract/INVARIANTS.md",
        "uv run poe check-contract",
        "uv run pytest test/contract -q",
        "solidlsp.util.subprocess_util",
    }
    assert required <= set(token for token in required if token in text)
    assert "`pytest.ini`" not in text
    assert "solidlsp.utils.subprocess_utils" not in text
    assert "### 5 Documentation" not in text


def test_contributing_and_changelog_publish_the_contract_workflow() -> None:
    contributing = _required_text(ROOT / "CONTRIBUTING.md")
    changelog = _required_text(ROOT / "CHANGELOG.md")

    assert "poe check-contract" in contributing
    assert "contract/README.md" in contributing
    assert "CUE-backed language and CI contract" in changelog
