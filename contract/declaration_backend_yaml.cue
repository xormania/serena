package contract

backends: yaml: #DeclaredBackend & {
	id:       "yaml"
	language: "yaml"
	role:     "sole"
	class: {module: "yaml_language_server", name: "YamlLanguageServer"}
	status: "experimental"
	matcher: extensions: [".yaml", ".yml"]
	provisioning: {strategy: "npm", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/yaml_language_server.py#DEFAULT_YAML_LANGUAGE_SERVER_VERSION"], packages: [{name: "yaml-language-server", pin: "1.19.2"}]}
	testing: {tested: true, marker: "yaml", fixtureRepo: "yaml", testDir: "yaml_ls"}
	ci: _CIExpected & _BatchOther & _CIAllOS & _SkipEverywhere
}
