package contract

import "strings"

_stableDocLabels: {
	for _, backend in backends
	if backend.status == "stable" && backend.role != "alternate" {
		"\(languages[backend.language].docLabel)": true
	}
}

_cDocReadmeMissing: [
	for label, _ in _stableDocLabels
	let matches = [for actual in extracted.docs.readmeLabels if strings.Contains(strings.ToLower(actual), strings.ToLower(label)) {1}]
	if len(matches) == 0 {label},
]

_cDocPageMissing: [
	for label, _ in _stableDocLabels
	let matches = [for actual in extracted.docs.docsLabels if strings.Contains(strings.ToLower(actual), strings.ToLower(label)) {1}]
	if len(matches) == 0 {label},
]

_cDoc001Pre: {
	if len(_cDocReadmeMissing) != 0 {
		"README.md": "missing stable language labels: \(strings.Join(_cDocReadmeMissing, ", "))"
	}
	if len(_cDocPageMissing) != 0 {
		"docs/01-about/020_programming-languages.md": "missing stable language labels: \(strings.Join(_cDocPageMissing, ", "))"
	}
}

_cDoc001Post: {
	for subject, message in _cDoc001Pre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-DOC-001" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message
	}
}

C_DOC_001: {
	for subject, message in _cDoc001Post {
		"\(subject)": message & false
	}
}
