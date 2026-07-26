package contract

backends: cue: #DeclaredBackend & {
	id:       "cue"
	language: "cue"
	role:     "sole"
	class: {module: "cue_language_server", name: "CueLanguageServer"}
	status: "stable"
	matcher: extensions: [".cue"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/cue_language_server.py#DEFAULT_CUE_VERSION"], pin: "v0.16.1", checksums: "all-platform-assets", hosts: ["github.com"]}
	testing: {tested: true, marker: "cue", fixtureRepo: "cue", testDir: "cue"}
	ci: _CIExpected & _BatchOther & _CIAllOS & _SkipEverywhere
}
