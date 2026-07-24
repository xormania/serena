package contract

backends: crystal: #DeclaredBackend & {
	id:       "crystal"
	language: "crystal"
	role:     "sole"
	class: {module: "crystal_language_server", name: "CrystalLanguageServer"}
	status: "stable"
	matcher: extensions: [".cr"]
	provisioning: {strategy: "path", owner: {runtime: "user", ci: "none"}, cacheInputs: [], executables: ["crystalline"]}
	testing: {tested: true, marker: "crystal", fixtureRepo: "crystal", testDir: "crystal"}
	ci: {expected: false, waiver: "W-CI-CRYSTAL", skipPolicy: {category: 3, toolProbe: "crystalline"}}
}
