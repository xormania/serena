package contract

backends: python_pyrefly: #DeclaredBackend & {
	id:       "python_pyrefly"
	language: "python"
	role:     "alternate"
	class: {module: "pyrefly_server", name: "PyreflyLanguageServer"}
	status: "experimental"
	matcher: sharedArmWith: "python"
	provisioning: {strategy: "uvx", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/pyrefly_server.py#PYREFLY_VERSION"], package: "pyrefly", pin: "1.1.1"}
	testing: {tested: true, marker: "python", fixtureRepo: "python", aliasOf: "python", testDir: "python"}
	ci: _CIExpected & _BatchCatchAll & _CIAllOS & _SkipEverywhere
}
