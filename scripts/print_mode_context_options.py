#!/usr/bin/env python3
"""Prints an overview of every registered Serena mode and context — the values accepted by
``--mode`` and ``--context`` — with each one's description.
"""

import argparse

from serena.config.context_mode import SerenaAgentContext, SerenaAgentMode

if __name__ == "__main__":
    argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0]).parse_args()
    print("---------- Available modes: ----------")
    for mode_name in SerenaAgentMode.list_registered_mode_names():
        mode = SerenaAgentMode.load(mode_name)
        mode.print_overview()
        print("\n")
    print("---------- Available contexts: ----------")
    for context_name in SerenaAgentContext.list_registered_context_names():
        context = SerenaAgentContext.load(context_name)
        context.print_overview()
        print("\n")
