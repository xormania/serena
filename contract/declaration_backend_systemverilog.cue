package contract

backends: systemverilog: #DeclaredBackend & {
	id:       "systemverilog"
	language: "systemverilog"
	role:     "sole"
	class: {module: "systemverilog_server", name: "SystemVerilogLanguageServer"}
	status: "stable"
	matcher: extensions: [".sv", ".svh", ".v", ".vh"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "workflow-step"}, cacheInputs: ["src/solidlsp/language_servers/systemverilog_server.py#verible_version"], pin: "v0.0-4051-g9fdb4057", checksums: "all-platform-assets", hosts: ["github.com"]}
	testing: {tested: true, marker: "systemverilog", fixtureRepo: "systemverilog", testDir: "systemverilog"}
	ci: _CIExpected & _BatchOther & _CIAllOS & {skipPolicy: {category: 3, toolProbe: "verible-verilog-ls"}} & {installStep: "Install verible-verilog-ls (SystemVerilog Language Server)"}
}
