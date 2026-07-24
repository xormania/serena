package contract

// Fixture adapter: semantic cases supply concrete contract-authoritative and extracted documents.
languages: [#LanguageKey]: #Language
backends: [ID=#BackendId]: #Backend & {id: ID}
waivers: [#WaiverId]: #Waiver
extracted: #Extracted
