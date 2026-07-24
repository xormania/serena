package contract

backends: typescript_vts: #DeclaredBackend & {
	id:       "typescript_vts"
	language: "typescript"
	role:     "alternate"
	class: {module: "vts_language_server", name: "VtsLanguageServer"}
	status: "experimental"
	matcher: sharedArmWith: "typescript"
	provisioning: {strategy: "npm", owner: {runtime: "serena", ci: "none"}, cacheInputs: ["src/solidlsp/language_servers/vts_language_server.py#DEFAULT_VTSLS_VERSION"], packages: [{name: "@vtsls/language-server", pin: "0.2.9"}]}
	testing: {tested: false, waiver: "W-TEST-VTS"}
	ci: {expected: false, waiver: "W-TEST-VTS", skipPolicy: {category: 4}}
}
