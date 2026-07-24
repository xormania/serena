package contract

backends: solidity: #DeclaredBackend & {
	id:       "solidity"
	language: "solidity"
	role:     "sole"
	class: {module: "solidity_language_server", name: "SolidityLanguageServer"}
	status: "experimental"
	matcher: extensions: [".sol"]
	provisioning: {
		strategy: "composite"
		owner: {runtime: "serena", ci: "runtime"}
		cacheInputs: [
			"src/solidlsp/language_servers/solidity_language_server.py#DEFAULT_SOLIDITY_LANGUAGE_SERVER_VERSION",
			"src/solidlsp/language_servers/solidity_language_server.py#DEFAULT_FORGE_VERSION",
		]
		primary: {strategy: "npm", packages: [{name: "@nomicfoundation/solidity-language-server", pin: "0.8.4"}]}
		companions: [{
			name: "forge"
			provisioning: {
				strategy: "npm"
				packages: [
					{name: "@foundry-rs/forge-linux-amd64", pin: "1.5.1"},
					{name: "@foundry-rs/forge-linux-arm64", pin: "1.5.1"},
					{name: "@foundry-rs/forge-darwin-amd64", pin: "1.5.1"},
					{name: "@foundry-rs/forge-darwin-arm64", pin: "1.5.1"},
					{name: "@foundry-rs/forge-win32-amd64", pin: "1.5.1"},
				]
			}
		}]
	}
	platforms: {
		supported: ["linux", "macos", "windows"]
		excluded: []
		archNotes: "Forge npm packages cover Linux and macOS x64/ARM64 and Windows x64."
	}
	testing: {tested: true, marker: "solidity", fixtureRepo: "solidity", testDir: "solidity"}
	ci: _CIExpected & _BatchCatchAll & _CIAllOS & _SkipEverywhere
}
