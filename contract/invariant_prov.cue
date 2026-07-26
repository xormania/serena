package contract

import "strings"

// Provisioning leaves retain companion identity so composite downloads are checked independently.
_baseProvisioningLeaves: {
	for backendId, backend in backends {
		"\(backendId)": {
			if backend.provisioning.strategy != "composite" {
				root: {
					provisioning: backend.provisioning
					evidenceId:   ""
					excludedEvidenceIds: []
				}
			}
			if backend.provisioning.strategy == "composite" {
				primary: {
					provisioning: backend.provisioning.primary
					evidenceId:   ""
					excludedEvidenceIds: [for companion in backend.provisioning.companions {
						strings.ToLower(companion.name)
					}]
				}
				for index, companion in backend.provisioning.companions {
					"companion-\(index)": {
						provisioning: companion.provisioning
						evidenceId:   strings.ToLower(companion.name)
						excludedEvidenceIds: []
					}
				}
			}
		}
	}
}

_allProvisioningLeaves: {
	for backendId, backend in backends {
		"\(backendId)": _baseProvisioningLeaves[backendId] & {
			for field, overrides in backend.platforms
			if field == "provisioningOverrides"
			for os, override in overrides {
				"override-\(os)": {
					provisioning: override
					evidenceId:   ""
					excludedEvidenceIds: []
				}
			}
		}
	}
}

_serverRecords: {
	for backendId, backend in backends {
		"\(backendId)": [for module, record in extracted.servers if module == backend.class.module {
			record
		}]
	}
}

#PlatformEvidenceMatch: {
	candidate: string | null
	targetOS:  #PlatformOS
	matches:   bool
	if candidate == null {
		matches: true
	}
	if candidate != null {
		_id:     strings.ToLower(candidate)
		matches: _id == "any" || _id == "platform-agnostic" ||
			(targetOS == "linux" && (strings.HasPrefix(_id, "linux") || strings.Contains(_id, ".linux_"))) ||
			(targetOS == "macos" && (strings.HasPrefix(_id, "osx") || strings.HasPrefix(_id, "darwin") || strings.HasPrefix(_id, "mac") || strings.Contains(_id, ".osx_"))) ||
			(targetOS == "windows" && (strings.HasPrefix(_id, "win") || strings.HasPrefix(_id, "windows") || strings.Contains(_id, ".win_")))
	}
}

