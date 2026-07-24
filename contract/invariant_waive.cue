package contract

// Staleness is checked against pre-waiver sets, so a waiver cannot make its own justification disappear.
_preWaiverViolations: {
	"C-REG-001":   _cReg001Pre
	"C-REG-002":   _cReg002Pre
	"C-REG-003":   _cReg003Pre
	"C-REG-004":   _cReg004Pre
	"C-REG-005":   _cReg005Pre
	"C-REG-006":   _cReg006Pre
	"C-REG-007":   _cReg007Pre
	"C-PROV-002":  _cProv002Pre
	"C-PROV-003":  _cProv003Pre
	"C-PROV-004":  _cProv004Pre
	"C-PROV-005":  _cProv005Pre
	"C-PLAT-001":  _cPlat001Pre
	"C-CI-001":    _cCi001Pre
	"C-CACHE-001": _cCache001Pre
	"C-CACHE-002": _cCache002Pre
	"C-DOC-001":   _cDoc001Pre
	"C-TEST-001":  _cTest001Pre
	"C-TEST-002":  _cTest002Pre
	"C-TEST-003":  _cTest003Pre
	"C-TEST-004":  _cTest004Pre
	"C-TEST-005":  _cTest005Pre
	"C-TEST-006":  _cTest006Pre
	"C-SKIP-001":  _cSkip001Pre
	"C-SKIP-002":  _cSkip002Pre
	"C-FIX-001":   _cFix001Pre
	"C-FIX-002":   _cFix002Pre
}

_behavioralInvariants: {"B-REG-002": true}

_cWaive001Pre: {
	for waiverId, waiver in waivers
	let current = [for invariantId, subjects in _preWaiverViolations for subject, _ in subjects if invariantId == waiver.invariant && subject == waiver.subject {1}]
	let behavioral = [for invariantId, _ in _behavioralInvariants if invariantId == waiver.invariant {1}]
	if waiver.id != waiverId || waiver.reference == "" || (len(current) == 0 && len(behavioral) == 0) {
		"\(waiverId)": "waiver id, invariant, subject, or reference is unknown or stale"
	}
}

C_WAIVE_001: {
	for subject, message in _cWaive001Pre {
		"\(subject)": message & false
	}
}
