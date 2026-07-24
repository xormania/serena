package contract

backends: lean4: #DeclaredBackend & {
	id:       "lean4"
	language: "lean4"
	role:     "sole"
	class: {module: "lean4_language_server", name: "Lean4LanguageServer"}
	status: "stable"
	matcher: extensions: [".lean"]
	provisioning: {strategy: "path", owner: {runtime: "project", ci: "workflow-step"}, cacheInputs: ["test/resources/repos/lean4/test_repo/lean-toolchain"], executables: ["lake", "lean"]}
	testing: {tested: true, marker: "lean4", fixtureRepo: "lean4", testDir: "lean4"}
	ci: _CIExpected & _BatchNiche & _CILinux & {skipPolicy: {category: 3, toolProbe: "lean"}}
}
