package contract

backends: fortran: #DeclaredBackend & {
	id:       "fortran"
	language: "fortran"
	role:     "sole"
	class: {module: "fortran_language_server", name: "FortranLanguageServer"}
	status: "stable"
	matcher: {extensions: [".f90", ".f95", ".f03", ".f08", ".f", ".for", ".fpp"], caseSensitive: false}
	provisioning: {strategy: "uvx", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/fortran_language_server.py#FORTLS_VERSION"], package: "fortls", pin: "3.2.2"}
	testing: {tested: true, marker: "fortran", fixtureRepo: "fortran", testDir: "fortran"}
	ci: _CIExpected & _BatchOther & _CIAllOS & _SkipEverywhere
}
