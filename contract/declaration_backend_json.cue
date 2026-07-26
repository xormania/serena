package contract

backends: json: #DeclaredBackend & {
	id:       "json"
	language: "json"
	role:     "sole"
	class: {module: "json_language_server", name: "JsonLanguageServer"}
	status: "experimental"
	matcher: extensions: [".json", ".jsonc"]
	provisioning: {strategy: "npm", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/json_language_server.py#DEFAULT_JSON_LANGUAGE_SERVER_VERSION"], packages: [{name: "vscode-json-languageserver", pin: "1.3.4"}]}
	testing: {tested: true, marker: "json", fixtureRepo: "json", testDir: "json_ls"}
	ci: _CIExpected & _BatchCatchAll & _CIAllOS & _SkipEverywhere
}
