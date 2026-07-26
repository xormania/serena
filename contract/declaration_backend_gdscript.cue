package contract

backends: gdscript: #DeclaredBackend & {
	id:       "gdscript"
	language: "gdscript"
	role:     "sole"
	class: {module: "godot_language_server", name: "GodotLanguageServer"}
	status: "stable"
	matcher: extensions: [".gd", ".gdscript"]
	provisioning: {strategy: "tcp", owner: {runtime: "user", ci: "none"}, cacheInputs: [], host: "127.0.0.1", port: 6005}
	testing: {tested: false, waiver: "W-TEST-GDSCRIPT"}
	ci: {expected: false, waiver: "W-TEST-GDSCRIPT", skipPolicy: {category: 4}}
}
