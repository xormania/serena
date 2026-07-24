"""CUE declaration exports consumed by the semantic conformance suite."""

import json
from functools import cache
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast

from scripts.lsp_contract.cue_runtime import CueRuntime
from scripts.lsp_contract.extract.assemble import write_extracted

_REPOSITORY_ROOT = Path(__file__).parents[2]


def _export_mapping(expression: str) -> dict[str, dict[str, object]]:
    with TemporaryDirectory(prefix="serena-contract-conformance-") as directory:
        extracted_path = write_extracted(_REPOSITORY_ROOT, Path(directory) / "extracted.json")
        returncode, stdout, stderr = CueRuntime().run(["export", "./contract", str(extracted_path), "-e", expression, "--out", "json"])
    if returncode:
        raise RuntimeError(f"CUE declaration export failed for {expression}:\n{stderr}")
    document = json.loads(stdout)
    if not isinstance(document, dict) or not all(isinstance(key, str) and isinstance(value, dict) for key, value in document.items()):
        raise TypeError(f"CUE declaration export {expression} was not an object map")
    return cast(dict[str, dict[str, object]], document)


@cache
def export_backends() -> dict[str, dict[str, object]]:
    """Export the concrete backend declaration map once per test process."""
    return _export_mapping("backends")


@cache
def export_waived_subjects(invariant_id: str) -> set[str]:
    """Return subjects with registered waivers for an invariant."""
    waivers = _export_mapping("waivers")
    return {str(waiver["subject"]) for waiver in waivers.values() if waiver["invariant"] == invariant_id}
