package contract

backends: luau: #DeclaredBackend & {
	id:       "luau"
	language: "luau"
	role:     "sole"
	class: {module: "luau_lsp", name: "LuauLanguageServer"}
	status: "stable"
	matcher: extensions: [".luau"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/luau_lsp.py#DEFAULT_LUAU_LSP_VERSION"], pin: "1.63.0", checksums: "default-version-only", hosts: ["github.com"]}
	testing: {tested: true, marker: "luau", fixtureRepo: "luau", testDir: "luau"}
	ci: _CIExpected & _BatchOther & _CIAllOS & _SkipEverywhere
}
