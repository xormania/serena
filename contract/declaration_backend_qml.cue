package contract

backends: qml: #DeclaredBackend & {
	id:       "qml"
	language: "qml"
	role:     "sole"
	class: {module: "qml_language_server", name: "QmlLanguageServer"}
	status: "stable"
	matcher: extensions: [".qml"]
	provisioning: {strategy: "path", owner: {runtime: "user", ci: "workflow-step"}, cacheInputs: [".github/workflows/pytest.yml#Install qmlls (QML Language Server)"], executables: ["qmlls6", "qmlls"]}
	testing: {tested: true, marker: "qml", fixtureRepo: "qml", testDir: "qml"}
	ci: _CIExpected & _BatchOther & _CILinux & {skipPolicy: {category: 2, loudOn: {os: ["linux"], ci: true}, toolProbe: "qmlls6|qmlls"}}
}
