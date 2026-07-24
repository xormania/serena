package contract

// Extracted facts are code-authoritative snapshots. This closed schema normalizes their shape without becoming an editable source of truth.
#DispatchArm: {
	module: string & !=""
	class:  string & !=""
}

#ExtractedMatcherArm: {
	{
		literalExtensions: [...string]
		caseSensitive: bool
	} | {
		computedShape: true
	}
}

#ExtractedLSConfig: {
	members: [...string]
	memberSymbols: [string]: string
	dispatch: [string]:      #DispatchArm
	matchers: [string]:      #ExtractedMatcherArm
	experimentalSet: [...string]
	nonProgrammingSet: [...string]
	priorityZeroSet: [...string]
}

#ExtractedConftest: {
	aliases: [string]: string
	rawDuplicateKeys: [...[string, int, int]]
	markerDict: [string]: [...string]
	backendLists: [string]: [...string]
	verifiedImplementationSet: [...string]
}

#ExtractedPyproject: {
	markers: [...{
		name:        string & !=""
		description: string
	}]
	devPins: [string]: string
}

#WorkflowMatrix: {
	os: [...#PlatformOS]
	batches: [...#Batch]
	exclude: [...{
		os:    #PlatformOS
		batch: #Batch
	}]
}

#WorkflowJob: {
	name:           string & !=""
	timeoutMinutes: int | null
	needs: [...string]
}

#WorkflowStep: {
	job:  string & !=""
	name: string & !=""
	"if": string
	uses: string
	run:  string
	batchGate: [...#Batch]
	osGate: [...#PlatformOS]
}

#WorkflowCache: {
	job:  string & !=""
	name: string & !=""
	path: string
	key:  string & !=""
	restoreKeys: [...string]
}

#ExtractedWorkflow: {
	markerGroups: [string]: [...string]
	matrix: #WorkflowMatrix
	jobs: [...#WorkflowJob]
	steps: [...#WorkflowStep]
	caches: [...#WorkflowCache]
}

#ExtractedRuntimeDependency: {
	id?:              string
	platformId?:      string | null
	platformIdOpaque: *false | bool
	url?:             string | null
	sha256?:          string | null
	sha256Opaque:     *false | bool
	allowedHosts?: [...string] | string | null
	archiveType?: string | null
	binaryName?:  string | null
	command?: string | [...string] | null
	packageName?:    string | null
	packageVersion?: string | null
	extractPath?:    string | null
	extract_path?:   string | null
	description?:    string | null
	opaque:          bool
}

#ExtractedUvxPin: {
	package: string
	version: string
	opaque?: bool
}

#OmnisharpRuntimeDependency: {
	id:          string
	description: string
	url:         string
	installPath: string
	platforms: [...string]
	architectures: [...string]
	installTestPath?: string
	platformId:       string
	isFramework?:     bool
	integrity?:       string
	dotnet_version?:  string
	binaryName?:      string
	binaries?: [...string]
	dll_path?: string
}

#OmnisharpDocument: {
	"_description": string
	runtimeDependencies: [...#OmnisharpRuntimeDependency]
}

#JSONValue: null | bool | number | string | [...#JSONValue] | {[string]: #JSONValue}

#ExtractedServerModule: {
	runtimeDeps: [...#ExtractedRuntimeDependency]
	opaqueProvisioningCalls: *[] | [...string]
	uvxPins: [...#ExtractedUvxPin]
	cargoCommands: [...[...string]]
	pathProbes: [...string]
	pins: [string]: #JSONValue
	runtimeDependencyJson?: #OmnisharpDocument
}

#ExtractedFilesystem: {
	repoDirs: [...string]
	testDirs: [...string]
	bootstrapConftests: [...string]
}

#ExtractedDocs: {
	readmeLabels: [...string]
	docsLabels: [...string]
	templateIds: [...#BackendId]
}

#ExtractedFreshness: {
	registrationCurrent: bool
	templateCurrent:     bool
}

#Extracted: {
	lsConfig:  #ExtractedLSConfig
	conftest:  #ExtractedConftest
	pyproject: #ExtractedPyproject
	workflow:  #ExtractedWorkflow
	servers: [string]: #ExtractedServerModule
	filesystem: #ExtractedFilesystem
	docs:       #ExtractedDocs
	freshness?: #ExtractedFreshness
}

#ExtractedDocument: {extracted: #Extracted}
