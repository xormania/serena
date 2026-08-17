#!/usr/bin/env python3
"""Serena as a toolkit inside another agent framework: builds an Agno AgentOS app around
Serena's tools and serves it. The model is chosen by editing this file (examples inline);
the custom-agent guide in the documentation walks through the setup.

    uv run python scripts/agno_agent.py
"""

import argparse

# consume --help BEFORE the optional agno imports: the extras may not be installed, and with
# them installed the app would otherwise build and serve instead of printing usage. Guarded
# on __main__ because serve() re-imports this module by name (``agno_agent:app``), and the
# server's argv is not ours to parse.
if __name__ == "__main__":
    argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0]).parse_args()

from agno.models.anthropic.claude import Claude
from agno.models.google.gemini import Gemini
from agno.os import AgentOS
from sensai.util import logging
from sensai.util.helper import mark_used

from serena.agno import SerenaAgnoAgentProvider

mark_used(Gemini, Claude)

# initialize logging
if __name__ == "__main__":
    logging.configure(level=logging.INFO)

# Define the model to use (see Agno documentation for supported models; these are just examples)
# model = Claude(id="claude-3-7-sonnet-20250219")
model = Gemini(id="gemini-2.5-pro")

# Create the Serena agent using the existing provider
serena_agent = SerenaAgnoAgentProvider.get_agent(model)

# Create AgentOS app with the Serena agent
agent_os = AgentOS(
    description="Serena coding assistant powered by AgentOS",
    id="serena-agentos",
    agents=[serena_agent],
)

app = agent_os.get_app()

if __name__ == "__main__":
    # Start the AgentOS server
    agent_os.serve(app="agno_agent:app", reload=False)
