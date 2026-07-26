package contract

_platformOSes: ["linux", "macos", "windows"]

_cPlat001Pre: {
	for backendId, backend in backends
	for os in _platformOSes
	let supported = [for supportedOS in backend.platforms.supported if supportedOS == os {1}]
	let excluded = [for exclusion in backend.platforms.excluded if exclusion.os == os {1}]
	if len(supported)+len(excluded) != 1 {
		"\(backendId):\(os)": "supported and excluded platforms must form an exact three-OS partition"
	}
}

C_PLAT_001: {
	for subject, message in _cPlat001Pre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-PLAT-001" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}
