# Serena

**The IDE for Your Coding Agent**

Serena is an MCP server that equips the coding agent you already use — Claude Code, Codex,
Copilot, a JetBrains IDE, or any other MCP client — with the semantic code tools of an IDE.
It is not an agent itself: it provides the tools, and your agent does the work. For what that
means in practice, start with [About Serena](01-about/000_intro.md).

## Get it running

1. [Install Serena](02-usage/010_installation.md) — a `uv tool install`, then `serena init`.
2. [Connect your client](02-usage/030_clients.md) — a `serena setup` one-liner for several popular clients, manual MCP configuration for the rest.
3. [Set up your project](02-usage/040_workflow.md) — create and activate the project your agent will work on (index it if it is large).

Using a JetBrains IDE? After step 2, consider the [Serena JetBrains plugin](02-usage/025_jetbrains_plugin.md),
an IDE-powered backend with capabilities the language-server backend does not have.

## Find your path

- **Deciding whether Serena is worth it** — check the
  [supported languages](01-about/020_programming-languages.md), and see
  [what coding agents concluded](04-evaluation/000_evaluation-intro.md) when evaluating it on real codebases.
- **Curious what your agent actually gets** — the [full tool list](01-about/035_tools.md) and the
  [feature comparison](01-about/025_features.md) of the two backends.
- **Already running Serena** — get more out of it with [the project workflow](02-usage/040_workflow.md),
  [memories](02-usage/045_memories.md) and [configuration](02-usage/050_configuration.md), and read the
  [security considerations](02-usage/070_security.md) before opening repositories you do not trust.
- **On a special stack** — [setup guides](03-special-guides/000_intro.md) for C/C++, Unreal Engine, Scala,
  Godot, OCaml and Groovy, plus recipes for [ChatGPT](03-special-guides/serena_on_chatgpt.md) and for
  [embedding Serena in your own agent](03-special-guides/custom_agent.md).
- **Contributing** — Serena is developed on [GitHub](https://github.com/oraios/serena); start with
  [CONTRIBUTING.md](https://github.com/oraios/serena/blob/main/CONTRIBUTING.md).
