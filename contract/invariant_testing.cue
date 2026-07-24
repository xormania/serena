package contract

_cTest001Pre: {
	for id, backend in backends
	if backend.testing.tested
	let matches = [for marker in extracted.pyproject.markers if marker.name == backend.testing.marker {1}]
	if len(matches) == 0 {
		"\(id)": "tested backend marker is absent from pyproject markers"
	}
}

_cTest002Pre: {
	for id, backend in backends
	if backend.testing.tested
	let repos = [for repo in extracted.filesystem.repoDirs if repo == backend.testing.fixtureRepo {1}]
	let aliasFields = [for field, _ in backend.testing if field == "aliasOf" {1}]
	let aliases = [for field, target in backend.testing if field == "aliasOf" for targetId, targetBackend in backends if targetId == target && targetBackend.testing.tested {1}]
	if len(repos) == 0 || (len(aliasFields) != 0 && len(aliases) == 0) {
		"\(id)": "tested backend fixture repository is missing or its alias target is invalid"
	}
}

_cTest003Pre: {
	for id, backend in backends
	if backend.testing.tested
	let matches = [for directory in extracted.filesystem.testDirs if directory == backend.testing.testDir {1}]
	if len(matches) == 0 {
		"\(id)": "tested backend test directory is absent"
	}
}

_cTest004Pre: {
	for marker in extracted.pyproject.markers
	let owners = [for _, backend in backends if backend.testing.tested for field, markerName in backend.testing if field == "marker" && markerName == marker.name {1}]
	if marker.name != "slow" && marker.name != "snapshot" && len(owners) == 0 {
		"\(marker.name)": "pyproject language marker has no backend owner"
	}
}

_cTest005Pre: {
	for duplicate in extracted.conftest.rawDuplicateKeys
	let normalizedIds = [for id, symbol in extracted.lsConfig.memberSymbols if symbol == duplicate[0] {id}]
	if len(normalizedIds) == 0 {
		"\(duplicate[0])": "conftest alias or marker dictionary contains a duplicate key"
	}
	for duplicate in extracted.conftest.rawDuplicateKeys
	for id, symbol in extracted.lsConfig.memberSymbols
	if symbol == duplicate[0] {
		"\(id)": "conftest alias or marker dictionary contains a duplicate key"
	}
	for id, backend in backends
	if backend.role == "alternate" && backend.testing.tested
	let symbol = extracted.lsConfig.memberSymbols[id]
	let targetSymbol = extracted.lsConfig.memberSymbols[backend.testing.aliasOf]
	let aliases = [for aliasId, target in extracted.conftest.aliases if (aliasId == id || aliasId == symbol) && (target == backend.testing.aliasOf || target == targetSymbol) {1}]
	let markers = [for markerId, markerNames in extracted.conftest.markerDict if markerId == id || markerId == symbol for markerName in markerNames if markerName == backend.testing.marker {1}]
	if len(aliases) == 0 || len(markers) == 0 {
		"\(id)": "tested alternate lacks a matching alias or marker-dictionary entry"
	}
}

_cTest006Pre: {
	for id, backend in backends
	if !backend.testing.tested {
		"\(id)": "untested backend requires a matching registered C-TEST-006 waiver"
	}
}

C_TEST_001: {
	for subject, message in _cTest001Pre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-TEST-001" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}

C_TEST_002: {
	for subject, message in _cTest002Pre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-TEST-002" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}

C_TEST_003: {
	for subject, message in _cTest003Pre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-TEST-003" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}

C_TEST_004: {
	for subject, message in _cTest004Pre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-TEST-004" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}

C_TEST_005: {
	for subject, message in _cTest005Pre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-TEST-005" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}

C_TEST_006: {
	for subject, message in _cTest006Pre
	let waived = [for waiverId, waiver in waivers if waiver.invariant == "C-TEST-006" && waiver.subject == subject && waiverId == backends[subject].testing.waiver {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}
