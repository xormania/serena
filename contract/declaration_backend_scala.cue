package contract

backends: scala: #DeclaredBackend & {
	id:       "scala"
	language: "scala"
	role:     "sole"
	class: {module: "scala_language_server", name: "ScalaLanguageServer"}
	status: "stable"
	matcher: extensions: [".scala", ".sbt"]
	provisioning: {strategy: "package-manager", owner: {runtime: "serena", ci: "workflow-step"}, cacheInputs: ["src/solidlsp/language_servers/scala_language_server.py#DEFAULT_METALS_VERSION"], manager: "coursier", pin: "1.6.4"}
	testing: {tested: true, marker: "scala", fixtureRepo: "scala", testDir: "scala"}
	ci: _CIExpected & _BatchJVM & _CIAllOS & _SkipEverywhere & {installStep: "Setup Java (for JVM based languages)"}
}
