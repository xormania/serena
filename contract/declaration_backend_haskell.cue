package contract

backends: haskell: #DeclaredBackend & {
	id:       "haskell"
	language: "haskell"
	role:     "sole"
	class: {module: "haskell_language_server", name: "HaskellLanguageServer"}
	status: "stable"
	matcher: extensions: [".hs", ".lhs"]
	provisioning: {strategy: "path", owner: {runtime: "user", ci: "workflow-step"}, cacheInputs: [".github/workflows/pytest.yml#Install Haskell language server"], executables: ["haskell-language-server-wrapper"]}
	platforms: {supported: ["linux"], excluded: [{os: "macos", reason: "The CI Haskell toolchain is provisioned only on Linux."}, {os: "windows", reason: "The CI Haskell toolchain is provisioned only on Linux."}]}
	testing: {tested: true, marker: "haskell", fixtureRepo: "haskell", testDir: "haskell"}
	ci: _CIExpected & _BatchOther & _CILinux & {skipPolicy: {category: 3, toolProbe: "haskell-language-server-wrapper"}}
}
