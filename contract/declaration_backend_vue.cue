package contract

backends: vue: #DeclaredBackend & {
	id:       "vue"
	language: "vue"
	role:     "sole"
	class: {module: "vue_language_server", name: "VueLanguageServer"}
	status: "stable"
	matcher: extensions: [".vue", ".ctsx", ".cjsx", ".cts", ".cjs", ".mtsx", ".mjsx", ".mts", ".mjs", ".tsx", ".jsx", ".ts", ".js"]
	provisioning: {strategy: "composite", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/vue_language_server.py"], primary: {strategy: "npm", packages: [{name: "@vue/language-server", pin: "3.1.5"}]}, companions: [{name: "typescript", provisioning: {strategy: "npm", packages: [{name: "typescript", pin: "5.9.3"}, {name: "typescript-language-server", pin: "5.1.3"}]}}]}
	testing: {tested: true, marker: "vue", fixtureRepo: "vue", testDir: "vue", bootstrap: {required: true, steps: [{kind: "npm-install", detail: "npm install"}], produces: ["node_modules/vue/package.json"], onFailure: {ci: "fail", local: "skip"}}}
	ci: _CIExpected & _BatchCatchAll & _CIAllOS & _SkipEverywhere
}
