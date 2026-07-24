package contract

backends: solidity: #DeclaredBackend & {
	id:       "solidity"
	language: "solidity"
	role:     "sole"
	class: {module: "solidity_language_server", name: "SolidityLanguageServer"}
	status: "experimental"
	matcher: extensions: [".sol"]
	provisioning: {strategy: "composite", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/solidity_language_server.py#DEFAULT_SOLIDITY_LANGUAGE_SERVER_VERSION", "src/solidlsp/language_servers/solidity_language_server.py#DEFAULT_FORGE_VERSION"], primary: {strategy: "npm", packages: [{name: "@nomicfoundation/solidity-language-server", pin: "0.8.4"}]}, companions: [{name: "forge", provisioning: {strategy: "download", pin: "1.5.1", checksums: "default-version-only", hosts: ["github.com"]}}]}
	testing: {tested: true, marker: "solidity", fixtureRepo: "solidity", testDir: "solidity"}
	ci: _CIExpected & _BatchCatchAll & _CIAllOS & _SkipEverywhere
}
