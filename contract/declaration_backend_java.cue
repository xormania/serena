package contract

backends: java: #DeclaredBackend & {
	id:       "java"
	language: "java"
	role:     "sole"
	class: {module: "eclipse_jdtls", name: "EclipseJDTLS"}
	status: "stable"
	matcher: extensions: [".java"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/eclipse_jdtls.py#DEFAULT_VSCODE_JAVA_VERSION", "src/solidlsp/language_servers/eclipse_jdtls.py#DEFAULT_INTELLICODE_VERSION"], pin: "1.54.0-923", checksums: "default-version-only", hosts: ["marketplace.visualstudio.com", "services.gradle.org", "github.com"]}
	testing: {tested: true, marker: "java", fixtureRepo: "java", testDir: "java"}
	ci: _CIExpected & _BatchJVM & _CIAllOS & _SkipEverywhere
	capabilities: implementationSupport: "verified"
}
