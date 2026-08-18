#!/usr/bin/env python3
"""Refreshes the pinned-download checksum database
(``src/solidlsp/resources/downloaded_dependency_hashes.json``) for the language servers
that verify their downloads. Run after bumping a pinned server version, then commit the
resulting changes.
"""

import argparse

from sensai.util import logging

from solidlsp.language_servers.eclipse_jdtls import EclipseJDTLS
from solidlsp.language_servers.kotlin_language_server import KotlinLanguageServer
from solidlsp.language_servers.nextflow_language_server import NextflowLanguageServer

if __name__ == "__main__":
    argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0]).parse_args()
    logging.configure()
    EclipseJDTLS.DependencyProvider.update_dep_hashes()
    NextflowLanguageServer.DependencyProvider.update_dep_hashes()
    KotlinLanguageServer.DependencyProvider.update_dep_hashes()
