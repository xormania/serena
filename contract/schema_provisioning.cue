package contract

// Provisioning intent is contract-authoritative; pins, commands, hashes, and probes remain code-authoritative and are joined by invariants.
#RepoRef: string & !=""

#ProvisioningOwner: {
	runtime!: "serena" | "user" | "project"
	ci!:      "runtime" | "workflow-step" | "image" | "none"
}

#ProvisioningLeafStrategy: "download" | "npm" | "uvx" | "nuget-download" | "dotnet-tool" | "source-build" | "path" | "bundled" | "tcp" | "package-manager"
#ProvisioningStrategy:     #ProvisioningLeafStrategy | "composite"

#PackagePin: {
	name: string & !=""
	pin:  string & !=""
}

#ProvisioningLeaf: {
	strategy: #ProvisioningLeafStrategy
	if strategy == "download" || strategy == "nuget-download" {
		pin!:       string & !=""
		checksums!: "all-platform-assets" | "default-version-only"
		hosts!: [string, ...string]
	}
	if strategy == "source-build" {
		pin!: string & !=""
		lockDiscipline!: {tool: "cargo", flag: "--locked"}
	}
	if strategy == "path" {
		executables!: [string, ...string]
	}
	if strategy == "uvx" || strategy == "dotnet-tool" {
		package!: string & !=""
		pin!:     string & !=""
	}
	if strategy == "npm" {
		packages!: [#PackagePin, ...#PackagePin]
	}
	if strategy == "package-manager" {
		manager!: string & !=""
		pin:      *"UNPINNED" | (string & !="")
		if pin == "UNPINNED" {
			waiver!: #WaiverId
		}
	}
	if strategy == "tcp" {
		host!: string & !=""
		port!: int & >0 & <=65535
	}
	if strategy == "bundled" {
		enginePin!: #RepoRef
	}
}

#CompanionRef: {
	name:         string & !=""
	provisioning: #ProvisioningLeaf
}

#Provisioning: {
	strategy: #ProvisioningStrategy
	owner:    #ProvisioningOwner
	cacheInputs: [...#RepoRef]
	if strategy == "download" || strategy == "nuget-download" {
		pin!:       string & !=""
		checksums!: "all-platform-assets" | "default-version-only"
		hosts!: [string, ...string]
	}
	if strategy == "source-build" {
		pin!: string & !=""
		lockDiscipline!: {tool: "cargo", flag: "--locked"}
	}
	if strategy == "path" {
		executables!: [string, ...string]
	}
	if strategy == "uvx" || strategy == "dotnet-tool" {
		package!: string & !=""
		pin!:     string & !=""
	}
	if strategy == "npm" {
		packages!: [#PackagePin, ...#PackagePin]
	}
	if strategy == "package-manager" {
		manager!: string & !=""
		pin:      *"UNPINNED" | (string & !="")
		if pin == "UNPINNED" {
			waiver!: #WaiverId
		}
	}
	if strategy == "tcp" {
		host!: string & !=""
		port!: int & >0 & <=65535
	}
	if strategy == "bundled" {
		enginePin!: #RepoRef
	}
	if strategy == "composite" {
		primary!: #ProvisioningLeaf
		companions!: [#CompanionRef, ...#CompanionRef]
	}
}
