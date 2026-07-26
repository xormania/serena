package contract

// Waivers are contract-authoritative intent. This closed schema is the only escape-hatch shape; invariants later reject stale entries.
#WaiverId:    string & =~"^W-[A-Z0-9]+-[A-Z0-9][A-Z0-9-]*$"
#InvariantId: (string & =~"^C-[A-Z]+-[0-9]{3}$") | "B-REG-002"

#Waiver: {
	id:        #WaiverId
	invariant: #InvariantId
	subject:   string & !=""
	reason:    string & !=""
	reference: string
	added:     string & =~"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
}
