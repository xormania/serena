package contract

backends: scss: #DeclaredBackend & {
	id:       "scss"
	language: "scss"
	role:     "sole"
	class: {module: "some_sass_language_server", name: "SomeSassLanguageServer"}
	status: "experimental"
	matcher: extensions: [".scss", ".sass", ".css"]
	provisioning: {strategy: "npm", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/some_sass_language_server.py#DEFAULT_PACKAGE_VERSION"], packages: [{name: "some-sass-language-server", pin: "2.3.8"}]}
	testing: {tested: true, marker: "scss", fixtureRepo: "scss", testDir: "scss"}
	ci: _CIExpected & _BatchCatchAll & _CIAllOS & _SkipEverywhere
}
