package contract

backends: ada: #DeclaredBackend & {
	id:       "ada"
	language: "ada"
	role:     "sole"
	class: {module: "ada_language_server", name: "AdaLanguageServer"}
	status: "stable"
	matcher: {extensions: [".ads", ".adb", ".ada"], caseSensitive: false}
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/ada_language_server.py#DEFAULT_ALS_VERSION"], pin: "2026.2.202604091", checksums: "default-version-only", hosts: ["github.com"]}
	testing: {tested: true, marker: "ada", fixtureRepo: "ada", testDir: "ada"}
	ci: _CIExpected & _BatchOther & _CIAllOS & _SkipEverywhere
}
