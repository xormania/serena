# scripts/

Everything here runs the same way, from the repository root:

```bash
uv run python scripts/<dir>/<name>.py
```

| where | what |
|:--|:--|
| `demos/` | see a tool run — direct tool execution against real repositories, no MCP client and no LLM involved |
| `dev/` | working on Serena itself — the dev-environment doctor, live client-setup probes, printers, profiling, prompt-factory codegen, dependency-hash updates |
| `release/` | cutting releases — the version bump and the news build; contributors never need these |
| top level | `mcp_server.py` and `agno_agent.py` stay here deliberately: external MCP configurations and guides launch them by these exact paths, so moving them would break callers outside this repository |

The contributing docs carry the per-script map; this file only names the buckets.
