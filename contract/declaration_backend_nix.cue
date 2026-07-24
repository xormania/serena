package contract

backends: nix: #DeclaredBackend & {
	id:       "nix"
	language: "nix"
	role:     "sole"
	class: {module: "nixd_ls", name: "NixLanguageServer"}
	status: "stable"
	matcher: extensions: [".nix"]
	provisioning: {strategy: "package-manager", owner: {runtime: "serena", ci: "workflow-step"}, cacheInputs: ["src/solidlsp/language_servers/nixd_ls.py"], manager: "nix profile", pin: "UNPINNED", waiver: "W-PROV-NIXD-UNPINNED"}
	testing: {tested: true, marker: "nix", fixtureRepo: "nix", testDir: "nix"}
	ci: _CIExpected & _BatchNiche & _CILinux & {skipPolicy: {category: 3, toolProbe: "nixd"}}
}
