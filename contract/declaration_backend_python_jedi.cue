package contract

backends: python_jedi: #DeclaredBackend & {
	id:       "python_jedi"
	language: "python"
	role:     "alternate"
	class: {module: "jedi_server", name: "JediServer"}
	status: "experimental"
	matcher: sharedArmWith: "python"
	provisioning: {strategy: "path", owner: {runtime: "user", ci: "none"}, cacheInputs: [], executables: ["jedi-language-server"]}
	testing: {tested: false, waiver: "W-TEST-JEDI"}
	ci: {expected: false, waiver: "W-TEST-JEDI", skipPolicy: {category: 4}}
}
