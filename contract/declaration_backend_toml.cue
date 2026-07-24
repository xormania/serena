package contract

backends: toml: #DeclaredBackend & {
	id:       "toml"
	language: "toml"
	role:     "sole"
	class: {module: "taplo_server", name: "TaploServer"}
	status: "experimental"
	matcher: extensions: [".toml"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/taplo_server.py#DEFAULT_TAPLO_VERSION"], pin: "0.10.0", checksums: "default-version-only", hosts: ["github.com"]}
	testing: {tested: true, marker: "toml", fixtureRepo: "toml", testDir: "toml"}
	ci: _CIExpected & _BatchOther & _CIAllOS & _SkipEverywhere
}
