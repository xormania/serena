package contract

import "strings"

// Cache identity is code-authoritative and cannot be waived as key-coverage debt.
_cCache001IdentityHard: {
	for cacheId, cache in ciLayout.caches {
		let matches = [for extractedCache in extracted.workflow.caches if extractedCache.name == cache.workflowName {1}]
		if len(matches) != 1 {
			"identity:\(cacheId)": "cache declaration must resolve to exactly one extracted cache"
		}
	}
	for extractedCache in extracted.workflow.caches {
		let declarations = [for _, cache in ciLayout.caches if cache.workflowName == extractedCache.name {1}]
		if len(declarations) != 1 {
			"identity:extracted:\(extractedCache.name)": "extracted cache must have exactly one declaration"
		}
	}
}

// Backend coverage and declaration shape remain hard even when a cache key has known debt.
_cCache001JoinHard: {
	for cacheId, cache in ciLayout.caches {
		let missingCoveredBackends = [
			for coveredId in cache.covers
			let matches = [for backendId, _ in backends if backendId == coveredId {1}]
			if len(matches) != 1 {coveredId}
		]
		let coveredBackends = [for coveredId in cache.covers for backendId, backend in backends if backendId == coveredId {backend}]
		let nonExpectedCovered = [for backend in coveredBackends if !backend.ci.expected {backend.id}]
		let missingCoveredInputs = [
			for backend in coveredBackends
			for backendInput in backend.provisioning.cacheInputs
			let matches = [for cacheInput in cache.inputs if cacheInput == backendInput {1}]
			if len(matches) != 1 {backendInput}
		]
		let orphanInputs = [
			for cacheInput in cache.inputs
			if len(cache.covers) > 0
			let matches = [for backend in coveredBackends for backendInput in backend.provisioning.cacheInputs if backendInput == cacheInput {1}]
			if len(matches) != 1 {cacheInput}
		]
		let missingTokens = [
			for cacheInput in cache.inputs
			if !cache.managed
			let matches = [for tokenInput, _ in cache.keyTokens if tokenInput == cacheInput {1}]
			if len(matches) != 1 {cacheInput}
		]
		let orphanTokens = [
			for tokenInput, _ in cache.keyTokens
			if !cache.managed
			let matches = [for cacheInput in cache.inputs if cacheInput == tokenInput {1}]
			if len(matches) != 1 {tokenInput}
		]
		if len(missingCoveredBackends)+len(nonExpectedCovered)+len(missingCoveredInputs)+len(orphanInputs)+len(missingTokens)+len(orphanTokens) > 0 {
			"join:\(cacheId)": "cache coverage, covered backend inputs, and key-token declarations must agree exactly"
		}
	}
}

// Every declared key token must have one code-authoritative source witness.
_cCache001SourceHard: {
	for cacheId, cache in ciLayout.caches {
		let malformedRefs = [
			for cacheInput in cache.inputs
			if !cache.managed && strings.Contains(cacheInput, "#")
			let parts = strings.Split(cacheInput, "#")
			if len(parts) != 2 {cacheInput}
		]
		let serverSourceProblems = [
			for cacheInput in cache.inputs
			if !cache.managed && strings.HasPrefix(cacheInput, "src/solidlsp/language_servers/") && strings.Contains(cacheInput, "#")
			let parts = strings.Split(cacheInput, "#")
			if len(parts) == 2
			for tokenInput, token in cache.keyTokens
			if tokenInput == cacheInput
			let moduleName = strings.TrimSuffix(strings.TrimPrefix(parts[0], "src/solidlsp/language_servers/"), ".py")
			let matches = [
				for serverId, server in extracted.servers
				if serverId == moduleName
				for pinName, pinValue in server.pins
				if pinName == parts[1] && pinValue == token {1}
			]
			if len(matches) != 1 {cacheInput}
		]
		let workflowSourceProblems = [
			for cacheInput in cache.inputs
			if !cache.managed && strings.HasPrefix(cacheInput, ".github/workflows/") && strings.Contains(cacheInput, "#")
			let parts = strings.Split(cacheInput, "#")
			if len(parts) == 2
			for tokenInput, token in cache.keyTokens
			if tokenInput == cacheInput
			let namedSteps = [for step in extracted.workflow.steps if step.name == parts[1] {step}]
			let matches = [for step in namedSteps if strings.Contains(step.run, token) {1}]
			if len(matches) != 1 {cacheInput}
		]
		let fileSourceProblems = [
			for cacheInput in cache.inputs
			if !cache.managed && !strings.Contains(cacheInput, "#")
			for tokenInput, token in cache.keyTokens
			if tokenInput == cacheInput && token != "hashFiles('\(cacheInput)')" {cacheInput}
		]
		let unsupportedRefs = [
			for cacheInput in cache.inputs
			if !cache.managed && strings.Contains(cacheInput, "#") && !strings.HasPrefix(cacheInput, "src/solidlsp/language_servers/") && !strings.HasPrefix(cacheInput, ".github/workflows/") {cacheInput}
		]
		if len(malformedRefs)+len(serverSourceProblems)+len(workflowSourceProblems)+len(fileSourceProblems)+len(unsupportedRefs) > 0 {
			"source:\(cacheId)": "cache key tokens must resolve exactly to extracted source pins, workflow steps, or file hashes"
		}
	}
}

