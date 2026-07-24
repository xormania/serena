package contract

backends: csharp_omnisharp: #DeclaredBackend & {
	id:       "csharp_omnisharp"
	language: "csharp"
	role:     "alternate"
	class: {module: "omnisharp", name: "OmniSharp"}
	status: "experimental"
	matcher: sharedArmWith: "csharp"
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "none"}, cacheInputs: ["src/solidlsp/language_servers/omnisharp.py#DEFAULT_OMNISHARP_VERSION"], pin: "1.39.10", checksums: "default-version-only", hosts: ["github.com"]}
	testing: {tested: false, waiver: "W-TEST-OMNISHARP"}
	ci: {expected: false, waiver: "W-TEST-OMNISHARP", skipPolicy: {category: 4}}
}
