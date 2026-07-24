package contract

backends: hlsl: #DeclaredBackend & {
	id:       "hlsl"
	language: "hlsl"
	role:     "sole"
	class: {module: "hlsl_language_server", name: "HlslLanguageServer"}
	status: "stable"
	matcher: extensions: [".hlsl", ".hlsli", ".fx", ".fxh", ".cginc", ".compute", ".shader", ".glsl", ".vert", ".frag", ".geom", ".tesc", ".tese", ".comp", ".wgsl"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/hlsl_language_server.py#_DEFAULT_VERSION"], pin: "1.3.1", checksums: "default-version-only", hosts: ["github.com"]}
	platforms: {supported: ["linux", "macos", "windows"], excluded: [], provisioningOverrides: {macos: {strategy: "source-build", pin: "1.3.1", lockDiscipline: {tool: "cargo", flag: "--locked"}}}}
	testing: {tested: true, marker: "hlsl", fixtureRepo: "hlsl", testDir: "hlsl"}
	ci: _CIExpected & _BatchOther & _CIAllOS & _SkipEverywhere
}
