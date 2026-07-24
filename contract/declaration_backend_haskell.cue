package contract

backends: haskell: #DeclaredBackend & {
	id:       "haskell"
	language: "haskell"
	role:     "sole"
	class: {module: "haskell_language_server", name: "HaskellLanguageServer"}
	status: "stable"
	matcher: extensions: [".hs", ".lhs"]
	provisioning: {strategy: "path", owner: {runtime: "user", ci: "workflow-step"}, cacheInputs: [".github/workflows/pytest.yml#Install Haskell language server"], executables: ["haskell-language-server-wrapper"]}
	platforms: {supported: ["linux", "macos", "windows"], excluded: []}
	testing: {tested: true, marker: "haskell", fixtureRepo: "haskell", testDir: "haskell", bootstrap: {required: true, steps: [{kind: "cabal-build", detail: "Pre-build Haskell test project for HLS"}], produces: ["dist-newstyle"], onFailure: {ci: "fail", local: "skip"}}}
	ci: _CIExpected & _BatchOther & _CILinux & {skipPolicy: {category: 3, toolProbe: "haskell-language-server-wrapper"}} & {installStep: "Setup Haskell toolchain"}
}
