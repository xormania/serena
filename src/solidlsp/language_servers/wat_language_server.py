import os
import shutil
from pathlib import Path

from solidlsp.dependency_provider import LanguageServerDependencyProviderSinglePath
from solidlsp.ls import SolidLanguageServer
from solidlsp.ls_config import LanguageServerConfig
from solidlsp.settings import SolidLSPSettings
from solidlsp.util.subprocess_util import subprocess_run


class WatLanguageServer(SolidLanguageServer):
    """
    Experimental WebAssembly text-format support using wasm-language-tools.

    Builds a pinned ``wat_server`` revision using Cargo on first use and reuses it thereafter.
    Set ``ls_specific_settings.wat.ls_path`` or ``ls_base_cmd`` to use an existing server.
    Only ``.wat`` files are supported. References and rename are document-local;
    binary WebAssembly and ``.wast`` scripts are not supported.
    """

    def __init__(self, config: LanguageServerConfig, repository_root_path: str, solidlsp_settings: SolidLSPSettings):
        super().__init__(config, repository_root_path, None, "wat", solidlsp_settings)

    class DependencyProvider(LanguageServerDependencyProviderSinglePath):
        # the published 0.11.0 release predates the server's UTF-16 position fix
        _SERVER_REVISION = "6b9888088b2e569fe8fde1588cac7b989246c5c2"

        def _get_or_install_core_dependency(self) -> str:
            # reuse the installation for this exact server revision
            install_dir = Path(self._ls_resources_dir) / f"wat_server-{self._SERVER_REVISION}"
            executable = install_dir / "bin" / ("wat_server.exe" if os.name == "nt" else "wat_server")
            if executable.is_file():
                return str(executable)

            # build the pinned source with its dependency lockfile
            cargo = shutil.which("cargo")
            if cargo is None:
                raise FileNotFoundError(
                    "WAT support requires Cargo to build wat_server. Install Rust from https://rustup.rs "
                    "or configure ls_specific_settings.wat.ls_path with a prebuilt wat_server."
                )
            install_dir.mkdir(parents=True, exist_ok=True)
            subprocess_run(
                [
                    cargo,
                    "install",
                    "--git",
                    "https://github.com/g-plane/wasm-language-tools",
                    "--rev",
                    self._SERVER_REVISION,
                    "--locked",
                    "--root",
                    str(install_dir),
                    "wat_server",
                ],
                cwd=str(install_dir),
                check=True,
                timeout=600,
            )
            if not executable.is_file():
                raise FileNotFoundError(f"wat_server installation did not produce {executable}")
            return str(executable)

        def _create_launch_command(self, core_path: str) -> list[str]:
            return [core_path]

    def _create_dependency_provider(self) -> DependencyProvider:
        return self.DependencyProvider(self._custom_settings, self._ls_resources_dir)

    def _create_base_initialize_params(self) -> dict:
        return {
            "capabilities": {
                "general": {"positionEncodings": ["utf-16"]},
                "textDocument": {
                    "documentSymbol": {"hierarchicalDocumentSymbolSupport": True},
                    "definition": {},
                    "references": {},
                    "rename": {"prepareSupport": True},
                },
            },
        }

    def _start_server(self) -> None:
        self.server.start()
        self.server.send.initialize(self._create_initialize_params())
        self.server.notify.initialized({})

    def _get_wait_time_for_cross_file_referencing(self) -> float:
        # references are resolved within the current document, without workspace indexing
        return 0.0
