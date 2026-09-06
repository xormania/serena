"""Command-line options shared by the Agno entrypoint and provider, without Agno imports."""

import argparse


class SerenaAgnoArgumentParser(argparse.ArgumentParser):
    """Parse the Agno application's mutually exclusive project-selection options."""

    def __init__(self, description: str = "Serena coding assistant") -> None:
        super().__init__(description=description)
        group = self.add_mutually_exclusive_group()
        for option in ("--project-file", "--project"):
            group.add_argument(option, help="Path to the project (or project.yml file).")
