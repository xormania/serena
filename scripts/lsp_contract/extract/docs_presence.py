"""Extraction of supported-language labels from user-facing documentation.

The repository source remains authoritative; extraction supplies agreement checks and never a competing editable truth.
"""

import re
from pathlib import Path

from scripts.lsp_contract.diagnostics import ExtractionError

_DOC_LABEL = re.compile(r"^\s*[*-]\s+\*\*([^*]+)\*\*", re.MULTILINE)
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _readme_labels(text: str) -> list[str]:
    fixture = re.search(r"(?im)^Language support:\s*(.+)$", text)
    if fixture:
        language_text = fixture.group(1)
    else:
        supported = re.search(
            r"support for over \d+ programming languages.*?including\s*\n([^\n]+)",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        language_text = supported.group(1) if supported else ""
    language_text = re.sub(r"\s+and\s+", ", ", language_text.strip().rstrip("."))
    return sorted({part.strip() for part in language_text.split(",") if part.strip()})


def _template_ids(text: str) -> list[str]:
    lines = text.splitlines()
    starts = [index for index, line in enumerate(lines) if "BEGIN generated language list" in line]
    ends = [index for index, line in enumerate(lines) if "END generated language list" in line]
    path = Path("src/serena/resources/project.template.yml")
    if len(starts) != 1 or len(ends) != 1:
        raise ExtractionError(
            path,
            1,
            "expected exactly one BEGIN and one END generated language list marker",
        )
    if starts[0] >= ends[0]:
        raise ExtractionError(
            path,
            starts[0] + 1,
            "END generated language list marker must follow BEGIN",
        )

    result: list[str] = []
    for index in range(starts[0] + 1, ends[0]):
        match = re.fullmatch(r"#\s*-\s*([a-z][a-z0-9_]*)\s*", lines[index])
        if match is None:
            raise ExtractionError(path, index + 1, "malformed generated language identifier")
        result.append(match.group(1))
    if result != sorted(set(result)):
        raise ExtractionError(
            path,
            starts[0] + 1,
            "generated language identifiers must be unique and sorted",
        )
    return result


def extract_docs(root: Path) -> dict[str, object]:
    """Extract actual supported-language labels and template identifiers."""
    readme = _read(root / "README.md")
    documentation_path = root / "programming-languages.md"
    if not documentation_path.is_file():
        documentation_path = root / "docs" / "01-about" / "020_programming-languages.md"
    documentation = _read(documentation_path)

    template_path = root / "project.template.yml"
    if not template_path.is_file():
        template_path = root / "src" / "serena" / "resources" / "project.template.yml"
    template = _read(template_path)

    return {
        "readmeLabels": _readme_labels(readme),
        "docsLabels": sorted(set(_DOC_LABEL.findall(documentation))),
        "templateIds": _template_ids(template),
    }
