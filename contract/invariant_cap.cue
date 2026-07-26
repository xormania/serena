package contract

_cCap001Pre: {
	for backendId, backend in backends
	let symbols = [for memberId, symbol in extracted.lsConfig.memberSymbols if memberId == backendId {symbol}]
	let evidenced = [for symbol in symbols for evidence in extracted.conftest.verifiedImplementationSet if evidence == symbol {1}]
	if (backend.capabilities.implementationSupport == "verified" && len(evidenced) == 0) || (backend.capabilities.implementationSupport != "verified" && len(evidenced) != 0) {
		"\(backendId)": "implementation-support claim and extracted verified set disagree"
	}
	for evidence in extracted.conftest.verifiedImplementationSet
	let owners = [for memberId, symbol in extracted.lsConfig.memberSymbols if symbol == evidence {memberId}]
	if len(owners) == 0 {
		"evidence:\(evidence)": "verified implementation evidence names no registered backend"
	}
}

C_CAP_001: {
	for subject, message in _cCap001Pre {
		"\(subject)": message & false
	}
}
