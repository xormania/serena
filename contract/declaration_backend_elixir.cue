package contract

backends: elixir: #DeclaredBackend & {
	id:       "elixir"
	language: "elixir"
	role:     "sole"
	class: {module: "elixir_tools.elixir_tools", name: "ElixirTools"}
	status: "stable"
	matcher: extensions: [".ex", ".exs"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "none"}, cacheInputs: ["src/solidlsp/language_servers/elixir_tools/elixir_tools.py#EXPERT_VERSION"], pin: "v0.1.0-rc.6", checksums: "default-version-only", hosts: ["github.com"]}
	testing: {tested: true, marker: "elixir", fixtureRepo: "elixir", testDir: "elixir", bootstrap: {required: true, steps: [{kind: "mix", detail: "mix deps.get"}, {kind: "mix", detail: "mix compile"}], produces: ["deps", "_build"], onFailure: {ci: "skip", local: "skip"}}}
	ci: {expected: false, waiver: "W-CI-NEVER-RUN-ELIXIR", skipPolicy: {category: 3, toolProbe: "expert"}}
}
