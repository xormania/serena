package contract

backends: haxe: #DeclaredBackend & {
	id:       "haxe"
	language: "haxe"
	role:     "sole"
	class: {module: "haxe_language_server", name: "HaxeLanguageServer"}
	status: "stable"
	matcher: extensions: [".hx"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "workflow-step"}, cacheInputs: ["src/solidlsp/language_servers/haxe_language_server.py#DEFAULT_VSHAXE_VERSION"], pin: "2.34.2", checksums: "default-version-only", hosts: ["marketplace.visualstudio.com"]}
	testing: {tested: true, marker: "haxe", fixtureRepo: "haxe", testDir: "haxe"}
	ci: _CIExpected & _BatchOther & _CIAllOS & _SkipEverywhere & {installStep: "Install Haxe"}
}
