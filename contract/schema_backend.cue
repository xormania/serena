package contract

// Backend identity and intent are declared once here; every code-authored registration surface is checked by agreement invariants.
#LanguageKey: string & =~"^[a-z0-9_]+$"
#BackendId:   string & =~"^[a-z0-9_]+$"

#Language: {
	displayName:    string & !=""
	defaultBackend: #BackendId
	docLabel:       string & !=""
}

#Matcher: {
	{
		extensions: [string, ...string]
	} | {
		sharedArmWith: #BackendId
	}
	caseSensitive: *true | bool
}

#Backend: {
	id:       #BackendId
	language: #LanguageKey
	role:     "default" | "alternate" | "sole"
	class: {
		module: string & !=""
		name:   string & !=""
	}
	status:       "stable" | "experimental"
	matcher:      #Matcher
	provisioning: #Provisioning
	platforms:    #Platforms
	testing:      #Testing
	ci:           #CI
	capabilities: #Capabilities
}
