package contract

// Registration facts are joined against the live extracted repository snapshot.
extracted: #Extracted

_cReg001Pre: {
	for member in extracted.lsConfig.members
	if len([for id, _ in backends if id == member {id}]) == 0 {
		"\(member)": "enum member has no backend declaration"
	}
	for id, _ in backends
	if len([for member in extracted.lsConfig.members if member == id {member}]) == 0 {
		"\(id)": "backend declaration has no enum member"
	}
}

_cReg002Pre: {
	for id, backend in backends
	let matches = [for dispatchId, arm in extracted.lsConfig.dispatch if dispatchId == id && arm.class == backend.class.name && (arm.module == backend.class.module || arm.module == "solidlsp.language_servers.\(backend.class.module)") {1}]
	if len(matches) == 0 {
		"\(id)": "dispatch arm is missing or does not match the declared module and class"
	}
}

_cReg003Pre: {
	for id, backend in backends
	let own = [for matcherId, _ in extracted.lsConfig.matchers if matcherId == id {1}]
	let shared = [for field, target in backend.matcher if field == "sharedArmWith" for matcherId, _ in extracted.lsConfig.matchers if matcherId == target {1}]
	if len(own)+len(shared) == 0 {
		"\(id)": "no own or declared shared matcher arm is reachable"
	}
}

_cReg004Pre: {
	for id, backend in backends
	let membership = [for member in extracted.lsConfig.experimentalSet if member == id {1}]
	if (backend.status == "experimental" && len(membership) == 0) || (backend.status == "stable" && len(membership) != 0) {
		"\(id)": "declared status disagrees with is_experimental membership"
	}
}

_cReg005Pre: {
	for id, backend in backends
	let defaults = [for _, candidate in backends if candidate.language == backend.language && candidate.role == "default" {1}]
	if backend.role == "alternate" && len(defaults) != 1 {
		"\(id)": "alternate backend mints a language or does not reference an existing default"
	}
}

_cReg006Pre: {
	for languageId, language in languages
	let candidates = [for id, backend in backends if backend.language == languageId {{id: id, role: backend.role}}]
	let defaults = [for id, backend in backends if backend.language == languageId && backend.role == "default" {id}]
	let soles = [for id, backend in backends if backend.language == languageId && backend.role == "sole" {id}]
	let designated = [for id, backend in backends if id == language.defaultBackend && backend.language == languageId && backend.role != "alternate" {id}]
	if len(candidates) == 0 || (len(candidates) == 1 && (len(soles) != 1 || len(defaults) != 0 || len(designated) != 1)) || (len(candidates) > 1 && (len(defaults) != 1 || len(soles) != 0 || len(designated) != 1)) {
		"\(languageId)": "language must have exactly one coherent default, or one sole backend"
	}
}

_cReg007Missing: [
	for member in extracted.lsConfig.members
	if len([for templateId in extracted.docs.templateIds if templateId == member {1}]) == 0 {
		member
	},
]

_cReg007Pre: {
	if len(_cReg007Missing) != 0 {
		"project.template.yml": "template backend id list is missing one or more enum members"
	}
}

C_REG_001: {
	for subject, message in _cReg001Pre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-REG-001" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}

C_REG_002: {
	for subject, message in _cReg002Pre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-REG-002" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}

C_REG_003: {
	for subject, message in _cReg003Pre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-REG-003" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}

C_REG_004: {
	for subject, message in _cReg004Pre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-REG-004" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}

C_REG_005: {
	for subject, message in _cReg005Pre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-REG-005" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}

C_REG_006: {
	for subject, message in _cReg006Pre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-REG-006" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}

C_REG_007: {
	for subject, message in _cReg007Pre
	let waived = [for _, waiver in waivers if waiver.invariant == "C-REG-007" && waiver.subject == subject {1}]
	if len(waived) == 0 {
		"\(subject)": message & false
	}
}
