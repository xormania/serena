package contract

backends: fsharp: #DeclaredBackend & {
	id:       "fsharp"
	language: "fsharp"
	role:     "sole"
	class: {module: "fsharp_language_server", name: "FSharpLanguageServer"}
	status: "stable"
	matcher: extensions: [".fs", ".fsx", ".fsi"]
	provisioning: {strategy: "dotnet-tool", owner: {runtime: "serena", ci: "none"}, cacheInputs: ["src/solidlsp/language_servers/fsharp_language_server.py#FSAUTOCOMPLETE_VERSION"], package: "fsautocomplete", pin: "0.83.0"}
	testing: {tested: true, marker: "fsharp", fixtureRepo: "fsharp", testDir: "fsharp"}
	ci: {expected: false, waiver: "W-CI-NEVER-RUN-FSHARP", skipPolicy: {category: 1, waiver: "W-SKIP-FSHARP", reason: "F# language server tests are unreliable."}}
}
