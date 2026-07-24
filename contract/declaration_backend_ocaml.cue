package contract

backends: ocaml: #DeclaredBackend & {
	id:       "ocaml"
	language: "ocaml"
	role:     "sole"
	class: {module: "ocaml_lsp_server", name: "OcamlLanguageServer"}
	status: "stable"
	matcher: extensions: [".ml", ".mli", ".re", ".rei"]
	provisioning: {strategy: "path", owner: {runtime: "project", ci: "workflow-step"}, cacheInputs: [".github/workflows/pytest.yml#Install OCaml language server"], executables: ["opam", "ocamllsp"]}
	testing: {tested: true, marker: "ocaml", fixtureRepo: "ocaml", testDir: "ocaml"}
	ci: _CIExpected & _BatchNiche & _CILinux & {skipPolicy: {category: 3, toolProbe: "opam:ocaml-lsp-server"}}
}
