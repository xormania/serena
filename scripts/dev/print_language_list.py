#!/usr/bin/env python3
"""
Prints the list of supported languages, for use in the project.yml template
"""

import argparse

from solidlsp.ls_config import LanguageServerId

if __name__ == "__main__":
    argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0]).parse_args()
    lang_strings = sorted([l.value for l in LanguageServerId])
    max_len = max(len(s) for s in lang_strings)
    fmt = f"%-{max_len + 2}s"
    for i, l in enumerate(lang_strings):
        if i % 5 == 0:
            print("\n# ", end="")
        print("  " + fmt % l, end="")
