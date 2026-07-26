package contract

// Declaration defaults cover only genuinely universal facts; every backend file owns the integration-specific intent.
#DeclaredBackend: #Backend & {
	platforms: {
		supported: *["linux", "macos", "windows"] | [#PlatformOS, ...#PlatformOS]
		excluded: *[] | [...{os: #PlatformOS, reason: string & !=""}]
	}
	capabilities: implementationSupport: *"none" | "verified" | "advertised"
}

_CIExpected: {expected: true}
_BatchJVM: {batch: "jvm"}
_BatchNative: {batch: "native"}
_BatchOther: {batch: "other-langs"}
_BatchNiche: {batch: "niche"}
_BatchCatchAll: {batch: "catch-all"}
_CIAllOS: {os: ["linux", "macos", "windows"]}
_CINonWindows: {os: ["linux", "macos"]}
_CILinux: {os: ["linux"]}
_CIMacOS: {os: ["macos"]}
_SkipEverywhere: {skipPolicy: category: 4}
