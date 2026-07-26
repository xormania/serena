package contract

backends: java: #DeclaredBackend & {
	id:       "java"
	language: "java"
	role:     "sole"
	class: {module: "eclipse_jdtls", name: "EclipseJDTLS"}
	status: "stable"
	matcher: extensions: [".java"]

	provisioning: {
		strategy: "composite"
		owner: {runtime: "serena", ci: "runtime"}
		cacheInputs: [
			"src/solidlsp/language_servers/eclipse_jdtls.py#DEFAULT_VSCODE_JAVA_VERSION",
			"src/solidlsp/language_servers/eclipse_jdtls.py#DEFAULT_INTELLICODE_VERSION",
			"src/solidlsp/language_servers/eclipse_jdtls.py#GRADLE_SHA256",
		]
		primary: {
			strategy:  "download"
			pin:       "1.54.0-923"
			checksums: "all-platform-assets"
			hosts: [
				"github.com",
				"release-assets.githubusercontent.com",
				"objects.githubusercontent.com",
			]
		}
		companions: [
			{
				name: "gradle"
				provisioning: {
					strategy:  "download"
					pin:       "8.14.2"
					checksums: "default-version-only"
					hosts: [
						"services.gradle.org",
						"github.com",
						"release-assets.githubusercontent.com",
						"objects.githubusercontent.com",
					]
				}
			},
			{
				name: "intellicode"
				provisioning: {
					strategy:  "download"
					pin:       "1.2.30"
					checksums: "default-version-only"
					hosts: [
						"visualstudioexptteam.gallery.vsassets.io",
						"marketplace.visualstudio.com",
						"download.visualstudio.microsoft.com",
					]
				}
			},
		]
	}

	platforms: {
		supported: ["linux", "macos", "windows"]
		excluded: []
		archNotes: "vscode-java assets cover Linux and macOS x64/ARM64 and Windows x64."
	}

	testing: {tested: true, marker: "java", fixtureRepo: "java", testDir: "java"}
	ci: _CIExpected & _BatchJVM & _CIAllOS & _SkipEverywhere
	capabilities: implementationSupport: "verified"
}
