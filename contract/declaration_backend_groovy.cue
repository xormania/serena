package contract

backends: groovy: #DeclaredBackend & {
	id:       "groovy"
	language: "groovy"
	role:     "sole"
	class: {module: "groovy_language_server", name: "GroovyLanguageServer"}
	status: "experimental"
	matcher: extensions: [".groovy", ".gvy"]
	provisioning: {strategy: "path", owner: {runtime: "user", ci: "workflow-step"}, cacheInputs: [".github/workflows/pytest.yml#Groovy language server"], executables: ["java"]}
	testing: {tested: true, marker: "groovy", fixtureRepo: "groovy", testDir: "groovy"}
	ci: _CIExpected & _BatchJVM & _CIAllOS & _SkipEverywhere
}
