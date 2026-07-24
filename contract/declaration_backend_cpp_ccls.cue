package contract

backends: cpp_ccls: #DeclaredBackend & {
	id:       "cpp_ccls"
	language: "cpp"
	role:     "alternate"
	class: {module: "ccls_language_server", name: "CCLS"}
	status: "experimental"
	matcher: {extensions: [".c", ".h", ".c++", ".cc", ".cp", ".cpp", ".cxx", ".hh", ".hpp", ".hxx", ".inl", ".ipp", ".tpp", ".txx", ".m", ".mm", ".ino"], caseSensitive: false}
	provisioning: {strategy: "path", owner: {runtime: "user", ci: "workflow-step"}, cacheInputs: [".github/workflows/pytest.yml#Install ccls"], executables: ["ccls"]}
	platforms: {supported: ["linux", "macos"], excluded: [{os: "windows", reason: "No current Windows ccls binary is available."}]}
	testing: {tested: true, marker: "cpp", fixtureRepo: "cpp", aliasOf: "cpp", testDir: "cpp"}
	ci: _CIExpected & _BatchNative & _CINonWindows & {skipPolicy: {category: 3, toolProbe: "ccls"}} & {installStep: "Install ccls (C/C++ Language Server)"}
}
