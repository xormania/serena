package contract

backends: csharp_omnisharp: #DeclaredBackend & {
	id:       "csharp_omnisharp"
	language: "csharp"
	role:     "alternate"
	class: {module: "omnisharp", name: "OmniSharp"}
	status: "experimental"
	matcher: sharedArmWith: "csharp"

	provisioning: {
		strategy: "composite"
		owner: {runtime: "serena", ci: "none"}
		cacheInputs: [
			"src/solidlsp/language_servers/omnisharp.py#DEFAULT_OMNISHARP_VERSION",
			"src/solidlsp/language_servers/omnisharp.py#DEFAULT_RAZOR_OMNISHARP_VERSION",
		]
		primary: {
			strategy:  "download"
			pin:       "1.39.10"
			checksums: "all-platform-assets"
			hosts: [
				"roslynomnisharp.blob.core.windows.net",
				"download.visualstudio.microsoft.com",
			]
		}
		companions: [{
			name: "RazorOmnisharp"
			provisioning: {
				strategy:  "download"
				pin:       "7.0.0-preview.23363.1"
				checksums: "all-platform-assets"
				hosts: [
					"roslynomnisharp.blob.core.windows.net",
					"download.visualstudio.microsoft.com",
				]
			}
		}]
	}

	platforms: {
		supported: ["linux", "windows"]
		excluded: [{
			os:     "macos"
			reason: "OmniSharp._setup_runtime_dependencies permits only linux-x64 and win-x64."
		}]
		archNotes: "Runtime provisioning is restricted to x64."
	}

	testing: {tested: false, waiver: "W-TEST-OMNISHARP"}
	ci: {expected: false, waiver: "W-TEST-OMNISHARP", skipPolicy: {category: 4}}
}
