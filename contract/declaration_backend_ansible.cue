package contract

backends: ansible: #DeclaredBackend & {
	id:       "ansible"
	language: "ansible"
	role:     "sole"
	class: {module: "ansible_language_server", name: "AnsibleLanguageServer"}
	status: "experimental"
	matcher: extensions: [".yaml", ".yml"]
	provisioning: {strategy: "npm", owner: {runtime: "serena", ci: "workflow-step"}, cacheInputs: ["src/solidlsp/language_servers/ansible_language_server.py#DEFAULT_ANSIBLE_LANGUAGE_SERVER_VERSION"], packages: [{name: "@ansible/ansible-language-server", pin: "1.2.3"}]}
	platforms: {supported: ["linux", "macos"], excluded: [{os: "windows", reason: "ansible-language-server has no native Windows support."}]}
	testing: {tested: true, marker: "ansible", fixtureRepo: "ansible", testDir: "ansible"}
	ci: _CIExpected & _BatchOther & _CINonWindows & {skipPolicy: {category: 3, toolProbe: "ansible-language-server"}}
}
