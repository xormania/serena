package contract

// Every entry must suppress a current pre-waiver violation; C-WAIVE-001 rejects stale register entries.
waivers: [#WaiverId]: #Waiver
waivers: {
	"W-TEST-GDSCRIPT": {id: "W-TEST-GDSCRIPT", invariant: "C-TEST-006", subject: "gdscript", reason: "Godot owns the TCP server lifecycle and no hermetic fixture exists.", reference: "proj/cue/plan.md#2.9", added: "2026-07-24"}
	"W-TEST-JEDI": {id: "W-TEST-JEDI", invariant: "C-TEST-006", subject: "python_jedi", reason: "The alternate has no dedicated collected test surface.", reference: "proj/cue/plan.md#2.9", added: "2026-07-24"}
	"W-TEST-SOLARGRAPH": {id: "W-TEST-SOLARGRAPH", invariant: "C-TEST-006", subject: "ruby_solargraph", reason: "The alternate has no dedicated collected test surface.", reference: "proj/cue/plan.md#2.9", added: "2026-07-24"}
	"W-TEST-VTS": {id: "W-TEST-VTS", invariant: "C-TEST-006", subject: "typescript_vts", reason: "The alternate has no dedicated collected test surface.", reference: "proj/cue/plan.md#2.9", added: "2026-07-24"}
	"W-TEST-OMNISHARP": {id: "W-TEST-OMNISHARP", invariant: "C-TEST-006", subject: "csharp_omnisharp", reason: "The alternate has no dedicated collected test surface.", reference: "proj/cue/plan.md#2.9", added: "2026-07-24"}
	"W-TEST-DUP-ALIAS": {id: "W-TEST-DUP-ALIAS", invariant: "C-TEST-005", subject: "python_ty", reason: "The live alias dictionary contains a duplicate PYTHON_TY literal.", reference: "test/conftest.py#_LANGUAGE_REPO_ALIASES", added: "2026-07-24"}
	"W-REG-TEMPLATE-STALE": {id: "W-REG-TEMPLATE-STALE", invariant: "C-REG-007", subject: "project.template.yml", reason: "The generated template list remains stale until P9 regeneration.", reference: "proj/cue/plan.md#P9", added: "2026-07-24"}
}
