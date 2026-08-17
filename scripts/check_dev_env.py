"""
Reports whether this machine is ready for Serena development: core environment checks
(Python version, uv, the project virtual environment), version skew between an installed
``serena`` executable and this checkout, and which per-language pytest markers can run
locally, given the toolchains that are present.

The toolchain requirements mirror the install steps in ``.github/workflows/pytest.yml``,
which remains canonical when in doubt. Language servers themselves are not checked here:
Serena downloads most of them on first use. What is checked are the toolchains those
servers and the test fixtures need (compilers, runtimes, package managers).

Usage::

    uv run python scripts/check_dev_env.py             # full report
    uv run python scripts/check_dev_env.py --markers   # only the pytest -m expression of runnable markers

The ``--markers`` form composes directly with pytest::

    uv run pytest test -m "$(uv run python scripts/check_dev_env.py --markers)"

Exit code: 1 if a core environment check fails, 0 otherwise. Missing language toolchains
never fail the check; they only shrink the set of runnable markers.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

NON_LANGUAGE_MARKERS = {"snapshot", "slow"}
"""markers registered in pyproject.toml that do not correspond to a language"""


@dataclass(frozen=True)
class ToolchainRequirement:
    """A local toolchain prerequisite and the pytest language markers it gates."""

    markers: tuple[str, ...]
    """the pytest markers whose tests need this toolchain"""
    commands: tuple[str, ...]
    """the executables that must be on the PATH; ``|`` separates accepted alternatives"""
    note: str
    """what the toolchain is, including version constraints worth knowing"""
    min_java: int | None = None
    """the minimum Java major version, verified in addition to the presence of ``java``"""
    min_php: tuple[int, int] | None = None
    """the minimum PHP (major, minor) version, verified in addition to the presence of ``php``"""
    min_dotnet_runtime: int | None = None
    """the minimum .NET runtime major version, verified in addition to the presence of ``dotnet``"""

    def unsatisfied(self) -> list[str]:
        """
        :return: descriptions of the requirement parts not met on this machine: commands absent
            from the PATH, plus too-old ``java``/``php``/.NET runtimes where a minimum is declared
        """
        problems = [command for command in self.commands if not any(shutil.which(alternative) for alternative in command.split("|"))]
        if self.min_java is not None and "java" in self.commands and shutil.which("java") is not None:
            major = _java_major_version()
            if major is None:
                problems.append(f"java >= {self.min_java} (the installed version could not be determined)")
            elif major < self.min_java:
                problems.append(f"java >= {self.min_java} (found {major})")
        if self.min_php is not None and "php" in self.commands and shutil.which("php") is not None:
            php_version = _php_version()
            wanted = f"php >= {self.min_php[0]}.{self.min_php[1]}"
            if php_version is None:
                problems.append(f"{wanted} (the installed version could not be determined)")
            elif php_version < self.min_php:
                problems.append(f"{wanted} (found {php_version[0]}.{php_version[1]})")
        if self.min_dotnet_runtime is not None and "dotnet" in self.commands and shutil.which("dotnet") is not None:
            majors = _dotnet_runtime_majors()
            wanted = f"dotnet runtime >= {self.min_dotnet_runtime}"
            if majors is None:
                problems.append(f"{wanted} (the installed runtimes could not be determined)")
            elif max(majors) < self.min_dotnet_runtime:
                problems.append(f"{wanted} (found {max(majors)})")
        return problems


def _java_major_version() -> int | None:
    """
    :return: the major version of the ``java`` executable on the PATH, or None if it cannot be determined
    """
    try:
        result = subprocess.run(["java", "-version"], check=False, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    # `java -version` prints to stderr, e.g. 'openjdk version "21.0.2"' or 'java version "1.8.0_402"'
    match = re.search(r'version "(\d+)(?:\.(\d+))?', result.stderr or result.stdout)
    if match is None:
        return None
    major = int(match.group(1))
    # pre-9 JVMs report 1.x
    return int(match.group(2)) if major == 1 and match.group(2) else major


def _php_version() -> tuple[int, int] | None:
    """
    :return: the (major, minor) version of the ``php`` executable on the PATH, or None if it cannot be determined
    """
    try:
        result = subprocess.run(["php", "--version"], check=False, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    match = re.search(r"PHP (\d+)\.(\d+)", result.stdout or result.stderr)
    return (int(match.group(1)), int(match.group(2))) if match else None


def _dotnet_runtime_majors() -> set[int] | None:
    """
    :return: the major versions of the installed Microsoft.NETCore.App runtimes, or None if they cannot be determined
    """
    try:
        result = subprocess.run(["dotnet", "--list-runtimes"], check=False, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    majors = {int(match.group(1)) for match in re.finditer(r"^Microsoft\.NETCore\.App (\d+)\.", result.stdout, re.MULTILINE)}
    return majors or None


TOOLCHAIN_REQUIREMENTS: list[ToolchainRequirement] = [
    # jvm batch (see MARKERS_JVM in .github/workflows/pytest.yml)
    ToolchainRequirement(("java",), ("java",), "JDK 21+ (JDTLS_MIN_JDK_VERSION in eclipse_jdtls.py)", min_java=21),
    ToolchainRequirement(("kotlin", "scala", "groovy"), ("java",), "JDK (no declared minimum; CI uses 21)"),
    ToolchainRequirement(("bsl",), ("java",), "JDK 21+ (BSL_LS_MIN_JAVA_VERSION in bsl_language_server.py)", min_java=21),
    ToolchainRequirement(("nextflow",), ("java",), "JDK 17+ (MIN_JDK_VERSION in nextflow_language_server.py)", min_java=17),
    ToolchainRequirement(("clojure",), ("java", "clojure"), "JDK + Clojure CLI"),
    ToolchainRequirement(
        ("csharp",), ("dotnet",), ".NET SDK with a 10+ runtime (the Roslyn server ships as net10.0)", min_dotnet_runtime=10
    ),
    ToolchainRequirement(("fsharp",), ("dotnet",), ".NET SDK with an 8+ runtime (fsautocomplete)", min_dotnet_runtime=8),
    # native batch
    ToolchainRequirement(("go",), ("go", "gopls"), "Go toolchain + gopls (go install golang.org/x/tools/gopls@latest)"),
    ToolchainRequirement(
        ("rust",), ("cargo", "rustup|rust-analyzer"), "Rust toolchain + rust-analyzer (resolved via rustup, or standalone on the PATH)"
    ),
    ToolchainRequirement(("zig",), ("zig", "zls"), "Zig + ZLS"),
    ToolchainRequirement(("cpp",), ("ccls",), "ccls"),
    ToolchainRequirement(("pascal",), ("fpc",), "Free Pascal (fpc + fpc-source)"),
    ToolchainRequirement(("swift",), ("swift",), "Swift, which bundles sourcekit-lsp (CI runs Swift tests on macOS only)"),
    # other-langs batch
    ToolchainRequirement(("ruby",), ("ruby", "gem"), "Ruby (ruby-lsp is installed via gem)"),
    ToolchainRequirement(("php",), ("php",), "PHP 8.1+ (enforced by phpactor, whose phar Serena downloads itself)", min_php=(8, 1)),
    ToolchainRequirement(("lua",), ("lua-language-server",), "lua-language-server"),
    ToolchainRequirement(("powershell",), ("pwsh",), "PowerShell 7 (preinstalled on CI runners)"),
    ToolchainRequirement(("elixir",), ("elixir", "erl"), "Elixir + Erlang/OTP"),
    ToolchainRequirement(("erlang",), ("erl",), "Erlang/OTP"),
    ToolchainRequirement(("dart",), ("dart",), "Dart SDK"),
    ToolchainRequirement(("deno",), ("deno",), "Deno v2 (deno lsp ships with the CLI)"),
    ToolchainRequirement(
        ("haxe",), ("haxe", "neko", "node"), "Haxe + Neko + Node.js (the downloaded haxe server is server.js, run via node)"
    ),
    ToolchainRequirement(("haskell",), ("ghc", "cabal"), "GHC + cabal for HLS (CI runs Haskell tests on Linux only)"),
    ToolchainRequirement(("terraform",), ("terraform",), "Terraform CLI"),
    ToolchainRequirement(("rego",), ("regal",), "Regal"),
    ToolchainRequirement(("ansible",), ("ansible", "ansible-lint", "node"), "ansible-core + ansible-lint + Node.js"),
    ToolchainRequirement(("gleam",), ("gleam",), "Gleam compiler (bundles `gleam lsp`)"),
    ToolchainRequirement(("systemverilog",), ("verible-verilog-ls",), "Verible"),
    ToolchainRequirement(("qml",), ("qmlls6|qmlls",), "Qt qmlls, qmlls6 preferred (CI runs QML tests on Linux only)"),
    ToolchainRequirement(("matlab",), ("matlab", "node"), "MATLAB R2021b+ + Node.js (the MATLAB language server runs via node)"),
    ToolchainRequirement(("wolfram",), ("wolframscript",), "Mathematica 13.0+ or Wolfram Engine 12.1+"),
    ToolchainRequirement(("crystal",), ("crystalline",), "Crystalline (not auto-installed by Serena; crystal tests skip without it)"),
    # niche batch
    ToolchainRequirement(("julia",), ("julia",), "Julia (plus the LanguageServer.jl package)"),
    ToolchainRequirement(("r",), ("R", "Rscript"), "R (plus the languageserver package)"),
    ToolchainRequirement(("perl",), ("perl", "cpanm"), "Perl + cpanminus (Perl::LanguageServer; CI skips Perl tests on Windows)"),
    ToolchainRequirement(("lean4",), ("lake",), "Lean 4 via elan (the test fixture is built with lake)"),
    ToolchainRequirement(("nix",), ("nix", "nixd"), "Nix + nixd (CI skips Nix tests on Windows)"),
    ToolchainRequirement(("ocaml",), ("opam", "ocamllsp"), "opam + ocaml-lsp-server"),
    # catch-all batch: npm-distributed language servers need a Node.js runtime
    ToolchainRequirement(
        ("typescript", "vue", "angular", "svelte", "yaml", "json", "html", "scss", "bash", "solidity"),
        ("node", "npm"),
        "Node.js (npm-distributed language servers; Angular and Svelte fixtures also run npm installs)",
    ),
    ToolchainRequirement(("elm",), ("elm", "node"), "Elm compiler (CI installs it via npm)"),
]


def _read_pyproject() -> dict:
    """
    :return: the parsed content of this checkout's pyproject.toml
    """
    with open(REPO_ROOT / "pyproject.toml", "rb") as f:
        return tomllib.load(f)


def _language_markers(pyproject: dict) -> list[str]:
    """
    :param pyproject: the parsed pyproject.toml content
    :return: the names of all registered language markers, in registration order
    """
    marker_definitions = pyproject["tool"]["pytest"]["ini_options"]["markers"]
    names = [definition.split(":")[0].strip() for definition in marker_definitions]
    return [name for name in names if name not in NON_LANGUAGE_MARKERS]


def _python_version_in_range(requires_python: str) -> bool:
    """
    :param requires_python: the requires-python specifier from pyproject.toml (e.g. ">=3.11, <3.15")
    :return: whether the running interpreter satisfies the lower and upper bounds of the specifier
    """
    current = sys.version_info[:2]
    for constraint in requires_python.split(","):
        match = re.fullmatch(r"\s*(>=|<=|<|>)\s*(\d+)\.(\d+)\s*", constraint)
        if match is None:
            continue
        operator, bound = match.group(1), (int(match.group(2)), int(match.group(3)))
        if operator == ">=" and current < bound:
            return False
        if operator == ">" and current <= bound:
            return False
        if operator == "<" and current >= bound:
            return False
        if operator == "<=" and current > bound:
            return False
    return True


def _find_external_serena() -> Path | None:
    """
    Locates a ``serena`` executable outside this checkout — i.e. the persistent installation
    that MCP clients launching ``serena`` by name would actually run (not the entry point of
    this checkout's own virtual environment).

    :return: the path to the first such executable on the PATH, or None if there is none
    """
    for path_entry in os.get_exec_path():
        candidate = shutil.which("serena", path=path_entry)
        if candidate is None:
            continue
        if REPO_ROOT not in Path(candidate).resolve().parents:
            return Path(candidate)
    return None


def _installed_serena_version(executable: Path) -> str | None:
    """
    :param executable: the serena executable to query
    :return: the version it reports, or None if it could not be determined
    """
    try:
        result = subprocess.run([str(executable), "--version"], check=False, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    # tolerate both "Serena 1.7.1" and "serena, version 1.7.1": the version is the last token of the first line
    first_line = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
    return first_line.split()[-1] if first_line else None


def _check_core_environment(pyproject: dict) -> bool:
    """
    Prints the core environment report (interpreter, uv, virtual environment).

    :param pyproject: the parsed pyproject.toml content
    :return: whether all core checks passed
    """
    ok = True

    # running interpreter vs. the project's requires-python
    requires_python = pyproject["project"]["requires-python"]
    python_version = ".".join(str(c) for c in sys.version_info[:3])
    if _python_version_in_range(requires_python):
        print(f"  OK       Python {python_version} (project requires {requires_python})")
    else:
        print(f"  FAIL     Python {python_version} does not satisfy the project requirement '{requires_python}'")
        ok = False

    # uv, the entry point for every dev task
    uv = shutil.which("uv")
    if uv is not None:
        print(f"  OK       uv ({uv})")
    else:
        print("  FAIL     uv not found on the PATH (see CONTRIBUTING.md for setup instructions)")
        ok = False

    # the project virtual environment (informational: uv run creates it on demand)
    if (REPO_ROOT / ".venv").is_dir():
        print("  OK       .venv exists")
    else:
        print("  NOTE     .venv missing; create it with: uv venv -p 3.13 && uv sync --extra dev")

    return ok


def _check_install_skew(pyproject: dict) -> None:
    """
    Prints the version comparison between a persistently installed ``serena`` executable and this
    checkout. A skewed installation does not only run outdated code: merely starting it rewrites
    the ``project.yml`` of every registered project whose schema differs from the installed
    version's, which churns files tracked by version control (such as this repository's own
    ``.serena/project.yml``).

    :param pyproject: the parsed pyproject.toml content
    """
    checkout_version = pyproject["project"]["version"]
    installed = _find_external_serena()
    if installed is None:
        print("  NOTE     no serena installation found outside this checkout (fine if you only use `uv run serena`)")
        return
    installed_version = _installed_serena_version(installed)
    if installed_version is None:
        print(f"  WARN     {installed} did not report a version")
        return
    if installed_version == checkout_version:
        print(f"  OK       installed serena ({installed}) matches the checkout: {installed_version}")
    else:
        print(f"  WARN     installed serena ({installed}) is {installed_version}, checkout is {checkout_version}")
        print("           A version-skewed installation rewrites the project.yml of every registered project on")
        print("           startup (including .serena/project.yml in this repository, which is tracked by git).")
        print("           Reinstall from this checkout:  uv tool install --reinstall -p 3.13 .")


def _report_toolchains(language_markers: list[str]) -> list[str]:
    """
    Prints the per-toolchain report and computes the runnable markers.

    :param language_markers: the names of all registered language markers
    :return: the markers whose required toolchains are all present, in registration order
    """
    blocked_markers: dict[str, list[str]] = {}
    for requirement in TOOLCHAIN_REQUIREMENTS:
        missing = requirement.unsatisfied()
        status = "OK  " if not missing else "MISS"
        detail = requirement.note if not missing else f"{requirement.note} — missing: {', '.join(missing)}"
        print(f"  {status}     {', '.join(requirement.markers):<55} {detail}")
        if missing:
            for marker in requirement.markers:
                blocked_markers.setdefault(marker, []).extend(missing)

    covered = {marker for requirement in TOOLCHAIN_REQUIREMENTS for marker in requirement.markers}
    uncovered = [marker for marker in language_markers if marker not in covered]
    if uncovered:
        print()
        print(f"  No local toolchain is known to be required for: {', '.join(uncovered)}")
        print("  (Serena installs or bundles these language servers itself on first use.)")

    return [marker for marker in language_markers if marker not in blocked_markers]


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--markers", action="store_true", help="print only the pytest -m expression of runnable language markers")
    args = parser.parse_args()

    pyproject = _read_pyproject()
    language_markers = _language_markers(pyproject)

    if args.markers:
        print(" or ".join(_report_runnable_markers_quietly(language_markers)))
        return 0

    print("Core environment")
    core_ok = _check_core_environment(pyproject)
    print()
    print("Installed serena vs. this checkout")
    _check_install_skew(pyproject)
    print()
    print("Language toolchains (requirements mirror .github/workflows/pytest.yml)")
    runnable = _report_toolchains(language_markers)
    print()
    print(f"Runnable language markers ({len(runnable)}/{len(language_markers)}):")
    print(f'  uv run pytest test -m "{" or ".join(runnable)}"')

    return 0 if core_ok else 1


def _report_runnable_markers_quietly(language_markers: list[str]) -> list[str]:
    """
    :param language_markers: the names of all registered language markers
    :return: the markers whose required toolchains are all present, without printing a report
    """
    blocked = {marker for requirement in TOOLCHAIN_REQUIREMENTS if requirement.unsatisfied() for marker in requirement.markers}
    return [marker for marker in language_markers if marker not in blocked]


if __name__ == "__main__":
    sys.exit(main())
