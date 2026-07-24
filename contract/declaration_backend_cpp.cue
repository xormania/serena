package contract

backends: cpp: #DeclaredBackend & {
	id:       "cpp"
	language: "cpp"
	role:     "default"
	class: {module: "clangd_language_server", name: "ClangdLanguageServer"}
	status: "stable"
	matcher: {extensions: [".c", ".h", ".c++", ".cc", ".cp", ".cpp", ".cxx", ".hh", ".hpp", ".hxx", ".inl", ".ipp", ".tpp", ".txx", ".m", ".mm", ".c++m", ".cppm", ".cxxm", ".ixx", ".cu", ".hip", ".cl", ".clcpp", ".ino"], caseSensitive: false}
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "image"}, cacheInputs: ["src/solidlsp/language_servers/clangd_language_server.py#clangd_version"], pin: "19.1.2", checksums: "default-version-only", hosts: ["github.com", "release-assets.githubusercontent.com"]}
	testing: {tested: true, marker: "cpp", fixtureRepo: "cpp", testDir: "cpp"}
	ci: _CIExpected & _BatchNative & _CIAllOS & {skipPolicy: {category: 3, toolProbe: "clangd"}}
}
