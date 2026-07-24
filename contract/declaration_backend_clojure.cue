package contract

backends: clojure: #DeclaredBackend & {
	id:       "clojure"
	language: "clojure"
	role:     "sole"
	class: {module: "clojure_lsp", name: "ClojureLSP"}
	status: "stable"
	matcher: extensions: [".clj", ".cljs", ".cljc", ".edn"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "workflow-step"}, cacheInputs: ["src/solidlsp/language_servers/clojure_lsp.py#DEFAULT_CLOJURE_LSP_VERSION"], pin: "2026.02.20-16.08.58", checksums: "default-version-only", hosts: ["github.com"]}
	testing: {tested: true, marker: "clojure", fixtureRepo: "clojure", testDir: "clojure"}
	ci: _CIExpected & _BatchJVM & _CIAllOS & {skipPolicy: {category: 3, toolProbe: "clojure"}}
}
