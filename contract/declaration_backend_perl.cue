package contract

backends: perl: #DeclaredBackend & {
	id:       "perl"
	language: "perl"
	role:     "sole"
	class: {module: "perl_language_server", name: "PerlLanguageServer"}
	status: "stable"
	matcher: extensions: [".pl", ".pm", ".t"]
	provisioning: {strategy: "path", owner: {runtime: "user", ci: "workflow-step"}, cacheInputs: [".github/workflows/pytest.yml#Install Perl::LanguageServer"], executables: ["perl"]}
	platforms: {
		supported: ["linux", "macos"]
		excluded: [{os: "windows", reason: "The CI Perl::LanguageServer installation is explicitly disabled on Windows."}]
	}
	testing: {tested: true, marker: "perl", fixtureRepo: "perl", testDir: "perl"}
	ci: _CIExpected & _BatchNiche & _CILinux & {skipPolicy: {category: 3, toolProbe: "Perl::LanguageServer"}}
}
