package contract

backends: rust: #DeclaredBackend & {
	id:       "rust"
	language: "rust"
	role:     "sole"
	class: {module: "rust_analyzer", name: "RustAnalyzer"}
	status: "stable"
	matcher: extensions: [".rs"]
	provisioning: {strategy: "path", owner: {runtime: "user", ci: "image"}, cacheInputs: [], executables: ["rust-analyzer"]}
	testing: {tested: true, marker: "rust", fixtureRepo: "rust", testDir: "rust"}
	ci: _CIExpected & _BatchNative & _CIAllOS & _SkipEverywhere
	capabilities: implementationSupport: "verified"
}
