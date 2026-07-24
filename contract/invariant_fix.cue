package contract

_cFix001ShellPre: {
	for backendId, backend in backends
	for field, bootstrap in backend.testing
	if field == "bootstrap"
	let shellSteps = [for step in bootstrap.steps if step.kind == "shell" {1}]
	if len(shellSteps) != 0 {
		"\(backendId)": "opaque shell bootstrap step requires its exact registered waiver"
	}
}

_cFix001EvidencePre: {
	for backendId, backend in backends
	for field, bootstrap in backend.testing
	if field == "bootstrap"
	let fixtureEvidence = [for directory in extracted.filesystem.bootstrapConftests if directory == backend.testing.testDir {1}]
	let workflowEvidence = [for step in bootstrap.steps for stepField, detail in step if stepField == "detail" for workflowStep in extracted.workflow.steps if workflowStep.name == detail {1}]
	if len(fixtureEvidence)+len(workflowEvidence) == 0 {
		"\(backendId)": "declared bootstrap has no extracted fixture or workflow evidence"
	}
	for directory in extracted.filesystem.bootstrapConftests
	let declarations = [for candidateId, candidate in backends for candidateField, _ in candidate.testing if candidateField == "bootstrap" if candidate.testing.testDir == directory {candidateId}]
	if len(declarations) == 0 {
		"\(directory)": "extracted bootstrap fixture has no declaration"
	}
}

_cFix001Pre: _cFix001ShellPre & _cFix001EvidencePre

C_FIX_001: {
	for subject, message in _cFix001ShellPre
	let shellSteps = [for step in backends[subject].testing.bootstrap.steps if step.kind == "shell" {1}]
	let waivedSteps = [for step in backends[subject].testing.bootstrap.steps if step.kind == "shell" for localField, localWaiver in step if localField == "waiver" for waiverId, waiver in waivers if localWaiver == waiverId && waiver.invariant == "C-FIX-001" && waiver.subject == subject {1}]
	if len(waivedSteps) != len(shellSteps) {
		"\(subject)": message & false
	}
	for subject, message in _cFix001EvidencePre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-FIX-001" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}

_cFix002Pre: {
	for backendId, backend in backends
	for field, bootstrap in backend.testing
	if field == "bootstrap"
	if bootstrap.required && bootstrap.onFailure.ci != "fail" {
		"\(backendId)": "required bootstrap may not mask CI failure"
	}
}

C_FIX_002: {
	for subject, message in _cFix002Pre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-FIX-002" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}
