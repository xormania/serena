package contract

backends: latex: #DeclaredBackend & {
	id:       "latex"
	language: "latex"
	role:     "sole"
	class: {module: "texlab_language_server", name: "TexlabLanguageServer"}
	status: "experimental"
	matcher: extensions: [".tex", ".bib", ".sty", ".cls"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/texlab_language_server.py#TEXLAB_VERSION"], pin: "5.25.1", checksums: "all-platform-assets", hosts: ["github.com"]}
	testing: {tested: true, marker: "latex", fixtureRepo: "latex", testDir: "latex"}
	ci: _CIExpected & _BatchOther & _CIAllOS & _SkipEverywhere
}
