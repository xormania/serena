package contract

// CI placement joins declared intent to normalized workflow facts.
_cCi001Pre: {
	for backendId, backend in backends
	if backend.testing.tested {
		if !backend.ci.expected {
			"\(backendId)": "tested backend is excluded from every CI execution"
		}
		if backend.ci.expected {
			if backend.ci.batch != "catch-all" {
				let matchingGroups = [for group, markers in extracted.workflow.markerGroups for marker in markers if group == backend.ci.batch && marker == backend.testing.marker {1}]
				if len(matchingGroups) == 0 {
					"\(backendId)": "declared CI batch does not contain the backend marker"
				}
			}
		}
	}
}

C_CI_001: {
	for subject, message in _cCi001Pre {
		if backends[subject].ci.expected {
			"\(subject)": message & false
		}
		if !backends[subject].ci.expected {
			let localWaiver = backends[subject].ci.waiver
			let waived = [for waiverId, waiver in waivers if waiverId == localWaiver && waiver.id == waiverId && waiver.invariant == "C-CI-001" && waiver.subject == subject {1}]
			if len(waived) == 0 {
				"\(subject)": message & false
			}
		}
	}
}
_cCi002Pre: {
	for declaredBatch, _ in ciLayout.batches {
		let matches = [for extractedBatch in extracted.workflow.matrix.batches if extractedBatch == declaredBatch {1}]
		if len(matches) != 1 {
			"\(declaredBatch)": "declared batch must occur exactly once in the extracted matrix"
		}
	}
	for extractedBatch in extracted.workflow.matrix.batches {
		let matches = [for declaredBatch, _ in ciLayout.batches if declaredBatch == extractedBatch {1}]
		if len(matches) != 1 {
			"\(extractedBatch)": "extracted matrix batch is outside the declared closed batch set"
		}
	}
}

C_CI_002: {
	for subject, message in _cCi002Pre {
		"\(subject)": message & false
	}
}
_cCi003Pre: {
	for _, markers in extracted.workflow.markerGroups
	for marker in markers {
		let memberships = [
			for _, candidateMarkers in extracted.workflow.markerGroups
			let occurrences = [for candidate in candidateMarkers if candidate == marker {1}]
			if len(occurrences) > 0 {1}
		]
		if len(memberships) > 1 {
			"\(marker)": "marker occurs in more than one named CI group"
		}
	}
}

C_CI_003: {
	for subject, message in _cCi003Pre {
		"\(subject)": message & false
	}
}
_cCi004Pre: {
	for backendId, backend in backends
	if backend.ci.expected {
		if backend.ci.batch == "catch-all" {
			let memberships = [for _, markers in extracted.workflow.markerGroups for marker in markers if marker == backend.testing.marker {1}]
			if len(memberships) != 0 {
				"\(backendId)": "catch-all backend marker occurs in a named CI group"
			}
		}
	}
}

C_CI_004: {
	for subject, message in _cCi004Pre {
		"\(subject)": message & false
	}
}
_cCi005Pre: {
	for backendId, backend in backends
	if backend.ci.expected {
		if backend.provisioning.owner.ci == "none" {
			"\(backendId)": "CI-expected backend has no CI provisioning owner"
		}
		if backend.provisioning.owner.ci == "workflow-step" {
			let exactSteps = [for step in extracted.workflow.steps if step.name == backend.ci.installStep {step}]
			let coveringSteps = [
				for step in exactSteps
				let matchingBatch = [for gatedBatch in step.batchGate if gatedBatch == backend.ci.batch {1}]
				let uncoveredOS = [
					for declaredOS in backend.ci.os
					let matchingOS = [for gatedOS in step.osGate if gatedOS == declaredOS {1}]
					if len(step.osGate) > 0 && len(matchingOS) == 0 {declaredOS}
				]
				if step.job == "cpu" && !step.batchGateOpaque && !step.osGateOpaque && (len(step.batchGate) == 0 || len(matchingBatch) > 0) && len(uncoveredOS) == 0 {1}
			]
			if backend.ci.installStep == "" || len(exactSteps) != 1 || len(coveringSteps) != 1 {
				"\(backendId)": "workflow-step owner lacks one exact non-opaque step covering the declared batch and every declared OS"
			}
		}
	}
}

C_CI_005: {
	for subject, message in _cCi005Pre {
		"\(subject)": message & false
	}
}
_cCi006Pre: {
	for batch, declaredLayout in ciLayout.batches
	for os in _platformOSes {
		let declared = [for declaredOS in declaredLayout.os if declaredOS == os {1}]
		let effective = [
			for matrixBatch in extracted.workflow.matrix.batches
			if matrixBatch == batch
			for matrixOS in extracted.workflow.matrix.os
			if matrixOS == os
			let exclusions = [for exclusion in extracted.workflow.matrix.exclude if exclusion.batch == batch && exclusion.os == os {1}]
			if len(exclusions) == 0 {1}
		]
		if (len(declared) > 0) != (len(effective) > 0) {
			"layout:\(batch):\(os)": "declared batch OS set differs from the effective extracted matrix"
		}
	}
	for backendId, backend in backends
	if backend.ci.expected
	for os in backend.ci.os {
		let inLayout = [for declaredOS in ciLayout.batches[backend.ci.batch].os if declaredOS == os {1}]
		let supported = [for supportedOS in backend.platforms.supported if supportedOS == os {1}]
		if len(inLayout) == 0 || len(supported) == 0 {
			"\(backendId):\(os)": "declared CI OS is outside the effective batch or backend platform support"
		}
	}
}

C_CI_006: {
	for subject, message in _cCi006Pre {
		"\(subject)": message & false
	}
}
_cCi007Pre: {
	for job in extracted.workflow.jobs {
		if job.timeoutMinutes == null {
			"\(job.name)": "workflow job must declare a positive timeout-minutes"
		}
		if job.timeoutMinutes != null {
			if job.timeoutMinutes <= 0 {
				"\(job.name)": "workflow job must declare a positive timeout-minutes"
			}
		}
	}
}

C_CI_007: {
	for subject, message in _cCi007Pre {
		"\(subject)": message & false
	}
}
