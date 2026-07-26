package contract

backends: matlab: #DeclaredBackend & {
	id:       "matlab"
	language: "matlab"
	role:     "sole"
	class: {module: "matlab_language_server", name: "MatlabLanguageServer"}
	status: "stable"
	matcher: extensions: [".m", ".mlx", ".mlapp"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "none"}, cacheInputs: ["src/solidlsp/language_servers/matlab_language_server.py#DEFAULT_MATLAB_EXTENSION_VERSION"], pin: "1.3.9", checksums: "default-version-only", hosts: ["marketplace.visualstudio.com"]}
	testing: {tested: true, marker: "matlab", fixtureRepo: "matlab", testDir: "matlab"}
	ci: {expected: false, waiver: "W-CI-NEVER-RUN-MATLAB", skipPolicy: {category: 3, toolProbe: "MATLAB"}}
}
