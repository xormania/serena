package contract

backends: zig: #DeclaredBackend & {
	id:       "zig"
	language: "zig"
	role:     "sole"
	class: {module: "zls", name: "ZigLanguageServer"}
	status: "stable"
	matcher: extensions: [".zig", ".zon"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "workflow-step"}, cacheInputs: [".github/workflows/pytest.yml#ZLS version"], pin: "0.14.0", checksums: "default-version-only", hosts: ["github.com"]}
	testing: {tested: true, marker: "zig", fixtureRepo: "zig", testDir: "zig"}
	ci: _CIExpected & _BatchNative & _CIAllOS & _SkipEverywhere
}
