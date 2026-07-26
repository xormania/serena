package contract

backends: bash: #DeclaredBackend & {
	id:       "bash"
	language: "bash"
	role:     "sole"
	class: {module: "bash_language_server", name: "BashLanguageServer"}
	status: "stable"
	matcher: extensions: [".sh", ".bash"]
	provisioning: {strategy: "composite", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/bash_language_server.py#DEFAULT_BASH_LANGUAGE_SERVER_VERSION", "src/solidlsp/language_servers/bash_language_server.py#_SHELLCHECK_VERSION"], primary: {strategy: "npm", packages: [{name: "bash-language-server", pin: "5.6.0"}]}, companions: [{name: "shellcheck", provisioning: {strategy: "download", pin: "0.10.0", checksums: "default-version-only", hosts: ["github.com"]}}]}
	testing: {tested: true, marker: "bash", fixtureRepo: "bash", testDir: "bash"}
	ci: _CIExpected & _BatchOther & _CIAllOS & _SkipEverywhere
}
