package contract

backends: groovy: #DeclaredBackend & {
	id:       "groovy"
	language: "groovy"
	role:     "sole"
	class: {module: "groovy_language_server", name: "GroovyLanguageServer"}
	status: "experimental"
	matcher: extensions: [".groovy", ".gvy"]
	provisioning: {
		strategy: "composite"
		owner: {runtime: "user", ci: "workflow-step"}
		cacheInputs: ["src/solidlsp/language_servers/groovy_language_server.py#DEFAULT_VSCODE_JAVA_VERSION"]
		primary: {strategy: "path", executables: ["java"]}
		companions: [{
			name: "vscode-java"
			provisioning: {
				strategy:  "download"
				pin:       "1.42.0-561"
				checksums: "all-platform-assets"
				hosts: [
					"github.com",
					"release-assets.githubusercontent.com",
					"objects.githubusercontent.com",
				]
			}
		}]
	}
	testing: {tested: true, marker: "groovy", fixtureRepo: "groovy", testDir: "groovy"}
	ci: _CIExpected & _BatchJVM & _CIAllOS & _SkipEverywhere
}
