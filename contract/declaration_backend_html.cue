package contract

backends: html: #DeclaredBackend & {
	id:       "html"
	language: "html"
	role:     "sole"
	class: {module: "vscode_html_language_server", name: "VsCodeHtmlLanguageServer"}
	status: "experimental"
	matcher: extensions: [".html", ".htm"]
	provisioning: {strategy: "npm", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/vscode_html_language_server.py#DEFAULT_PACKAGE_VERSION"], packages: [{name: "vscode-langservers-extracted", pin: "4.10.0"}]}
	testing: {tested: true, marker: "html", fixtureRepo: "html", testDir: "html_ls"}
	ci: _CIExpected & _BatchCatchAll & _CIAllOS & _SkipEverywhere
}
