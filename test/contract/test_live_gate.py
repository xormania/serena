"""End-to-end validation against the live repository."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.lsp_contract.extract.server_modules_ast import extract_server_modules

ROOT = Path(__file__).parents[2]
OPAQUE_PROVISIONING_MODULES = {
    "al_language_server",
    "bash_language_server",
    "eclipse_jdtls",
    "groovy_language_server",
    "haxe_language_server",
    "kotlin_language_server",
    "lua_ls",
    "luau_lsp",
    "matlab_language_server",
    "omnisharp",
    "pascal_server",
    "phpactor",
    "powershell_language_server",
    "taplo_server",
}


def test_live_opaque_provisioning_inventory_is_explicit() -> None:
    modules = extract_server_modules(ROOT / "src" / "solidlsp" / "language_servers")
    actual = {module for module, record in modules.items() if record["opaqueProvisioningCalls"]}

    assert actual == OPAQUE_PROVISIONING_MODULES
    assert modules["common"]["opaqueProvisioningCalls"] == []
    assert modules["csharp_language_server"]["opaqueProvisioningCalls"] == []
    assert modules["elixir_tools.elixir_tools"]["opaqueProvisioningCalls"] == []


def test_full_repo_validates() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "scripts.lsp_contract", "validate", "--root", str(ROOT)],
        check=False,
        capture_output=True,
        text=True,
        env={"CUE_REGISTRY": "host.invalid"},
    )
    assert completed.returncode == 0, completed.stderr
    assert "0 violations" in completed.stdout
    assert "waivers: 46" in completed.stdout
