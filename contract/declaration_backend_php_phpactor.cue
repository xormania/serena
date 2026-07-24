package contract

backends: php_phpactor: #DeclaredBackend & {
	id:       "php_phpactor"
	language: "php"
	role:     "alternate"
	class: {module: "phpactor", name: "PhpactorServer"}
	status: "experimental"
	matcher: sharedArmWith: "php"
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/phpactor.py#DEFAULT_PHPACTOR_VERSION"], pin: "2025.12.21.1", checksums: "default-version-only", hosts: ["github.com"]}
	testing: {tested: true, marker: "php", fixtureRepo: "php", aliasOf: "php", testDir: "php"}
	ci: _CIExpected & _BatchOther & _CIAllOS & {skipPolicy: {category: 3, toolProbe: "php"}}
}
