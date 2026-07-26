package contract

backends: msl: #DeclaredBackend & {
	id:       "msl"
	language: "msl"
	role:     "sole"
	class: {module: "msl_language_server", name: "MslLanguageServer"}
	status: "stable"
	matcher: extensions: [".mrc"]
	provisioning: {strategy: "bundled", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["pyproject.toml#pygls", "uv.lock"], enginePin: "pyproject.toml#pygls==2.1.1"}
	testing: {tested: true, marker: "msl", fixtureRepo: "msl", testDir: "msl"}
	ci: _CIExpected & _BatchOther & _CIAllOS & _SkipEverywhere
}
