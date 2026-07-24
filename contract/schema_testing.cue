package contract

// Test and bootstrap policy is contract-authoritative; markers, fixture directories, and artifacts remain extracted facts.
#BootstrapStep: {
	kind:    "npm-ci" | "npm-install" | "mix" | "rebar3" | "cabal-build" | "lake-build" | "sync-cmd" | "shell"
	detail?: string
	waiver?: #WaiverId
}

#Bootstrap: {
	required: bool
	steps: [#BootstrapStep, ...#BootstrapStep]
	produces: [...string & !=""]
	onFailure: {
		ci:    "fail" | "skip"
		local: "fail" | "skip"
	}
	if required {
		produces: [string & !="", ...string & !=""]
	}
}

#Testing: {
	tested: bool
	if tested {
		marker!:      string & !=""
		fixtureRepo!: string & !=""
		aliasOf?:     #BackendId
		testDir!:     string & !=""
		bootstrap?:   #Bootstrap
	}
	if !tested {
		waiver!: #WaiverId
	}
}
