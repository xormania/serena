package contract

backends: ruby: #DeclaredBackend & {
	id:       "ruby"
	language: "ruby"
	role:     "default"
	class: {module: "ruby_lsp", name: "RubyLsp"}
	status: "stable"
	matcher: extensions: [".rb", ".erb"]
	provisioning: {strategy: "package-manager", owner: {runtime: "project", ci: "workflow-step"}, cacheInputs: ["src/solidlsp/language_servers/ruby_lsp.py#RUBY_LSP_VERSION"], manager: "bundler/gem", pin: "0.26.8"}
	testing: {tested: true, marker: "ruby", fixtureRepo: "ruby", testDir: "ruby"}
	ci: _CIExpected & _BatchOther & _CIAllOS & _SkipEverywhere
}
