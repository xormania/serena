package contract

backends: swift: #DeclaredBackend & {
	id:       "swift"
	language: "swift"
	role:     "sole"
	class: {module: "sourcekit_lsp", name: "SourceKitLSP"}
	status: "stable"
	matcher: extensions: [".swift"]
	provisioning: {strategy: "path", owner: {runtime: "user", ci: "workflow-step"}, cacheInputs: [".github/workflows/pytest.yml#Install Swift with swiftly (macOS)"], executables: ["sourcekit-lsp"]}
	platforms: {supported: ["macos"], excluded: [{os: "linux", reason: "The CI Swift toolchain is provisioned only on macOS."}, {os: "windows", reason: "The CI Swift toolchain is provisioned only on macOS."}]}
	testing: {tested: true, marker: "swift", fixtureRepo: "swift", testDir: "swift"}
	ci: _CIExpected & _BatchNative & _CIMacOS & {skipPolicy: {category: 3, toolProbe: "sourcekit-lsp"}}
}
