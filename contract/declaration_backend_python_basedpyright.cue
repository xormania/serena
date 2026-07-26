package contract

backends: python_basedpyright: #DeclaredBackend & {
	id:       "python_basedpyright"
	language: "python"
	role:     "alternate"
	class: {module: "basedpyright_server", name: "BasedPyrightLanguageServer"}
	status: "experimental"
	matcher: sharedArmWith: "python"
	provisioning: {strategy: "uvx", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/basedpyright_server.py#BASEDPYRIGHT_VERSION"], package: "basedpyright", pin: "1.39.9"}
	testing: {tested: true, marker: "python", fixtureRepo: "python", aliasOf: "python", testDir: "python"}
	ci: _CIExpected & _BatchCatchAll & _CIAllOS & _SkipEverywhere
}
