package contract

backends: angular: #DeclaredBackend & {
	id:       "angular"
	language: "angular"
	role:     "sole"
	class: {module: "angular_language_server", name: "AngularLanguageServer"}
	status: "experimental"
	matcher: extensions: [".html", ".htm", ".ctsx", ".cts", ".mtsx", ".mts", ".tsx", ".ts"]
	provisioning: {strategy: "composite", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/angular_language_server.py#DEFAULT_ANGULAR_LANGUAGE_SERVER_VERSION", "test/resources/repos/angular/test_repo/package-lock.json"], primary: {strategy: "npm", packages: [{name: "@angular/language-server", pin: "21.2.10"}, {name: "@angular/language-service", pin: "21.2.10"}]}, companions: [{name: "typescript", provisioning: {strategy: "npm", packages: [{name: "typescript", pin: "5.9.3"}, {name: "typescript-language-server", pin: "5.1.3"}]}}]}
	testing: {tested: true, marker: "angular", fixtureRepo: "angular", testDir: "angular"}
	ci: _CIExpected & _BatchCatchAll & _CIAllOS & _SkipEverywhere
	capabilities: implementationSupport: "verified"
}
