"""Unit tests for source-specific contract extractors."""

from pathlib import Path

from scripts.lsp_contract.extract.conftest_ast import extract_conftest
from scripts.lsp_contract.extract.docs_presence import extract_docs
from scripts.lsp_contract.extract.filesystem import extract_filesystem
from scripts.lsp_contract.extract.ls_config_ast import extract_ls_config
from scripts.lsp_contract.extract.pyproject_toml import extract_pyproject
from scripts.lsp_contract.extract.server_modules_ast import extract_server_modules
from scripts.lsp_contract.extract.workflow_yaml import extract_workflow

FIXTURES = Path(__file__).parent / "fixtures" / "extractor" / "good"


def test_extracts_language_identity_matchers_and_dispatch() -> None:
    extracted = extract_ls_config(FIXTURES / "ls_config.py")

    assert extracted["members"] == ["python", "qml"]
    assert extracted["dispatch"]["python"] == {"module": "example.python_server", "class": "PythonServer"}
    assert extracted["matchers"]["python"] == {"literalExtensions": [".py", ".pyi"], "caseSensitive": True}
    assert extracted["matchers"]["qml"] == {"computedShape": True}
    assert extracted["experimentalSet"] == ["qml"]
    assert extracted["priorityZeroSet"] == ["qml"]


def test_extracts_conftest_without_losing_duplicate_keys() -> None:
    extracted = extract_conftest(FIXTURES / "conftest.py")

    assert extracted["aliases"] == {"PYTHON_TY": "PYTHON"}
    assert extracted["rawDuplicateKeys"] == [["PYTHON_TY", 4, 5]]
    assert extracted["markerDict"] == {"PYTHON_TY": ["python"]}
    assert extracted["verifiedImplementationSet"] == ["PYTHON"]


def test_extracts_pyproject_markers_and_pins() -> None:
    extracted = extract_pyproject(FIXTURES / "pyproject.toml")

    assert [marker["name"] for marker in extracted["markers"]] == ["python", "slow", "snapshot"]
    assert extracted["devPins"] == {"ty": "0.0.24"}


def test_extracts_workflow_matrix_marker_groups_steps_and_caches() -> None:
    extracted = extract_workflow(FIXTURES / "workflow.yml")

    assert extracted["matrix"]["batches"] == ["jvm", "native", "other-langs", "niche", "catch-all"]
    assert extracted["markerGroups"]["jvm"] == ["java", "kotlin"]
    assert extracted["caches"] == [
        {
            "job": "cpu",
            "name": "Cache tools",
            "path": "~/.cache/tools",
            "key": "tools-${{ runner.os }}-v1",
            "restoreKeys": ["tools-${{ runner.os }}-"],
        }
    ]
    assert extracted["steps"][-1]["batchGate"] == ["other-langs"]
    assert extracted["steps"][-1]["osGate"] == ["linux"]


def test_extracts_filesystem_server_and_documentation_facts() -> None:
    filesystem = extract_filesystem(FIXTURES)
    servers = extract_server_modules(FIXTURES)
    docs = extract_docs(FIXTURES)

    assert filesystem == {"repoDirs": ["python"], "testDirs": ["python"], "bootstrapConftests": ["python"]}
    assert servers["server"]["uvxPins"] == [{"package": "example-ls", "version": "1.2.3"}]
    assert servers["server"]["cargoCommands"] == [["cargo", "install", "example-ls", "--version", "version", "--locked"]]
    assert servers["server"]["pathProbes"] == ["example-ls"]
    assert servers["server"]["runtimeDeps"][0]["platformIdOpaque"] is False
    assert servers["mixed_server"]["runtimeDeps"][0]["platformIdOpaque"] is True
    assert servers["opaque_sha_server"]["runtimeDeps"][0]["sha256Opaque"] is True
    assert servers["server"]["opaqueProvisioningCalls"] == []
    assert servers["opaque_server"]["opaqueProvisioningCalls"] == ["FileUtils.download_and_extract_archive_verified"]
    assert servers["forwarding_server"]["opaqueProvisioningCalls"] == []
    assert servers["mixed_server"]["opaqueProvisioningCalls"] == ["FileUtils.download_and_extract_archive_verified"]
    assert servers["raw_download_server"]["opaqueProvisioningCalls"] == [
        "urllib.request.urlopen",
        "urllib.request.urlretrieve",
    ]
    assert servers["unverified_file_server"]["opaqueProvisioningCalls"] == ["FileUtils.download_file_verified"]
    assert docs["readmeLabels"] == ["CUE", "Python", "QML"]
    assert docs["docsLabels"] == ["CUE", "Python", "QML"]
    assert docs["templateIds"] == ["python", "qml", "cue"]
