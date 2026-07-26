package contract

backends: dart: #DeclaredBackend & {
	id:       "dart"
	language: "dart"
	role:     "sole"
	class: {module: "dart_language_server", name: "DartLanguageServer"}
	status: "stable"
	matcher: extensions: [".dart"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "runtime"}, cacheInputs: ["src/solidlsp/language_servers/dart_language_server.py#DEFAULT_DART_SDK_VERSION"], pin: "3.7.1", checksums: "all-platform-assets", hosts: ["storage.googleapis.com"]}
	testing: {tested: true, marker: "dart", fixtureRepo: "dart", testDir: "dart"}
	ci: _CIExpected & _BatchOther & _CIAllOS & _SkipEverywhere
}
