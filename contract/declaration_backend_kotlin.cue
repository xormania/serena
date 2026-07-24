package contract

backends: kotlin: #DeclaredBackend & {
	id:       "kotlin"
	language: "kotlin"
	role:     "sole"
	class: {module: "kotlin_language_server", name: "KotlinLanguageServer"}
	status: "stable"
	matcher: extensions: [".kt", ".kts"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "none"}, cacheInputs: ["src/solidlsp/language_servers/kotlin_language_server.py#DEFAULT_KOTLIN_LSP_VERSION"], pin: "261.13587.0", checksums: "default-version-only", hosts: ["download.jetbrains.com"]}
	testing: {tested: true, marker: "kotlin", fixtureRepo: "kotlin", testDir: "kotlin"}
	ci: {expected: false, waiver: "W-CI-NEVER-RUN-KOTLIN", skipPolicy: {category: 5, waiver: "W-SKIP-KOTLIN", reason: "Kotlin LSP crashes under CI runner memory limits."}}
}
