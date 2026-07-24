package contract

backends: julia: #DeclaredBackend & {
	id:       "julia"
	language: "julia"
	role:     "sole"
	class: {module: "julia_server", name: "JuliaLanguageServer"}
	status: "stable"
	matcher: extensions: [".jl"]
	provisioning: {strategy: "package-manager", owner: {runtime: "serena", ci: "workflow-step"}, cacheInputs: ["src/solidlsp/language_servers/julia_server.py"], manager: "julia Pkg", pin: "UNPINNED", waiver: "W-PROV-JULIA-UNPINNED"}
	testing: {tested: true, marker: "julia", fixtureRepo: "julia", testDir: "julia"}
	ci: _CIExpected & _BatchNiche & _CILinux & {skipPolicy: {category: 3, toolProbe: "julia"}}
}
