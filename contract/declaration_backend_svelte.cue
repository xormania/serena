package contract

backends: svelte: #DeclaredBackend & {
	id:       "svelte"
	language: "svelte"
	role:     "sole"
	class: {module: "svelte_language_server", name: "SvelteLanguageServer"}
	status: "stable"
	matcher: extensions: [".svelte", ".cts", ".cjs", ".mts", ".mjs", ".ts", ".js"]
	provisioning: {strategy: "composite", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/svelte_language_server.py", "test/resources/repos/svelte/test_repo/package-lock.json"], primary: {strategy: "npm", packages: [{name: "svelte-language-server", pin: "0.18.0"}]}, companions: [{name: "typescript", provisioning: {strategy: "npm", packages: [{name: "typescript", pin: "6.0.3"}, {name: "typescript-language-server", pin: "5.1.3"}, {name: "typescript-svelte-plugin", pin: "0.3.52"}]}}]}
	testing: {tested: true, marker: "svelte", fixtureRepo: "svelte", testDir: "svelte", bootstrap: {required: true, steps: [{kind: "npm-ci", detail: "npm ci"}, {kind: "sync-cmd", detail: "svelte-kit sync"}], produces: ["node_modules/svelte/package.json", "node_modules/@sveltejs/adapter-auto/package.json", ".svelte-kit/tsconfig.json"], onFailure: {ci: "skip", local: "skip"}}}
	ci: _CIExpected & _BatchCatchAll & _CIAllOS & _SkipEverywhere
}
