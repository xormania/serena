"""Command-line interface for the language-integration contract."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path, PurePosixPath, PureWindowsPath
from tempfile import TemporaryDirectory

from scripts.lsp_contract.cue_runtime import CueRuntime, install
from scripts.lsp_contract.diagnostics import (
    DIAGNOSTICS,
    ExtractionError,
    render_cue_diagnostics,
    render_extractor_drift_summary,
    render_github_failure_summary,
    render_github_success_summary,
)
from scripts.lsp_contract.extract.assemble import write_extracted
from scripts.lsp_contract.render import write_registration, write_template_list


def _build_parser() -> argparse.ArgumentParser:
    """Build the contract command-line parser."""
    parser = argparse.ArgumentParser(prog="python -m scripts.lsp_contract")
    parser.add_argument(
        "command",
        choices=(
            "install-cue",
            "extract",
            "vet-schema",
            "validate",
            "explain",
            "render-registration",
            "render-template-list",
        ),
    )
    parser.add_argument("argument", nargs="?")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--github-summary", action="store_true")
    return parser


def _vet_schema(root: Path) -> int:
    """Vet and format-check the unified offline CUE schema package."""
    schema_files = sorted((root / "contract").glob("schema_*.cue"))
    if not schema_files:
        print(f"{root / 'contract'}: no schema_*.cue files found", file=sys.stderr)
        return 2

    runtime = CueRuntime()
    for arguments in (["vet", "-c=false"], ["fmt", "--check"]):
        returncode, stdout, stderr = runtime.run(arguments, schema_files)
        if stdout:
            print(stdout, end="")
        if returncode:
            print(stderr, file=sys.stderr, end="" if stderr.endswith("\n") else "\n")
            return 1
    return 0


def _write_github_summary(content: str, *, requested: bool) -> bool:
    """Append a summary when requested and GitHub provides a destination."""
    if not requested:
        return True
    summary_target = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_target:
        return True
    try:
        with Path(summary_target).open("a", encoding="utf-8") as summary_file:
            summary_file.write(content)
    except OSError as error:
        print(f"contract: could not write GITHUB_STEP_SUMMARY: {error}", file=sys.stderr)
        return False
    return True


def _explain(diagnostic_id: str | None) -> int:
    """Print the registered meaning and fix for one invariant id."""
    if diagnostic_id is None or diagnostic_id not in DIAGNOSTICS:
        label = diagnostic_id or "<missing>"
        print(f"unknown invariant: {label}", file=sys.stderr)
        return 2
    diagnostic = DIAGNOSTICS[diagnostic_id]
    print(f"{diagnostic_id}: {diagnostic.meaning}")
    print(f"fix: {diagnostic.fix}")
    print(f"details: contract/INVARIANTS.md#{diagnostic_id.lower()}")
    return 0


def _documentation_url() -> str:
    """Return an Actions-safe invariant-document URL with a local fallback."""
    server = os.environ.get("GITHUB_SERVER_URL")
    repository = os.environ.get("GITHUB_REPOSITORY")
    revision = os.environ.get("GITHUB_SHA")
    if server and repository and revision:
        return f"{server.rstrip('/')}/{repository}/blob/{revision}/contract/INVARIANTS.md"
    return "contract/INVARIANTS.md"


@contextmanager
def _repository_local_cue_input(root: Path, input_path: Path) -> Iterator[Path]:
    """Stage a generated CUE input under the repository when it lives elsewhere."""
    resolved_root = root.resolve()
    resolved_input = input_path.resolve()
    if resolved_input.is_relative_to(resolved_root):
        yield resolved_input
        return

    with TemporaryDirectory(prefix="serena-contract-input-", dir=resolved_root) as directory:
        staged_input = Path(directory) / resolved_input.name
        shutil.copyfile(resolved_input, staged_input)
        yield staged_input


class _GitInventoryError(RuntimeError):
    """Raised when Git cannot establish the repository's tracked evidence."""


def _tracked_repository_paths(root: Path) -> frozenset[str]:
    """Return repository-relative paths present in the Git index."""
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--cached", "--"],
            check=False,
            capture_output=True,
        )
    except OSError as error:
        raise _GitInventoryError(f"Git tracked-file inventory could not start: {error}") from error
    if completed.returncode:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        if not detail:
            detail = f"git ls-files exited with status {completed.returncode}"
        raise _GitInventoryError(f"Git tracked-file inventory failed: {detail}")

    try:
        return frozenset(path.decode("utf-8") for path in completed.stdout.split(b"\0") if path)
    except UnicodeDecodeError as error:
        raise _GitInventoryError("Git tracked-file inventory contains a non-UTF-8 path") from error


def _waiver_reference_path(reference: object) -> str | None:
    """Return a normalized repository path before an optional opaque fragment."""
    if not isinstance(reference, str):
        return None

    path_component = reference.split("#", 1)[0]
    windows_path = PureWindowsPath(path_component)
    repository_path = PurePosixPath(path_component.replace("\\", "/"))
    if (
        not path_component
        or windows_path.drive
        or windows_path.is_absolute()
        or repository_path.is_absolute()
        or ".." in repository_path.parts
    ):
        return None

    normalized = repository_path.as_posix()
    return None if normalized in {"", "."} else normalized


