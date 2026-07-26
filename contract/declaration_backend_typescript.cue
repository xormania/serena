package contract

backends: typescript: #DeclaredBackend & {
	id:       "typescript"
	language: "typescript"
	role:     "default"
	class: {module: "typescript_language_server", name: "TypeScriptLanguageServer"}
	status: "stable"
	matcher: extensions: [".ctsx", ".cjsx", ".cts", ".cjs", ".mtsx", ".mjsx", ".mts", ".mjs", ".tsx", ".jsx", ".ts", ".js"]
	provisioning: {strategy: "npm", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/typescript_language_server.py#DEFAULT_TYPESCRIPT_VERSION"], packages: [{name: "typescript-language-server", pin: "5.1.3"}, {name: "typescript", pin: "5.9.3"}]}
	testing: {tested: true, marker: "typescript", fixtureRepo: "typescript", testDir: "typescript"}
	ci: _CIExpected & _BatchCatchAll & _CIAllOS & _SkipEverywhere
	capabilities: implementationSupport: "verified"
}
