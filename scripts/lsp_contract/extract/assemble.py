"""Deterministic assembly of all extracted repository facts.\n\nThe repository source remains authoritative; extraction supplies agreement checks and never a competing editable truth.\n"""

import json
from pathlib import Path

from scripts.lsp_contract.extract.conftest_ast import extract_conftest
from scripts.lsp_contract.extract.docs_presence import extract_docs
from scripts.lsp_contract.extract.filesystem import extract_filesystem
from scripts.lsp_contract.extract.ls_config_ast import extract_ls_config
from scripts.lsp_contract.extract.pyproject_toml import extract_pyproject
from scripts.lsp_contract.extract.server_modules_ast import extract_server_modules
from scripts.lsp_contract.extract.workflow_yaml import extract_workflow


def extract_repository(root: Path) -> dict[str, object]:
    """Extract the complete normalized repository view."""
    root = root.resolve()
    extracted = {
        "lsConfig": extract_ls_config(root / "src" / "solidlsp" / "ls_config.py"),
        "conftest": extract_conftest(root / "test" / "conftest.py"),
        "pyproject": extract_pyproject(root / "pyproject.toml"),
        "workflow": extract_workflow(root / ".github" / "workflows" / "pytest.yml"),
        "servers": extract_server_modules(root / "src" / "solidlsp" / "language_servers"),
        "filesystem": extract_filesystem(root),
        "docs": extract_docs(root),
    }
    return {"extracted": extracted}


def write_extracted(root: Path, output_path: Path | None = None) -> Path:
    """Write the deterministic extracted JSON document."""
    destination = output_path or root / "contract" / "extracted" / "extracted.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(extract_repository(root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination
