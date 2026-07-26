package contract

backends: python_ty: #DeclaredBackend & {
	id:       "python_ty"
	language: "python"
	role:     "alternate"
	class: {module: "ty_server", name: "TyLanguageServer"}
	status: "experimental"
	matcher: sharedArmWith: "python"
	provisioning: {strategy: "uvx", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/ty_server.py#TY_VERSION"], package: "ty", pin: "0.0.25"}
	testing: {tested: true, marker: "python", fixtureRepo: "python", aliasOf: "python", testDir: "python"}
	ci: _CIExpected & _BatchCatchAll & _CIAllOS & _SkipEverywhere
}
