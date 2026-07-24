"""Structural smoke tests for live repository extraction."""

from pathlib import Path

from scripts.lsp_contract.extract.assemble import extract_repository

ROOT = Path(__file__).resolve().parents[2]


def test_live_repository_extracts_structural_contract_facts() -> None:
    extracted = extract_repository(ROOT)["extracted"]
    ls_config = extracted["lsConfig"]
    markers = {marker["name"] for marker in extracted["pyproject"]["markers"]}

    assert {"python", "qml", "gdscript"} <= set(ls_config["members"])
    assert set(ls_config["dispatch"]) == set(ls_config["members"])
    assert {"slow", "snapshot"} <= markers
    assert set(extracted["workflow"]["matrix"]["batches"]) == {"jvm", "native", "other-langs", "niche", "catch-all"}
    assert all(cache["key"] for cache in extracted["workflow"]["caches"])
    duplicates = extracted["conftest"]["rawDuplicateKeys"]
    assert len(duplicates) == 1
    assert duplicates[0][0] == "PYTHON_TY"
