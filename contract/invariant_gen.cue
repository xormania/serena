package contract

_cGen001Pre: {
	if !extracted.freshness.registrationCurrent {
		"contract/REGISTRATION.md": "generated registration table differs from deterministic regeneration"
	}
	if !extracted.freshness.templateCurrent {
		"src/serena/resources/project.template.yml": "generated template language list differs from deterministic regeneration"
	}
}

C_GEN_001: {
	for subject, message in _cGen001Pre {
		"\(subject)": message & false
	}
}
