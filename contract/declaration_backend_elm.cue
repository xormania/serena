package contract

backends: elm: #DeclaredBackend & {
	id:       "elm"
	language: "elm"
	role:     "sole"
	class: {module: "elm_language_server", name: "ElmLanguageServer"}
	status: "stable"
	matcher: extensions: [".elm"]
	provisioning: {strategy: "npm", owner: {runtime: "serena", ci: "workflow-step"}, cacheInputs: ["src/solidlsp/language_servers/elm_language_server.py#DEFAULT_ELM_LANGUAGE_SERVER_VERSION"], packages: [{name: "@elm-tooling/elm-language-server", pin: "2.8.0"}, {name: "elm", pin: "0.19.1-6"}]}
	testing: {tested: true, marker: "elm", fixtureRepo: "elm", testDir: "elm"}
	ci: _CIExpected & _BatchCatchAll & _CIAllOS & {skipPolicy: {category: 2, loudOn: {os: ["linux", "macos", "windows"], ci: true}, toolProbe: "elm"}} & {installStep: "Install Elm"}
}
