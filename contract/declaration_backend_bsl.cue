package contract

backends: bsl: #DeclaredBackend & {
	id:       "bsl"
	language: "bsl"
	role:     "sole"
	class: {module: "bsl_language_server", name: "BSLLanguageServer"}
	status: "stable"
	matcher: extensions: [".bsl", ".os"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "none"}, cacheInputs: ["src/solidlsp/language_servers/bsl_language_server.py#DEFAULT_BSL_LS_VERSION"], pin: "0.29.0", checksums: "default-version-only", hosts: ["github.com"]}
	testing: {tested: true, marker: "bsl", fixtureRepo: "bsl", testDir: "bsl"}
	ci: {expected: false, waiver: "W-CI-NEVER-RUN-BSL", skipPolicy: {category: 1, waiver: "W-SKIP-BSL", reason: "BSL tests are slow and flaky."}}
}
