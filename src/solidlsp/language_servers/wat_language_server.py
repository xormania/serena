from solidlsp.dependency_provider import LanguageServerDependencyProviderBaseCommand
from solidlsp.ls import SolidLanguageServer
from solidlsp.ls_config import LanguageServerConfig
from solidlsp.settings import SolidLSPSettings


class WatLanguageServer(SolidLanguageServer):
    """
    Experimental WebAssembly text-format support using wasm-language-tools.

    Requires an explicit ``ls_path`` or ``ls_base_cmd`` pointing to ``wat_server``.
    Only ``.wat`` files are supported, not binary WebAssembly or WAST scripts.
    """

    def __init__(self, config: LanguageServerConfig, repository_root_path: str, solidlsp_settings: SolidLSPSettings):
        super().__init__(config, repository_root_path, None, "wat", solidlsp_settings)

    class DependencyProvider(LanguageServerDependencyProviderBaseCommand):
        def _create_default_base_command(self) -> list[str]:
            raise RuntimeError("Configure ls_specific_settings.wat.ls_path with the path to the wat_server executable.")

        def _create_launch_command_from_base_command(self, base_command: list[str]) -> list[str]:
            return base_command

    def _create_dependency_provider(self) -> DependencyProvider:
        return self.DependencyProvider(self._custom_settings, self._ls_resources_dir)

    def _create_base_initialize_params(self) -> dict:
        return {
            "capabilities": {
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
