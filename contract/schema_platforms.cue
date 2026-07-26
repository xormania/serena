package contract

// Platform support is contract-authoritative intent; extracted dependency coverage and CI guards later prove agreement.
#PlatformOS: "linux" | "macos" | "windows"

#Platforms: {
	supported: [#PlatformOS, ...#PlatformOS]
	excluded: [...{
		os:     #PlatformOS
		reason: string & !=""
	}]
	archNotes?: string
	provisioningOverrides?: {
		[OS=#PlatformOS]: #ProvisioningLeaf
	}
}
