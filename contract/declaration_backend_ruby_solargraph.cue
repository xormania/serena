package contract

backends: ruby_solargraph: #DeclaredBackend & {
	id:       "ruby_solargraph"
	language: "ruby"
	role:     "alternate"
	class: {module: "solargraph", name: "Solargraph"}
	status: "experimental"
	matcher: extensions: [".rb"]
	provisioning: {strategy: "package-manager", owner: {runtime: "project", ci: "none"}, cacheInputs: ["Gemfile.lock"], manager: "bundler/gem", pin: "project:Gemfile.lock"}
	testing: {tested: false, waiver: "W-TEST-SOLARGRAPH"}
	ci: {expected: false, waiver: "W-TEST-SOLARGRAPH", skipPolicy: {category: 4}}
}
