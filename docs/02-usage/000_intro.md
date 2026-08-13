# Usage

Serena can be used in various ways and supports coding workflows through a project-based approach.
Its configuration is flexible and allows tailoring it to your specific needs.

In this section, you will find general usage instructions as well as concrete instructions for selected integrations.

**Getting set up**

- [Installation](010_installation.md) — installing the `serena-agent` package with uv, first-time setup via `serena init`, and how to update or uninstall.
- [Running Serena](020_running.md) — starting the MCP server (stdio or streamable HTTP), the most important CLI options, and alternative ways of running Serena (uvx, from source, Docker, Nix).
- [Connecting Your MCP Client](030_clients.md) — per-client setup instructions for Claude Code, Codex, VSCode, Copilot, Claude Desktop and many others.
- [The Serena JetBrains Plugin](025_jetbrains_plugin.md) — an IDE-powered alternative to the language-server backend with additional capabilities; connect your client first, then switch backends here.

**Daily work**

- [The Project Workflow](040_workflow.md) — creating, indexing and activating projects, and preparing a codebase for agent-based work.
- [Memories & Onboarding](045_memories.md) — the Markdown-based memory system, the onboarding process, and how to manage or disable both.

**Tuning and observing**

- [Configuration](050_configuration.md) — the configuration layers (global, project, contexts and modes), prompt templates, and per-language language-server settings.
- [The Dashboard and GUI Tool](060_dashboard.md) — the web dashboard for inspecting the running Serena instance and its logs, and the legacy GUI log viewer.
- [Logs](065_logs.md) — where logs are persisted on disk and how to adjust the log level.

**Operating safely**

- [Security Considerations](070_security.md) — Serena's trust model, trusted projects, network services, and recommended precautions.
- [Additional Usage Pointers](999_additional-usage.md) — workflow tips: plan-then-implement prompting and working with git worktrees.
