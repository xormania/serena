package contract

backends: rego: #DeclaredBackend & {
	id:       "rego"
	language: "rego"
	role:     "sole"
	class: {module: "regal_server", name: "RegalLanguageServer"}
	status: "stable"
	matcher: extensions: [".rego"]
	provisioning: {strategy: "path", owner: {runtime: "user", ci: "workflow-step"}, cacheInputs: [".github/workflows/pytest.yml#Install Regal"], executables: ["regal"]}
	testing: {tested: true, marker: "rego", fixtureRepo: "rego", testDir: "rego"}
	ci: _CIExpected & _BatchOther & _CIAllOS & {skipPolicy: {category: 2, loudOn: {os: ["linux", "macos", "windows"], ci: true}, toolProbe: "regal"}}
}
