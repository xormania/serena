package contract

backends: al: #DeclaredBackend & {
	id:       "al"
	language: "al"
	role:     "sole"
	class: {module: "al_language_server", name: "ALLanguageServer"}
	status: "stable"
	matcher: extensions: [".al", ".dal"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/al_language_server.py#DEFAULT_AL_EXTENSION_VERSION"], pin: "18.0.2242655", checksums: "default-version-only", hosts: ["marketplace.visualstudio.com"]}
	testing: {tested: true, marker: "al", fixtureRepo: "al", testDir: "al"}
	ci: _CIExpected & _BatchOther & _CIAllOS & _SkipEverywhere
}
