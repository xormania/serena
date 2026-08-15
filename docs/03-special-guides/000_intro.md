# Special Guides

This section contains special guides for certain topics that require more in-depth explanations.

**Language & engine setup** — for the language-server backend; pick the guide matching your stack:

- [C/C++](cpp_setup.md) — preparing `compile_commands.json` for clangd (the default) or ccls; not needed when using the JetBrains backend.
- [Unreal Engine](unreal_engine_setup_guide_for_serena.md) — obtaining a `compile_commands.json` for UE5 projects via UnrealBuildTool (Windows-centric).
- [Scala](scala_setup_guide_for_serena.md) — Metals bootstrap and build import, monorepo build-root detection, and stale-lock handling.
- [GDScript (Godot)](godot_gdscript_setup_guide_for_serena.md) — connecting to the LSP built into a running Godot editor; the editor must stay open while Serena is in use.
- [OCaml](ocaml_setup_guide_for_serena.md) — installing ocamllsp via opam and the version requirements for cross-file references.
- [Groovy](groovy_setup_guide_for_serena.md) — configuring a user-supplied Groovy language server; support is currently in an intermediate state.

**Integrations beyond the standard MCP clients**

- [Serena on ChatGPT](serena_on_chatgpt.md) — exposing a local Serena instance to ChatGPT via MCPO and a Cloudflare tunnel; mind the security notes.
- [Custom Agents with Serena](custom_agent.md) — embedding Serena's tools directly in your own agent framework, with a working Agno-based example.
