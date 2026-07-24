package contract

backends: php_phpantom: #DeclaredBackend & {
	id:       "php_phpantom"
	language: "php"
	role:     "alternate"
	class: {module: "phpantom", name: "PHPantomServer"}
	status: "experimental"
	matcher: sharedArmWith: "php"
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/phpantom.py#DEFAULT_PHPANTOM_VERSION"], pin: "0.8.0", checksums: "default-version-only", hosts: ["github.com"]}
	testing: {tested: true, marker: "php", fixtureRepo: "php", aliasOf: "php", testDir: "php"}
	ci: _CIExpected & _BatchOther & _CIAllOS & {skipPolicy: {category: 3, toolProbe: "php"}}
}
