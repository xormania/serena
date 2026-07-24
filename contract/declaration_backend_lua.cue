package contract

backends: lua: #DeclaredBackend & {
	id:       "lua"
	language: "lua"
	role:     "sole"
	class: {module: "lua_ls", name: "LuaLanguageServer"}
	status: "stable"
	matcher: extensions: [".lua"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "workflow-step"}, cacheInputs: ["src/solidlsp/language_servers/lua_ls.py#DEFAULT_LUA_LS_VERSION"], pin: "3.15.0", checksums: "default-version-only", hosts: ["github.com"]}
	testing: {tested: true, marker: "lua", fixtureRepo: "lua", testDir: "lua"}
	ci: _CIExpected & _BatchOther & _CIAllOS & _SkipEverywhere
}
