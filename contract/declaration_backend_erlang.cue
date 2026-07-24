package contract

backends: erlang: #DeclaredBackend & {
	id:       "erlang"
	language: "erlang"
	role:     "sole"
	class: {module: "erlang_language_server", name: "ErlangLanguageServer"}
	status: "stable"
	matcher: extensions: [".erl", ".hrl", ".escript", ".config", ".app", ".app.src"]
	provisioning: {strategy: "path", owner: {runtime: "user", ci: "none"}, cacheInputs: [], executables: ["erlang_ls"]}
	platforms: {supported: ["linux", "macos"], excluded: [{os: "windows", reason: "The Erlang fixture toolchain is unavailable on Windows."}]}
	testing: {tested: true, marker: "erlang", fixtureRepo: "erlang", testDir: "erlang"}
	ci: {expected: false, waiver: "W-CI-ERLANG", skipPolicy: {category: 3, toolProbe: "erlang_ls"}}
}
