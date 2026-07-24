package contract

backends: powershell: #DeclaredBackend & {
	id:       "powershell"
	language: "powershell"
	role:     "sole"
	class: {module: "powershell_language_server", name: "PowerShellLanguageServer"}
	status: "stable"
	matcher: extensions: [".ps1", ".psm1", ".psd1"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/powershell_language_server.py#DEFAULT_PSES_VERSION"], pin: "4.4.0", checksums: "default-version-only", hosts: ["github.com"]}
	testing: {tested: true, marker: "powershell", fixtureRepo: "powershell", testDir: "powershell"}
	ci: _CIExpected & _BatchOther & _CIAllOS & _SkipEverywhere
}
