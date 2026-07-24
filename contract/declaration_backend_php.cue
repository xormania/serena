package contract

backends: php: #DeclaredBackend & {
	id:       "php"
	language: "php"
	role:     "default"
	class: {module: "intelephense", name: "Intelephense"}
	status: "stable"
	matcher: extensions: [".php", ".phtml"]
	provisioning: {strategy: "npm", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/intelephense.py#DEFAULT_INTELEPHENSE_VERSION"], packages: [{name: "intelephense", pin: "1.14.4"}]}
	testing: {tested: true, marker: "php", fixtureRepo: "php", testDir: "php"}
	ci: _CIExpected & _BatchOther & _CIAllOS & _SkipEverywhere
}
