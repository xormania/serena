#!/usr/bin/env python3
"""
Autogenerates the `prompt_factory.py` module
"""

import argparse
from pathlib import Path

from sensai.util import logging

from interprompt import autogenerate_prompt_factory_module
from serena.constants import PROMPT_TEMPLATES_DIR_INTERNAL, REPO_ROOT

log = logging.getLogger(__name__)


def main():
    autogenerate_prompt_factory_module(
        prompts_dir=PROMPT_TEMPLATES_DIR_INTERNAL,
        target_module_path=str(Path(REPO_ROOT) / "src" / "serena" / "generated" / "generated_prompt_factory.py"),
    )


if __name__ == "__main__":
    argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0]).parse_args()
    logging.run_main(main)
