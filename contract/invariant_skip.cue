package contract

// Category-1 and category-5 policies are intentional exceptions and must be backed by their exact local waiver.
_cSkip001Pre: {
	for backendId, backend in backends
	if backend.ci.skipPolicy.category == 1 || backend.ci.skipPolicy.category == 5 {
		"\(backendId)": "exceptional skip policy requires a current registered waiver"
	}
}

C_SKIP_001: {
	for subject, message in _cSkip001Pre
	let localWaiver = backends[subject].ci.skipPolicy.waiver
	let registered = [for waiverId, waiver in waivers if waiverId == localWaiver && waiver.invariant == "C-SKIP-001" && waiver.subject == subject {1}]
	if len(registered) == 0 {
		"\(subject)": message & false
	}
}

// A backend scheduled in CI may be unguarded or fail loudly when its precondition disappears, never silently skip.
_cSkip002Pre: {
	for backendId, backend in backends
	if backend.ci.expected && backend.ci.skipPolicy.category != 2 && backend.ci.skipPolicy.category != 4 {
		"\(backendId)": "CI-expected backend uses a silent-skip category"
	}
}

C_SKIP_002: {
	for subject, message in _cSkip002Pre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-SKIP-002" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}
