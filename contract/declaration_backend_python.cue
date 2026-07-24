package contract

backends: python: #DeclaredBackend & {
	id:       "python"
	language: "python"
	role:     "default"
	class: {module: "pyright_server", name: "PyrightServer"}
	status: "stable"
	matcher: extensions: [".py", ".pyi"]
	provisioning: {strategy: "uvx", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/pyright_server.py#PYRIGHT_VERSION"], package: "pyright", pin: "1.1.403"}
	testing: {tested: true, marker: "python", fixtureRepo: "python", testDir: "python"}
	ci: _CIExpected & _BatchCatchAll & _CIAllOS & _SkipEverywhere
}
