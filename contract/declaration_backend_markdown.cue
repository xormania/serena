package contract

backends: markdown: #DeclaredBackend & {
	id:       "markdown"
	language: "markdown"
	role:     "sole"
	class: {module: "marksman", name: "Marksman"}
	status: "experimental"
	matcher: extensions: [".md", ".markdown"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/marksman.py#DEFAULT_MARKSMAN_VERSION"], pin: "2024-12-18", checksums: "all-platform-assets", hosts: ["github.com"]}
	testing: {tested: true, marker: "markdown", fixtureRepo: "markdown", testDir: "markdown"}
	ci: _CIExpected & _BatchOther & _CIAllOS & _SkipEverywhere
}
