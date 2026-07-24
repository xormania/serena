package contract

backends: go: #DeclaredBackend & {
	id:       "go"
	language: "go"
	role:     "sole"
	class: {module: "gopls", name: "Gopls"}
	status: "stable"
	matcher: extensions: [".go"]
	provisioning: {strategy: "path", owner: {runtime: "user", ci: "workflow-step"}, cacheInputs: [".github/workflows/pytest.yml#Install gopls"], executables: ["gopls"]}
	testing: {tested: true, marker: "go", fixtureRepo: "go", testDir: "go"}
	ci: _CIExpected & _BatchNative & _CIAllOS & _SkipEverywhere
	capabilities: implementationSupport: "verified"
}
