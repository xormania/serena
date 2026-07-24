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

#CIBatchLayout: {
	os: [#PlatformOS, ...#PlatformOS]
}

#CICacheLayout: {
	workflowName: string & !=""
	covers: [...#BackendId]
	inputs: [...#RepoRef]
	keyTokens: [#RepoRef]: string & !=""
	managed:      *false | bool
	versionToken: *"" | (string & !="")
}

#CILayout: {
	batches: {
		jvm:           #CIBatchLayout
		native:        #CIBatchLayout
		"other-langs": #CIBatchLayout
		niche:         #CIBatchLayout
		"catch-all":   #CIBatchLayout
	}
	caches: [string]: #CICacheLayout
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
	installStep: *"" | (string & !="")
	skipPolicy:  #SkipPolicy
}
