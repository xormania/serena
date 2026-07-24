package contract

backends: terraform: #DeclaredBackend & {
	id:       "terraform"
	language: "terraform"
	role:     "sole"
	class: {module: "terraform_ls", name: "TerraformLS"}
	status: "stable"
	matcher: extensions: [".tf", ".tfvars", ".tfstate"]
	provisioning: {strategy: "download", owner: {runtime: "serena", ci: "workflow-step"}, cacheInputs: ["src/solidlsp/language_servers/terraform_ls.py#DEFAULT_TERRAFORM_LS_VERSION"], pin: "0.36.5", checksums: "default-version-only", hosts: ["github.com"]}
	testing: {tested: true, marker: "terraform", fixtureRepo: "terraform", testDir: "terraform"}
	ci: _CIExpected & _BatchOther & _CIAllOS & {skipPolicy: {category: 2, loudOn: {os: ["linux", "macos", "windows"], ci: true}, toolProbe: "terraform"}}
}
