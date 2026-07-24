package contract

// CI layout is declared intent. Workflow extraction remains the code-authoritative observation.
ciLayout: #CILayout & {
	batches: {
		jvm: os: ["linux", "macos", "windows"]
		native: os: ["linux", "macos", "windows"]
		"other-langs": os: ["linux", "macos", "windows"]
		niche: os: ["linux"]
		"catch-all": os: ["linux", "macos", "windows"]
	}
	caches: {
		"uv-venv": {
			workflowName: "Cache uv virtualenv"
			covers: []
			inputs: ["uv.lock"]
			keyTokens: "uv.lock": "hashFiles('uv.lock')"
		}
		gopls: {
			workflowName: "Cache Go binaries"
			covers: ["go"]
			inputs: [".github/workflows/pytest.yml#Install gopls"]
			keyTokens: ".github/workflows/pytest.yml#Install gopls": "@latest"
		}
		swift: {
			workflowName: "Cache Swift toolchain (swiftly)"
			covers: ["swift"]
			inputs: [".github/workflows/pytest.yml#Install Swift with swiftly (macOS)"]
			keyTokens: ".github/workflows/pytest.yml#Install Swift with swiftly (macOS)": "6.1.2"
			versionToken: "v2"
		}
		zls: {
			workflowName: "Cache ZLS (Zig Language Server)"
			covers: ["zig"]
			inputs: [".github/workflows/pytest.yml#Install ZLS (Zig Language Server)"]
			keyTokens: ".github/workflows/pytest.yml#Install ZLS (Zig Language Server)": "0.14.0"
		}
		fpc: {
			workflowName: "Cache Free Pascal Compiler"
			covers: []
			inputs: [".github/workflows/pytest.yml#Install Free Pascal Compiler"]
			keyTokens: ".github/workflows/pytest.yml#Install Free Pascal Compiler": "3.2.2"
		}
		r: {
			workflowName: "Cache R packages (languageserver + its deps)"
			covers: ["r"]
			inputs: [".github/workflows/pytest.yml#Install R language server"]
			keyTokens: ".github/workflows/pytest.yml#Install R language server": "install.packages('languageserver'"
		}
		julia: {
			workflowName: "Cache Julia depot (packages + precompiled)"
			covers: ["julia"]
			inputs: ["src/solidlsp/language_servers/julia_server.py"]
			keyTokens: {}
			managed: true
		}
		perl: {
			workflowName: "Cache Perl::LanguageServer (~/perl5)"
			covers: ["perl"]
			inputs: [".github/workflows/pytest.yml#Install Perl::LanguageServer"]
			keyTokens: ".github/workflows/pytest.yml#Install Perl::LanguageServer": "cpanm --notest --force"
		}
		"language-servers-static": {
			workflowName: "Cache language servers"
			covers: [
				"ada", "al", "angular", "ansible", "bash", "clojure", "csharp", "cue", "dart", "elm",
				"haxe", "hlsl", "html", "java", "json", "latex", "luau", "markdown", "pascal", "php",
				"php_phpactor", "php_phpantom", "powershell", "scss", "solidity", "svelte", "terraform", "toml",
				"typescript", "vue", "yaml",
			]
			inputs: [
				"src/solidlsp/language_servers/ada_language_server.py#DEFAULT_ALS_VERSION",
				"src/solidlsp/language_servers/al_language_server.py#DEFAULT_AL_EXTENSION_VERSION",
				"src/solidlsp/language_servers/angular_language_server.py#DEFAULT_ANGULAR_LANGUAGE_SERVER_VERSION",
				"test/resources/repos/angular/test_repo/package-lock.json",
				"src/solidlsp/language_servers/ansible_language_server.py#DEFAULT_ANSIBLE_LANGUAGE_SERVER_VERSION",
				"src/solidlsp/language_servers/bash_language_server.py#DEFAULT_BASH_LANGUAGE_SERVER_VERSION",
				"src/solidlsp/language_servers/bash_language_server.py#_SHELLCHECK_VERSION",
				"src/solidlsp/language_servers/clojure_lsp.py#DEFAULT_CLOJURE_LSP_VERSION",
				"src/solidlsp/language_servers/csharp_language_server.py#DEFAULT_CSHARP_LANGUAGE_SERVER_VERSION",
				"src/solidlsp/language_servers/cue_language_server.py#DEFAULT_CUE_VERSION",
				"src/solidlsp/language_servers/dart_language_server.py#DEFAULT_DART_SDK_VERSION",
				"src/solidlsp/language_servers/elm_language_server.py#DEFAULT_ELM_LANGUAGE_SERVER_VERSION",
				"src/solidlsp/language_servers/haxe_language_server.py#DEFAULT_VSHAXE_VERSION",
				"src/solidlsp/language_servers/hlsl_language_server.py#_DEFAULT_VERSION",
				"src/solidlsp/language_servers/vscode_html_language_server.py#DEFAULT_PACKAGE_VERSION",
				"src/solidlsp/language_servers/eclipse_jdtls.py#DEFAULT_VSCODE_JAVA_VERSION",
				"src/solidlsp/language_servers/eclipse_jdtls.py#DEFAULT_INTELLICODE_VERSION",
				"src/solidlsp/language_servers/eclipse_jdtls.py#GRADLE_SHA256",
				"src/solidlsp/language_servers/json_language_server.py#DEFAULT_JSON_LANGUAGE_SERVER_VERSION",
				"src/solidlsp/language_servers/texlab_language_server.py#TEXLAB_VERSION",
				"src/solidlsp/language_servers/luau_lsp.py#DEFAULT_LUAU_LSP_VERSION",
				"src/solidlsp/language_servers/marksman.py#DEFAULT_MARKSMAN_VERSION",
				"src/solidlsp/language_servers/pascal_server.py#PASLS_VERSION",
				"src/solidlsp/language_servers/intelephense.py#DEFAULT_INTELEPHENSE_VERSION",
				"src/solidlsp/language_servers/phpactor.py#DEFAULT_PHPACTOR_VERSION",
				"src/solidlsp/language_servers/phpantom.py#DEFAULT_PHPANTOM_VERSION",
				"src/solidlsp/language_servers/powershell_language_server.py#DEFAULT_PSES_VERSION",
				"src/solidlsp/language_servers/some_sass_language_server.py#DEFAULT_PACKAGE_VERSION",
				"src/solidlsp/language_servers/solidity_language_server.py#DEFAULT_SOLIDITY_LANGUAGE_SERVER_VERSION",
				"src/solidlsp/language_servers/solidity_language_server.py#DEFAULT_FORGE_VERSION",
				"src/solidlsp/language_servers/svelte_language_server.py",
				"test/resources/repos/svelte/test_repo/package-lock.json",
				"src/solidlsp/language_servers/terraform_ls.py#DEFAULT_TERRAFORM_LS_VERSION",
				"src/solidlsp/language_servers/taplo_server.py#DEFAULT_TAPLO_VERSION",
				"src/solidlsp/language_servers/typescript_language_server.py#DEFAULT_TYPESCRIPT_VERSION",
				"src/solidlsp/language_servers/vue_language_server.py",
				"src/solidlsp/language_servers/yaml_language_server.py#DEFAULT_YAML_LANGUAGE_SERVER_VERSION",
			]
			keyTokens: {
				"src/solidlsp/language_servers/ada_language_server.py#DEFAULT_ALS_VERSION":                           "2026.2.202604091"
				"src/solidlsp/language_servers/al_language_server.py#DEFAULT_AL_EXTENSION_VERSION":                   "18.0.2242655"
				"src/solidlsp/language_servers/angular_language_server.py#DEFAULT_ANGULAR_LANGUAGE_SERVER_VERSION":   "21.2.10"
				"test/resources/repos/angular/test_repo/package-lock.json":                                           "hashFiles('test/resources/repos/angular/test_repo/package-lock.json')"
				"src/solidlsp/language_servers/ansible_language_server.py#DEFAULT_ANSIBLE_LANGUAGE_SERVER_VERSION":   "1.2.3"
				"src/solidlsp/language_servers/bash_language_server.py#DEFAULT_BASH_LANGUAGE_SERVER_VERSION":         "5.6.0"
				"src/solidlsp/language_servers/bash_language_server.py#_SHELLCHECK_VERSION":                          "0.10.0"
				"src/solidlsp/language_servers/clojure_lsp.py#DEFAULT_CLOJURE_LSP_VERSION":                           "2026.02.20-16.08.58"
				"src/solidlsp/language_servers/csharp_language_server.py#DEFAULT_CSHARP_LANGUAGE_SERVER_VERSION":     "5.5.0-2.26078.4"
				"src/solidlsp/language_servers/cue_language_server.py#DEFAULT_CUE_VERSION":                           "v0.16.1"
				"src/solidlsp/language_servers/dart_language_server.py#DEFAULT_DART_SDK_VERSION":                     "3.7.1"
				"src/solidlsp/language_servers/elm_language_server.py#DEFAULT_ELM_LANGUAGE_SERVER_VERSION":           "2.8.0"
				"src/solidlsp/language_servers/haxe_language_server.py#DEFAULT_VSHAXE_VERSION":                       "2.34.2"
				"src/solidlsp/language_servers/hlsl_language_server.py#_DEFAULT_VERSION":                             "1.3.1"
				"src/solidlsp/language_servers/vscode_html_language_server.py#DEFAULT_PACKAGE_VERSION":               "4.10.0"
				"src/solidlsp/language_servers/eclipse_jdtls.py#DEFAULT_VSCODE_JAVA_VERSION":                         "1.54.0-923"
				"src/solidlsp/language_servers/eclipse_jdtls.py#DEFAULT_INTELLICODE_VERSION":                         "1.2.30"
				"src/solidlsp/language_servers/eclipse_jdtls.py#GRADLE_SHA256":                                       "7197a12f450794931532469d4ff21a59ea2c1cd59a3ec3f89c035c3c420a6999"
				"src/solidlsp/language_servers/json_language_server.py#DEFAULT_JSON_LANGUAGE_SERVER_VERSION":         "1.3.4"
				"src/solidlsp/language_servers/texlab_language_server.py#TEXLAB_VERSION":                             "5.25.1"
				"src/solidlsp/language_servers/luau_lsp.py#DEFAULT_LUAU_LSP_VERSION":                                 "1.63.0"
				"src/solidlsp/language_servers/marksman.py#DEFAULT_MARKSMAN_VERSION":                                 "2024-12-18"
				"src/solidlsp/language_servers/pascal_server.py#PASLS_VERSION":                                       "v0.2.0"
				"src/solidlsp/language_servers/intelephense.py#DEFAULT_INTELEPHENSE_VERSION":                         "1.14.4"
				"src/solidlsp/language_servers/phpactor.py#DEFAULT_PHPACTOR_VERSION":                                 "2025.12.21.1"
				"src/solidlsp/language_servers/phpantom.py#DEFAULT_PHPANTOM_VERSION":                                 "0.8.0"
				"src/solidlsp/language_servers/powershell_language_server.py#DEFAULT_PSES_VERSION":                   "4.4.0"
				"src/solidlsp/language_servers/some_sass_language_server.py#DEFAULT_PACKAGE_VERSION":                 "2.3.8"
				"src/solidlsp/language_servers/solidity_language_server.py#DEFAULT_SOLIDITY_LANGUAGE_SERVER_VERSION": "0.8.4"
				"src/solidlsp/language_servers/solidity_language_server.py#DEFAULT_FORGE_VERSION":                    "1.5.1"
				"src/solidlsp/language_servers/svelte_language_server.py":                                            "hashFiles('src/solidlsp/language_servers/svelte_language_server.py')"
				"test/resources/repos/svelte/test_repo/package-lock.json":                                            "hashFiles('test/resources/repos/svelte/test_repo/package-lock.json')"
				"src/solidlsp/language_servers/terraform_ls.py#DEFAULT_TERRAFORM_LS_VERSION":                         "0.36.5"
				"src/solidlsp/language_servers/taplo_server.py#DEFAULT_TAPLO_VERSION":                                "0.10.0"
				"src/solidlsp/language_servers/typescript_language_server.py#DEFAULT_TYPESCRIPT_VERSION":             "5.9.3"
				"src/solidlsp/language_servers/vue_language_server.py":                                               "hashFiles('src/solidlsp/language_servers/vue_language_server.py')"
				"src/solidlsp/language_servers/yaml_language_server.py#DEFAULT_YAML_LANGUAGE_SERVER_VERSION":         "1.19.2"
			}
			versionToken: "v1"
		}
	}
}
