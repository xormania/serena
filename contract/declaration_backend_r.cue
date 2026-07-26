package contract

backends: r: #DeclaredBackend & {
	id:       "r"
	language: "r"
	role:     "sole"
	class: {module: "r_language_server", name: "RLanguageServer"}
	status: "stable"
	matcher: extensions: [".R", ".r", ".Rmd", ".Rnw"]
	provisioning: {strategy: "path", owner: {runtime: "user", ci: "workflow-step"}, cacheInputs: [".github/workflows/pytest.yml#Install R language server"], executables: ["R"]}
	testing: {tested: true, marker: "r", fixtureRepo: "r", testDir: "r"}
	ci: _CIExpected & _BatchNiche & _CILinux & {skipPolicy: {category: 3, toolProbe: "R:languageserver"}} & {installStep: "Install R language server"}
}
