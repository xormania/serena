package contract

backends: zig: #DeclaredBackend & {
	id:       "zig"
	language: "zig"
	role:     "sole"
	class: {module: "zls", name: "ZigLanguageServer"}
	status: "stable"
	matcher: extensions: [".zig", ".zon"]
	provisioning: {
		strategy: "path"
		owner: {runtime: "user", ci: "workflow-step"}
		cacheInputs: [".github/workflows/pytest.yml#Install ZLS (Zig Language Server)"]
		executables: ["zig", "zls"]
	}
	platforms: {
		supported: ["linux", "macos"]
		excluded: [{os: "windows", reason: "ZigLanguageServer rejects Windows because cross-file references are unreliable."}]
	}
	testing: {tested: true, marker: "zig", fixtureRepo: "zig", testDir: "zig"}
	ci: _CIExpected & _BatchNative & _CINonWindows & _SkipEverywhere
}