#DownloadEvidenceState: {
	records: [...#ExtractedServerModule]
	evidenceId: string
	excludedEvidenceIds: [...string]
	targetOS:     #PlatformOS
	_requestedOS: targetOS

	_runtimeEvidence: [
		for record in records
		for dependency in record.runtimeDeps
		let urls = [for field, value in dependency if field == "url" && value != null && value != "" {1}]
		let matchingIds = [for field, value in dependency if field == "id" if strings.ToLower(value) == evidenceId {1}]
		let excludedIds = [for field, value in dependency if field == "id" for excludedId in excludedEvidenceIds if strings.ToLower(value) == excludedId {1}]
		if len(urls) > 0 && ((evidenceId != "" && len(matchingIds) > 0) || (evidenceId == "" && len(excludedIds) == 0)) {
			dependency
		},
	]
	_jsonEvidence: [
		for record in records
		for field, document in record
		if field == "runtimeDependencyJson"
		for dependency in document.runtimeDependencies
		let excludedIds = [for excludedId in excludedEvidenceIds if strings.ToLower(dependency.id) == excludedId {1}]
		if (evidenceId != "" && strings.ToLower(dependency.id) == evidenceId) || (evidenceId == "" && len(excludedIds) == 0) {
			dependency
		},
	]
	_matchingRuntime: [
		for dependency in _runtimeEvidence
		let platformIds = [for field, value in dependency if field == "platformId" {value}]
		let matches = [for platformId in platformIds if (#PlatformEvidenceMatch & {candidate: platformId, targetOS: _requestedOS}).matches {1}]
		if len(platformIds) == 0 || len(matches) > 0 {1},
	]
	_matchingJSON: [
		for dependency in _jsonEvidence
		if (#PlatformEvidenceMatch & {candidate: dependency.platformId, targetOS: _requestedOS}).matches {1},
	]
	_unknownRuntime: [for dependency in _runtimeEvidence if dependency.platformIdOpaque {1}]
	_opaqueCalls: [for record in records for call in record.opaqueProvisioningCalls {call}]

	covered: len(_matchingRuntime)+len(_matchingJSON) > 0
	opaque:  !covered && (len(_unknownRuntime) > 0 || (len(_runtimeEvidence)+len(_jsonEvidence) == 0 && len(_opaqueCalls) > 0))
	missing: !covered && !opaque
}

_cProv002Pre: {
	for backendId, backend in backends
	let sourceBuildLeaves = [for _, leaf in _allProvisioningLeaves[backendId] if leaf.provisioning.strategy == "source-build" {1}]
	let commands = [for record in _serverRecords[backendId] for command in record.cargoCommands {command}]
	let unlockedCommands = [for command in commands
		let locked = [for argument in command if argument == "--locked" {1}]
		if len(locked) == 0 {1}]
	if (len(sourceBuildLeaves) > 0 && (len(commands) == 0 || len(unlockedCommands) > 0)) || (len(sourceBuildLeaves) == 0 && len(commands) > 0) {
		"\(backendId)": "source-build declarations and extracted cargo install commands must agree and use --locked"
	}
}

_cProv003MissingPre: {
	for backendId, backend in backends
	let downloadLeaves = [for _, leaf in _allProvisioningLeaves[backendId] if leaf.provisioning.strategy == "download" || leaf.provisioning.strategy == "nuget-download" {1}]
	let runtimeURLs = [for record in _serverRecords[backendId] for dependency in record.runtimeDeps
		let urls = [for field, value in dependency if field == "url" && value != null && value != "" {1}]
		if len(urls) > 0 {dependency}]
	let missingRuntimeHashes = [for dependency in runtimeURLs
		let hashes = [for field, value in dependency if field == "sha256" && value != null && value != "" {1}]
		if len(hashes) == 0 {1}]
	let jsonDependencies = [for record in _serverRecords[backendId] for field, document in record if field == "runtimeDependencyJson" for dependency in document.runtimeDependencies {dependency}]
	let missingJSONHashes = [for dependency in jsonDependencies
		let hashes = [for field, value in dependency if field == "integrity" && value != "" {1}]
		if len(hashes) == 0 {1}]
	let opaqueCalls = [for record in _serverRecords[backendId] for call in record.opaqueProvisioningCalls {call}]
	if len(missingRuntimeHashes)+len(missingJSONHashes) > 0 ||
		(len(downloadLeaves) > 0 && len(runtimeURLs)+len(jsonDependencies)+len(opaqueCalls) == 0) ||
		(len(downloadLeaves) == 0 && len(opaqueCalls) > 0) {
		"\(backendId)": "default-version downloads require checksum evidence and an aligned download declaration"
	}
}

_cProv003OpaquePre: {
	for backendId, _ in backends
	let downloadLeaves = [for _, leaf in _allProvisioningLeaves[backendId] if leaf.provisioning.strategy == "download" || leaf.provisioning.strategy == "nuget-download" {1}]
	let runtimeURLs = [for record in _serverRecords[backendId] for dependency in record.runtimeDeps
		let urls = [for field, value in dependency if field == "url" && value != null && value != "" {1}]
		if len(urls) > 0 {dependency}]
	let opaqueRuntimeHashes = [for dependency in runtimeURLs if dependency.sha256Opaque {1}]
	let jsonDependencies = [for record in _serverRecords[backendId] for field, document in record if field == "runtimeDependencyJson" for dependency in document.runtimeDependencies {dependency}]
	let opaqueCalls = [for record in _serverRecords[backendId] for call in record.opaqueProvisioningCalls {call}]
	if len(downloadLeaves) > 0 && (len(opaqueRuntimeHashes) > 0 || (len(runtimeURLs)+len(jsonDependencies) == 0 && len(opaqueCalls) > 0)) {
		"\(backendId):checksum-opaque": "default-version checksum verification is opaque to structural extraction"
	}
}

_cProv003Pre: _cProv003MissingPre
_cProv003Pre: _cProv003OpaquePre

_cProv004Pre: {
	for backendId, _ in backends
	let unpinned = [for _, leaf in _allProvisioningLeaves[backendId] if leaf.provisioning.strategy == "package-manager" if leaf.provisioning.pin == "UNPINNED" {1}]
	if len(unpinned) > 0 {
		"\(backendId)": "package-manager provisioning must be pinned or carry a current matching waiver"
	}
}

_cProv005MissingPre: {
	for backendId, backend in backends
	for os in backend.platforms.supported
	let overrides = [for field, values in backend.platforms if field == "provisioningOverrides" for overrideOS, override in values if overrideOS == os {override}]
	let baseMissing = [for _, leaf in _baseProvisioningLeaves[backendId]
		if leaf.provisioning.strategy == "download" || leaf.provisioning.strategy == "nuget-download"
		let state = #DownloadEvidenceState & {records: _serverRecords[backendId], evidenceId: leaf.evidenceId, excludedEvidenceIds: leaf.excludedEvidenceIds, targetOS: os}
		if state.missing {1}]
	let overrideMissing = [for override in overrides
		if override.strategy == "download" || override.strategy == "nuget-download"
		let state = #DownloadEvidenceState & {records: _serverRecords[backendId], evidenceId: "", excludedEvidenceIds: [], targetOS: os}
		if state.missing {1}]
	if (len(overrides) == 0 && len(baseMissing) > 0) || (len(overrides) > 0 && len(overrideMissing) > 0) {
		"\(backendId):\(os)": "supported platform has no provable provisioning path"
	}
}

_cProv005OpaquePre: {
	for backendId, backend in backends
	let opaquePlatforms = [for os in backend.platforms.supported
		let overrides = [for field, values in backend.platforms if field == "provisioningOverrides" for overrideOS, override in values if overrideOS == os {override}]
		let baseOpaque = [for _, leaf in _baseProvisioningLeaves[backendId]
			if leaf.provisioning.strategy == "download" || leaf.provisioning.strategy == "nuget-download"
			let state = #DownloadEvidenceState & {records: _serverRecords[backendId], evidenceId: leaf.evidenceId, excludedEvidenceIds: leaf.excludedEvidenceIds, targetOS: os}
			if state.opaque {1}]
		let overrideOpaque = [for override in overrides
			if override.strategy == "download" || override.strategy == "nuget-download"
			let state = #DownloadEvidenceState & {records: _serverRecords[backendId], evidenceId: "", excludedEvidenceIds: [], targetOS: os}
			if state.opaque {1}]
		if (len(overrides) == 0 && len(baseOpaque) > 0) || (len(overrides) > 0 && len(overrideOpaque) > 0) {os}]
	if len(opaquePlatforms) > 0 {
		"\(backendId):coverage-opaque": "platform coverage is declaration-backed because structured extraction is opaque"
	}
}

_cProv005ReversePre: {
	for backendId, backend in backends
	for exclusion in backend.platforms.excluded
	let os = exclusion.os
	let overrides = [for field, values in backend.platforms if field == "provisioningOverrides" for overrideOS, _ in values if overrideOS == os {1}]
	let runtimeMatches = [for record in _serverRecords[backendId] for dependency in record.runtimeDeps
		let platformIds = [for field, value in dependency if field == "platformId" && value != null {value}]
		for platformId in platformIds
		let normalized = strings.ToLower(platformId)
		if normalized != "any" && normalized != "platform-agnostic" && (#PlatformEvidenceMatch & {candidate: platformId, targetOS: os}).matches {1}]
	// A static dependency JSON may retain dormant artifacts that runtime guards reject (for example OmniSharp macOS).
	// Only active extracted RuntimeDependency records and explicit overrides prove a path outside declared support.
	if len(overrides)+len(runtimeMatches) > 0 {
		"\(backendId):\(os)": "extracted provisioning path targets an explicitly excluded platform"
	}
}

_cProv005Pre: _cProv005MissingPre
_cProv005Pre: _cProv005OpaquePre
_cProv005Pre: _cProv005ReversePre

C_PROV_002: {
	for subject, message in _cProv002Pre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-PROV-002" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}

C_PROV_003: {
	for subject, message in _cProv003Pre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-PROV-003" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}

C_PROV_004: {
	for subject, message in _cProv004Pre
	let localWaivers = [for _, leaf in _allProvisioningLeaves[subject] for field, waiverId in leaf.provisioning if field == "waiver" {waiverId}]
	let matching = [for waiverId, waiver in waivers for localWaiverId in localWaivers if waiverId == localWaiverId && waiver.invariant == "C-PROV-004" && waiver.subject == subject {1}]
	if len(matching) == 0 {
		"\(subject)": message & false
	}
}

C_PROV_005: {
	for subject, message in _cProv005Pre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-PROV-005" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}
