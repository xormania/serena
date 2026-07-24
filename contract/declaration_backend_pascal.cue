package contract

backends: pascal: #DeclaredBackend & {
	id:       "pascal"
	language: "pascal"
	role:     "sole"
	class: {module: "pascal_server", name: "PascalLanguageServer"}
	status: "stable"
	matcher: extensions: [".pas", ".pp", ".lpr", ".dpr", ".dpk", ".inc"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "workflow-step"}, cacheInputs: ["src/solidlsp/language_servers/pascal_server.py#PASLS_VERSION"], pin: "v0.2.0", checksums: "default-version-only", hosts: ["github.com"]}
	testing: {tested: true, marker: "pascal", fixtureRepo: "pascal", testDir: "pascal"}
	ci: _CIExpected & _BatchNative & _CIAllOS & _SkipEverywhere & {installStep: "Install Free Pascal Compiler"}
}