_cCache001ManagedHard: {
	for cacheId, cache in ciLayout.caches {
		let matches = [for extractedCache in extracted.workflow.caches if extractedCache.name == cache.workflowName {extractedCache}]
		let mismatches = [
			for extractedCache in matches
			if (cache.managed && !strings.HasPrefix(extractedCache.key, "action-managed:")) || (!cache.managed && strings.HasPrefix(extractedCache.key, "action-managed:")) {1}
		]
		if len(mismatches) > 0 {
			"managed:\(cacheId)": "managed cache declaration disagrees with the extracted action-managed shape"
		}
	}
}

_cCache001GateHard: {
	for cacheId, cache in ciLayout.caches {
		let matches = [for extractedCache in extracted.workflow.caches if extractedCache.name == cache.workflowName {extractedCache}]
		let coveredBackends = [for coveredId in cache.covers for backendId, backend in backends if backendId == coveredId {backend}]
		let mismatches = [
			for backend in coveredBackends
			if backend.ci.expected
			for extractedCache in matches
			let batchMatches = [for gatedBatch in extractedCache.batchGate if gatedBatch == backend.ci.batch {1}]
			let uncoveredOS = [
				for declaredOS in backend.ci.os
				let osMatches = [for gatedOS in extractedCache.osGate if gatedOS == declaredOS {1}]
				if len(extractedCache.osGate) > 0 && len(osMatches) == 0 {declaredOS}
			]
			if extractedCache.job != "cpu" || extractedCache.batchGateOpaque || extractedCache.osGateOpaque || (len(extractedCache.batchGate) > 0 && len(batchMatches) == 0) || len(uncoveredOS) > 0 {backend.id}
		]
		if len(mismatches) > 0 {
			"gate:\(cacheId)": "cache execution gates do not cover every declared backend batch and OS"
		}
	}
}

_cCache001HardPre: _cCache001IdentityHard & _cCache001JoinHard & _cCache001SourceHard & _cCache001ManagedHard & _cCache001GateHard

// Only an authoritative provisioning token's absence from the actual key is waiverable.
_cCache001Pre: {
	for cacheId, cache in ciLayout.caches {
		let extractedMatches = [for extractedCache in extracted.workflow.caches if extractedCache.name == cache.workflowName {extractedCache}]
		let uncoveredTokens = [
			for cacheInput in cache.inputs
			if !cache.managed
			for tokenInput, token in cache.keyTokens
			if tokenInput == cacheInput
			for extractedCache in extractedMatches
			if !strings.Contains(extractedCache.key, token) {cacheInput}
		]
		if len(uncoveredTokens) > 0 {
			"\(cacheId)": "resolved provisioning input token is absent from the cache key"
		}
	}
}

C_CACHE_001: {
	for subject, message in _cCache001HardPre {
		"\(subject)": message & false
	}
	for subject, message in _cCache001Pre {
		let hard = [for hardSubject, _ in _cCache001HardPre if hardSubject == subject {1}]
		if len(hard) == 0 {
			let waived = [for _, waiver in waivers if waiver.invariant == "C-CACHE-001" && waiver.subject == subject {1}]
			if len(waived) == 0 {
				"\(subject)": message & false
			}
		}
	}
}
// Declared-token presence and primary-key coverage are hard requirements.
_cCache002HardPre: {
	for cacheId, cache in ciLayout.caches {
		let extractedMatches = [for extractedCache in extracted.workflow.caches if extractedCache.name == cache.workflowName {extractedCache}]
		let missingDeclaredTokens = [
			for extractedCache in extractedMatches
			if len(extractedCache.restoreKeys) > 0 && cache.versionToken == "" {1}
		]
		let keyProblems = [
			for extractedCache in extractedMatches
			if cache.versionToken != "" && !strings.Contains(extractedCache.key, cache.versionToken) {1}
		]
		if len(missingDeclaredTokens)+len(keyProblems) > 0 {
			"key:\(cacheId)": "restore prefixes require a declared version token, and the primary key must contain it"
		}
	}
}

// Only a restore prefix that omits an otherwise valid primary-key token is waiverable.
_cCache002Pre: {
	for cacheId, cache in ciLayout.caches {
		let extractedMatches = [for extractedCache in extracted.workflow.caches if extractedCache.name == cache.workflowName {extractedCache}]
		let restoreProblems = [
			for extractedCache in extractedMatches
			for restoreKey in extractedCache.restoreKeys
			if cache.versionToken != "" && !strings.Contains(restoreKey, cache.versionToken) {restoreKey}
		]
		if len(restoreProblems) > 0 {
			"\(cacheId)": "declared version token is absent from a restore prefix"
		}
	}
}

C_CACHE_002: {
	for subject, message in _cCache002HardPre {
		"\(subject)": message & false
	}
	for subject, message in _cCache002Pre {
		let hard = [for hardSubject, _ in _cCache002HardPre if hardSubject == subject {1}]
		if len(hard) == 0 {
			let waived = [for _, waiver in waivers if waiver.invariant == "C-CACHE-002" && waiver.subject == subject {1}]
			if len(waived) == 0 {
				"\(subject)": message & false
			}
		}
	}
}