def _waiver_reference_diagnostics(root: Path, waivers: Mapping[str, Mapping[str, object]]) -> str:
    """Render C-WAIVE-001 diagnostics for references unavailable to reviewers."""
    tracked_paths = _tracked_repository_paths(root)
    violations: list[str] = []
    for waiver_id, waiver in sorted(waivers.items()):
        reference = waiver.get("reference") if isinstance(waiver, Mapping) else None
        reference_path = _waiver_reference_path(reference)
        if reference_path is not None:
            directory_prefix = f"{reference_path.rstrip('/')}/"
            if reference_path in tracked_paths or any(path.startswith(directory_prefix) for path in tracked_paths):
                continue

        rendered_reference = reference if isinstance(reference, str) else repr(reference)
        violations.append(
            f"C_WAIVE_001.{json.dumps(waiver_id)}: waiver reference {json.dumps(rendered_reference)} "
            "does not name a Git-tracked file or directory with tracked descendants"
        )

    return "\n".join(violations)


def _validate(
    root: Path,
    output: Path | None = None,
    *,
    github_summary: bool = False,
) -> int:
    """Extract repository facts, vet schemas, and evaluate the full CUE contract."""
    root = root.resolve()
    try:
        extracted_path = write_extracted(root, output)
    except ExtractionError as error:
        print(error, file=sys.stderr)
        drift_summary = render_extractor_drift_summary(error)
        print(drift_summary, file=sys.stderr, end="")
        _write_github_summary(drift_summary, requested=github_summary)
        return 2

    schema_result = _vet_schema(root)
    if schema_result:
        _write_github_summary(
            "## Language/CI contract schema validation failed\n\nInspect the raw job log for CUE schema diagnostics.\n",
            requested=github_summary,
        )
        return schema_result

    runtime = CueRuntime()
    with _repository_local_cue_input(root, extracted_path) as cue_input:
        returncode, stdout, stderr = runtime.run(["export", str(root / "contract"), str(cue_input), "--out", "json"])
    if returncode:
        rendered = render_cue_diagnostics(stderr)
        if rendered:
            print(rendered, file=sys.stderr)
        failure_summary = render_github_failure_summary(
            stderr,
            documentation_url=_documentation_url(),
        )
        print(failure_summary, file=sys.stderr, end="")
        _write_github_summary(failure_summary, requested=github_summary)
        return 1

    try:
        document = json.loads(stdout)
        waivers = document["waivers"]
        if not isinstance(waivers, dict):
            raise TypeError("waivers must be an object")
        waiver_count = len(waivers)
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        print(f"contract: invalid CUE export output: {error}", file=sys.stderr)
        _write_github_summary(
            "## Language/CI contract output error\n\nThe CUE export did not contain a valid waiver register.\n",
            requested=github_summary,
        )
        return 2

    try:
        reference_diagnostics = _waiver_reference_diagnostics(root, waivers)
    except _GitInventoryError as error:
        inventory_diagnostic = f"C_WAIVE_001.global: {error}"
        rendered = render_cue_diagnostics(inventory_diagnostic)
        print(rendered, file=sys.stderr)
        failure_summary = render_github_failure_summary(
            inventory_diagnostic,
            documentation_url=_documentation_url(),
        )
        print(failure_summary, file=sys.stderr, end="")
        _write_github_summary(failure_summary, requested=github_summary)
        return 2
    if reference_diagnostics:
        rendered = render_cue_diagnostics(reference_diagnostics)
        print(rendered, file=sys.stderr)
        failure_summary = render_github_failure_summary(
            reference_diagnostics,
            documentation_url=_documentation_url(),
        )
        print(failure_summary, file=sys.stderr, end="")
        _write_github_summary(failure_summary, requested=github_summary)
        return 1

    print(f"contract: 0 violations; waivers: {waiver_count}")
    summary_written = _write_github_summary(
        render_github_success_summary(waiver_count),
        requested=github_summary,
    )
    return 0 if summary_written else 2


def main(argv: Sequence[str] | None = None) -> int:
    """Run the selected contract command."""
    arguments = _build_parser().parse_args(argv)
    if arguments.command == "install-cue":
        print(install())
        return 0
    if arguments.command == "extract":
        try:
            print(write_extracted(arguments.root, arguments.output))
        except ExtractionError as error:
            print(f"C-EXTR-001: {error}", file=sys.stderr)
            return 2
        return 0
    if arguments.command == "render-registration":
        try:
            print(write_registration(arguments.root, arguments.output))
        except ExtractionError as error:
            print(f"C-EXTR-001: {error}", file=sys.stderr)
            return 2
        return 0
    if arguments.command == "render-template-list":
        try:
            print(write_template_list(arguments.root, arguments.output))
        except ExtractionError as error:
            print(f"C-EXTR-001: {error}", file=sys.stderr)
            return 2
        return 0
    if arguments.command == "vet-schema":
        return _vet_schema(arguments.root)
    if arguments.command == "validate":
        return _validate(
            arguments.root,
            arguments.output,
            github_summary=arguments.github_summary,
        )
    if arguments.command == "explain":
        return _explain(arguments.argument)

    raise NotImplementedError(f"lsp_contract.{arguments.command}")


if __name__ == "__main__":
    raise SystemExit(main())
