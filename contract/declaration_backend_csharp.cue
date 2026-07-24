package contract

backends: csharp: #DeclaredBackend & {
	id:       "csharp"
	language: "csharp"
	role:     "default"
	class: {module: "csharp_language_server", name: "CSharpLanguageServer"}
	status: "stable"
	matcher: extensions: [".cs"]
	provisioning: {strategy: "nuget-download", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/csharp_language_server.py#DEFAULT_CSHARP_LANGUAGE_SERVER_VERSION"], pin: "5.5.0-2.26078.4", checksums: "all-platform-assets", hosts: ["www.nuget.org", "globalcdn.nuget.org"]}
	testing: {tested: true, marker: "csharp", fixtureRepo: "csharp", testDir: "csharp"}
	ci: _CIExpected & _BatchJVM & _CIAllOS & _SkipEverywhere
	capabilities: implementationSupport: "verified"
}
