"""Extract CI workflow facts through the pinned CUE runtime.

The repository source remains authoritative; extraction supplies agreement checks and never a competing editable truth.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, cast

from scripts.lsp_contract.cue_runtime import CueRuntime
from scripts.lsp_contract.diagnostics import ExtractionError

_MARKER_ENV = {
    "MARKERS_JVM": "jvm",
    "MARKERS_NATIVE": "native",
    "MARKERS_OTHER_LANGS": "other-langs",
    "MARKERS_NICHE": "niche",
}
_BATCH_GATE = re.compile(r"""matrix\.batch\s*==\s*['\"]([^'\"]+)['\"]""")
_BATCH_EXCLUDE_GATE = re.compile(r"""matrix\.batch\s*!=\s*['\"]([^'\"]+)['\"]""")
_OS_GATE = re.compile(r"""runner\.os\s*==\s*['\"]([^'\"]+)['\"]""")
_OS_EXCLUDE_GATE = re.compile(r"""runner\.os\s*!=\s*['\"]([^'\"]+)['\"]""")
_OS_NAMES = {
    "linux": "linux",
    "ubuntu-latest": "linux",
    "macos": "macos",
    "macos-latest": "macos",
    "windows": "windows",
    "windows-latest": "windows",
}


def _mapping(value: object, path: Path, subject: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ExtractionError(path, 1, f"{subject} must be a mapping")
    return cast(dict[str, Any], value)


def _string_list(value: object, path: Path, subject: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ExtractionError(path, 1, f"{subject} must be a literal string list")
    return [item for item in value if isinstance(item, str)]


def _lines(value: object) -> list[str]:
    if isinstance(value, str):
        return [line.strip() for line in value.splitlines() if line.strip()]
    if isinstance(value, list):
        return [str(line).strip() for line in value if str(line).strip()]
    return []


def _gates(condition: object) -> tuple[list[str], list[str], bool, bool]:
    text = condition if isinstance(condition, str) else ""

    included_batches = set(_BATCH_GATE.findall(text))
    excluded_batches = set(_BATCH_EXCLUDE_GATE.findall(text))
    batches = included_batches - excluded_batches
    if not included_batches and excluded_batches:
        batches = set(_MARKER_ENV.values()) | {"catch-all"}
        batches -= excluded_batches
    remaining_batch_expression = _BATCH_EXCLUDE_GATE.sub("", _BATCH_GATE.sub("", text))
    batch_opaque = "matrix.batch" in remaining_batch_expression

    included_os_values = {_OS_NAMES.get(value.lower()) or value.lower() for value in _OS_GATE.findall(text)}
    excluded_os_values = {_OS_NAMES.get(value.lower()) or value.lower() for value in _OS_EXCLUDE_GATE.findall(text)}
    operating_systems = included_os_values - excluded_os_values
    if not included_os_values and excluded_os_values:
        operating_systems = set(_OS_NAMES.values()) - excluded_os_values
    remaining_os_expression = _OS_EXCLUDE_GATE.sub("", _OS_GATE.sub("", text))
    known_operating_systems = set(_OS_NAMES.values())
    os_opaque = "runner.os" in remaining_os_expression or not (included_os_values | excluded_os_values).issubset(known_operating_systems)

    return sorted(batches), sorted(operating_systems), batch_opaque, os_opaque


def _needs(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return [item for item in value if isinstance(item, str)]
    return []


def extract_workflow(path: Path, runtime: CueRuntime | None = None) -> dict[str, object]:
    """Extract workflow matrix, ownership, job, step, and cache facts."""
    cue = runtime or CueRuntime()
    returncode, stdout, stderr = cue.run(["export", "--out", "json"], [path])
    if returncode:
        diagnostic = stderr.strip().splitlines()[0] if stderr.strip() else "CUE could not decode workflow"
        raise ExtractionError(path, 1, diagnostic)
    try:
        document = json.loads(stdout)
    except json.JSONDecodeError as error:
        raise ExtractionError(path, error.lineno, f"CUE returned invalid JSON: {error.msg}") from error

    root = _mapping(document, path, "workflow")
    jobs = _mapping(root.get("jobs"), path, "workflow jobs")
    cpu = _mapping(jobs.get("cpu"), path, "jobs.cpu")
    environment = _mapping(root.get("env", cpu.get("env")), path, "workflow env")
    marker_groups: dict[str, list[str]] = {}
    for variable, group in _MARKER_ENV.items():
        expression = environment.get(variable)
        if not isinstance(expression, str):
            raise ExtractionError(path, 1, f"missing literal workflow environment variable {variable}")
        marker_groups[group] = [marker.strip() for marker in expression.split(" or ") if marker.strip()]

    strategy = _mapping(cpu.get("strategy"), path, "jobs.cpu.strategy")
    matrix = _mapping(strategy.get("matrix"), path, "jobs.cpu.strategy.matrix")
    os_values = _string_list(matrix.get("os"), path, "jobs.cpu.strategy.matrix.os")
    batch_values = _string_list(matrix.get("batch"), path, "jobs.cpu.strategy.matrix.batch")
    raw_excludes = matrix.get("exclude", [])
    if not isinstance(raw_excludes, list) or not all(isinstance(item, dict) for item in raw_excludes):
        raise ExtractionError(path, 1, "jobs.cpu.strategy.matrix.exclude must be a literal mapping list")
    excludes = [
        {
            "os": _OS_NAMES.get(str(item.get("os", "")).lower(), str(item.get("os", "")).lower()),
            "batch": str(item.get("batch", "")),
        }
        for item in raw_excludes
    ]

    extracted_jobs: list[dict[str, object]] = []
    steps: list[dict[str, object]] = []
    caches: list[dict[str, object]] = []
    for job_name, raw_job in jobs.items():
        job = _mapping(raw_job, path, f"jobs.{job_name}")
        timeout = job.get("timeout-minutes")
        extracted_jobs.append(
            {
                "name": job_name,
                "timeoutMinutes": timeout if isinstance(timeout, int) else None,
                "needs": _needs(job.get("needs")),
            }
        )
        raw_steps = job.get("steps", [])
        if not isinstance(raw_steps, list):
            raise ExtractionError(path, 1, f"jobs.{job_name}.steps must be a list")
        for position, raw_step in enumerate(raw_steps):
            step = _mapping(raw_step, path, f"jobs.{job_name}.steps[{position}]")
            batches, operating_systems, batch_gate_opaque, os_gate_opaque = _gates(step.get("if"))
            extracted_step: dict[str, object] = {
                "job": job_name,
                "name": str(step.get("name", step.get("uses", f"step-{position}"))),
                "if": str(step.get("if", "")),
                "uses": str(step.get("uses", "")),
                "run": str(step.get("run", "")),
                "batchGate": batches,
                "osGate": operating_systems,
                "batchGateOpaque": batch_gate_opaque,
                "osGateOpaque": os_gate_opaque,
            }
            steps.append(extracted_step)

            action = step.get("uses")
            if isinstance(action, str) and (action.startswith(("actions/cache@", "julia-actions/cache@"))):
                settings = step.get("with", {})
                if settings is None:
                    settings = {}
                settings = _mapping(settings, path, f"cache step {job_name}/{position} with")
                key = settings.get("key")
                if not isinstance(key, str):
                    key = f"action-managed:{action}"
                path_value = settings.get("path", "")
                if not isinstance(path_value, str):
                    path_value = str(path_value)
                caches.append(
                    {
                        "job": job_name,
                        "name": str(step.get("name", action)),
                        "path": path_value,
                        "key": key,
                        "restoreKeys": _lines(settings.get("restore-keys")),
                        "batchGate": batches,
                        "osGate": operating_systems,
                        "batchGateOpaque": batch_gate_opaque,
                        "osGateOpaque": os_gate_opaque,
                    }
                )

    return {
        "markerGroups": marker_groups,
        "matrix": {
            "os": [_OS_NAMES.get(value.lower(), value.lower()) for value in os_values],
            "batches": batch_values,
            "exclude": excludes,
        },
        "jobs": extracted_jobs,
        "steps": steps,
        "caches": caches,
    }
