package contract

// CI and skip policy is declared intent; workflow matrices, marker groups, gates, and timeouts remain code-authoritative.
#Batch: "jvm" | "native" | "other-langs" | "niche" | "catch-all"

#SkipPolicy: {
	category: 1 | 2 | 3 | 4 | 5
	if category == 2 {
		loudOn!: {
			os: [#PlatformOS, ...#PlatformOS]
			ci: true
		}
	}
	if category == 1 || category == 5 {
		waiver!: #WaiverId
		reason!: string & !=""
	}
	toolProbe?: string & !=""
}

#CI: {
	expected: bool
	if expected {
		batch!: #Batch
		os!: [#PlatformOS, ...#PlatformOS]
	}
	if !expected {
		waiver!: #WaiverId
	}
	skipPolicy: #SkipPolicy
}
