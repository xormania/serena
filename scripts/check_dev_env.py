"""
Reports whether this machine is ready for Serena development: core environment checks
(Python version, uv, the project virtual environment), version skew between an installed
``serena`` executable and this checkout, and which per-language pytest markers can run
locally, given the toolchains that are present.

The toolchain requirements mirror the availability guards in ``test/conftest.py``, which
decide whether a suite runs at all, and — for languages the guards do not mention — the
requirements of the language servers themselves. ``.github/workflows/pytest.yml`` is
context, not authority: CI installing a toolchain does not make a marker runnable if the
suite skips it anyway. Language servers themselves are not checked here: Serena downloads
or bundles most of them on first use. What is checked are the toolchains those servers and
the test fixtures need (compilers, runtimes, package managers).

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
import platform
import re
import shutil
import subprocess
import sys
import tomllib
from collections.abc import Callable
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
    min_dotnet_sdk: int | None = None
    """the minimum .NET SDK major version, verified in addition to the presence of ``dotnet``"""
    extra_check: Callable[[], str | None] | None = None
    """an additional predicate mirroring an availability guard in ``test/conftest.py``;
    returns a description of what is missing, or None when the requirement is met"""

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
        if self.min_dotnet_sdk is not None and "dotnet" in self.commands and shutil.which("dotnet") is not None:
            sdk_majors = _dotnet_sdk_majors()
            wanted = f"dotnet SDK >= {self.min_dotnet_sdk}"
            if sdk_majors is None:
                problems.append(f"{wanted} (no installed SDK could be determined — a runtime alone cannot load projects)")
            elif max(sdk_majors) < self.min_dotnet_sdk:
                problems.append(f"{wanted} (found {max(sdk_majors)})")
        if self.extra_check is not None and not problems:
            extra_problem = self.extra_check()
            if extra_problem is not None:
                problems.append(extra_problem)
        return problems


def _java_major_version(java_executable: str = "java") -> int | None:
    """
    :param java_executable: the java executable to interrogate (a PATH name or a full path)
    :return: the major version of that executable, or None if it cannot be determined
    """
    try:
        result = subprocess.run([java_executable, "-version"], check=False, capture_output=True, text=True, timeout=60)
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


def _dotnet_sdk_majors() -> set[int] | None:
    """
    :return: the major versions of the installed .NET SDKs, or None if they cannot be determined
    """
    try:
        result = subprocess.run(["dotnet", "--list-sdks"], check=False, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    # one SDK per line, e.g. '10.0.100 [/usr/lib/dotnet/sdk]'
    majors = {int(match.group(1)) for match in re.finditer(r"^(\d+)\.", result.stdout, re.MULTILINE)}
    return majors or None


def _probe_succeeds(argv: list[str], timeout: int = 60) -> bool:
    """
    :param argv: the command to run
    :param timeout: seconds before the probe is abandoned
    :return: whether the command ran and exited 0
    """
    try:
        return subprocess.run(argv, capture_output=True, timeout=timeout, check=False).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _r_languageserver_check() -> str | None:
    # mirrors test/conftest.py's _is_r_language_server_available: the R binary alone is not enough
    probe = ["R", "--vanilla", "-e", 'quit(status = as.integer(!requireNamespace("languageserver", quietly = TRUE)))']
    return None if _probe_succeeds(probe) else "the R package 'languageserver'"


def _ocamllsp_check() -> str | None:
    # mirrors test/conftest.py's _is_ocaml_lsp_available: ocamllsp must resolve in the active opam switch
    return None if _probe_succeeds(["opam", "exec", "--", "ocamllsp", "--version"]) else "ocamllsp in the active opam switch"


def _perl_language_server_check() -> str | None:
    # mirrors test/conftest.py's _is_perl_language_server_available: perl ships with most systems, the module is the signal
    return None if _probe_succeeds(["perl", "-MPerl::LanguageServer", "-e", "1"], timeout=30) else "the Perl::LanguageServer module"


def _windows_disabled_check() -> str | None:
    # ansible-language-server has no native Windows support; the erlang and zig suites skip on Windows
    return "a non-Windows platform (the suite is disabled on native Windows)" if sys.platform == "win32" else None


def _macos_only_check() -> str | None:
    # test/conftest.py enables the swift suite only on macOS (swiftly is set up on the macOS batch)
    return None if sys.platform == "darwin" else "macOS (the swift suite is enabled only there)"


def _hlsl_server_availability_check() -> str | None:
    # mirrors the provider's dependency matrix: prebuilt binaries exist for win-x64,
    # win-arm64 and linux-x64; macOS builds from source via cargo; any other platform
    # (e.g. linux-arm64) has no managed strategy and needs a system server
    if shutil.which("shader-language-server"):
        return None
    machine = platform.machine().lower()
    if sys.platform == "darwin":
        return None if shutil.which("cargo") else "an existing shader-language-server, or cargo to build it (macOS has no prebuilt binary)"
    if sys.platform.startswith("linux") and machine in ("x86_64", "amd64"):
        return None
    if sys.platform == "win32" and machine in ("amd64", "x86_64", "arm64", "aarch64"):
        return None
    return "a system shader-language-server (no prebuilt binary or build path exists for this platform)"


def _dart_managed_sdk_check() -> str | None:
    # mirrors DartLanguageServer's managed-SDK matrix (linux-x64, win-x64/arm64,
    # osx-x64/arm64): on those platforms Serena downloads its pinned SDK. Elsewhere the
    # suite CANNOT run at all -- the provider goes straight to its dependency table and
    # never resolves a system dart, so a PATH dart must not count
    machine = platform.machine().lower()
    if sys.platform == "darwin" or (sys.platform == "win32" and machine in ("amd64", "x86_64", "arm64", "aarch64")):
        return None
    if sys.platform.startswith("linux") and machine in ("x86_64", "amd64"):
        return None
    return "a platform in the managed-SDK matrix (the provider does not use a system dart)"


# rust-analyzer's fallback locations, split by whether they are under the home directory, so
# a test can neutralise the machine-wide ones instead of depending on what this host happens
# to have in /usr/local
RUST_ANALYZER_HOME_RELATIVE_PATHS: tuple[str, ...] = (
    (".cargo/bin/rust-analyzer.exe", "scoop/shims/rust-analyzer.exe", "scoop/apps/rust-analyzer/current/rust-analyzer.exe")
    if os.name == "nt"
    else (".cargo/bin/rust-analyzer", ".local/bin/rust-analyzer")
)
RUST_ANALYZER_FIXED_PATHS: tuple[str, ...] = (
    (str(Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "rust-analyzer" / "rust-analyzer.exe"),)
    if os.name == "nt"
    else ("/opt/homebrew/bin/rust-analyzer", "/usr/local/bin/rust-analyzer")
)


def _rust_analyzer_check() -> str | None:
    # mirrors _ensure_rust_analyzer_installed (rust_analyzer.py) read-only: rustup counts
    # (it can install the matching component), then a PATH rust-analyzer, then the
    # provider's common install locations -- which() alone missed those
    if shutil.which("rustup") or shutil.which("rust-analyzer"):
        return None
    home = Path.home()
    candidates = [home / relative for relative in RUST_ANALYZER_HOME_RELATIVE_PATHS] + [Path(fixed) for fixed in RUST_ANALYZER_FIXED_PATHS]
    if any(candidate.is_file() and os.access(candidate, os.X_OK) for candidate in candidates):
        return None
    return "rust-analyzer (via rustup, the PATH, or a standard install location)"


def _managed_binary_platform_check(what: str, windows_arm64: bool, extra_arches: bool = False) -> str | None:
    """
    :param what: the managed binary, named in the verdict
    :param windows_arm64: whether a Windows arm64 build exists
    :param extra_arches: whether architectures beyond x86_64/arm64 are supported
    :return: what is missing, or None when this platform is served

    Several servers download a mandatory helper whose upstream publishes a narrower platform
    set than Serena runs on, and the failure is a hard raise during startup rather than a
    skip -- so the marker must not be reported runnable there.
    """
    machine = platform.machine().lower()
    is_x64 = machine in ("x86_64", "amd64")
    is_arm64 = machine in ("arm64", "aarch64")
    if not (is_x64 or is_arm64 or extra_arches):
        return f"a supported architecture for {what} (no build exists for {machine})"
    if sys.platform == "win32" and is_arm64 and not windows_arm64:
        return f"a Windows arm64 build of {what} (none is published)"
    # PlatformUtils keys musl Linux separately (linux-musl-*), and these upstreams publish
    # nothing under those keys -- same libc test the provider uses
    if sys.platform.startswith("linux") and platform.libc_ver()[0] != "glibc":
        return f"a glibc Linux build of {what} (musl platforms have no published build)"
    return None


def _solidity_forge_check() -> str | None:
    # mirrors _get_forge_npm_package (solidity_language_server.py): forge publishes no
    # Windows arm64 package and nothing outside x86_64/arm64, and the raise happens while
    # BUILDING the dependency collection -- before any install or cache check
    return _managed_binary_platform_check("foundry forge", windows_arm64=False)


def _bash_shellcheck_check() -> str | None:
    # mirrors _SHELLCHECK_DEPENDENCIES (bash_language_server.py): linux/osx x64+arm64 and
    # win x64 only; _install_shellcheck_if_missing raises on anything else
    return _managed_binary_platform_check("ShellCheck", windows_arm64=False)


def _pascal_pasls_check() -> str | None:
    # mirrors the pasls download matrix (pascal_server.py): linux/osx x64+arm64 and win x64.
    # A pasls already on the PATH short-circuits the download, so it is accepted first
    if shutil.which("pasls"):
        return None
    return _managed_binary_platform_check("pasls", windows_arm64=False)


def _matlab_installation_check() -> str | None:
    # mirrors _is_matlab_available (test/conftest.py): MATLAB_PATH or a known install location --
    # a bare PATH launcher is NOT accepted, because neither the guard nor the provider's
    # _find_matlab_installation resolves one; and the provider rejects a MATLAB_PATH that is
    # not a real directory, so a stale value must not count
    matlab_path = os.environ.get("MATLAB_PATH")
    if matlab_path and Path(matlab_path).is_dir():
        return None
    known_locations = (
        "/Applications/MATLAB_R2024b.app",
        "/Applications/MATLAB_R2025b.app",
        "/Volumes/S1/Applications/MATLAB_R2024b.app",
        "/Volumes/S1/Applications/MATLAB_R2025b.app",
    )
    if any(Path(location).exists() for location in known_locations):
        return None
    return "a locatable MATLAB installation (a MATLAB_PATH naming a real directory, or a standard install dir)"


def _suite_always_disabled_check() -> str | None:
    # test/conftest.py section 1: the suite is disabled everywhere, regardless of toolchains
    return "a conftest re-enable (the suite is currently always-disabled as unreliable)"


def _clojure_cli_check() -> str | None:
    # mirrors verify_clojure_cli (clojure_lsp.py), which requires BOTH capabilities: the official
    # CLI advertises -Aaliases in its help text, and tools.deps must resolve a classpath (-Spath);
    # distro launchers can pass one and fail the other
    try:
        help_proc = subprocess.run(["clojure", "--help"], capture_output=True, text=True, timeout=120, check=False)
    except (OSError, subprocess.SubprocessError):
        return "a functional tools.deps Clojure CLI (clojure --help failed)"
    if help_proc.returncode != 0 or "-Aaliases" not in help_proc.stdout + help_proc.stderr:
        return "the official Clojure CLI (this launcher does not advertise -Aaliases)"
    if _probe_succeeds(["clojure", "-Spath"], timeout=120):
        return None
    return "a functional tools.deps Clojure CLI (clojure -Spath failed)"


def _nextflow_java_check() -> str | None:
    # mirrors NextflowLanguageServer._resolve_java: $JAVA_HOME/bin/java is consulted before
    # the PATH, and the FIRST existing candidate is the one whose version must satisfy 17+
    java_exe_name = "java.exe" if os.name == "nt" else "java"
    java_home = os.environ.get("JAVA_HOME")
    if java_home and Path(java_home, "bin", java_exe_name).is_file():
        chosen = str(Path(java_home, "bin", java_exe_name))
    else:
        chosen = shutil.which("java")
    if chosen is None:
        return "a JDK 17+ (via JAVA_HOME/bin/java or the PATH)"
    major = _java_major_version(chosen)
    if major is None:
        return "a JDK 17+ (the resolved java's version could not be determined)"
    if major < 17:
        return f"java >= 17 for nextflow (found {major} via the server's resolution order)"
    return None


def _groovy_ls_jar_check() -> str | None:
    # the groovy suite skips unless GROOVY_LS_JAR_PATH names an existing JAR (test/solidlsp/groovy)
    jar_path = os.environ.get("GROOVY_LS_JAR_PATH")
    if jar_path and Path(jar_path).is_file():
        return None
    return "GROOVY_LS_JAR_PATH naming an existing Groovy language-server JAR"


def _wolfram_kernel_check() -> str | None:
    # mirrors the kernel discovery the server and test/conftest.py use; falls back to a PATH
    # lookup when solidlsp is not importable, since this script is otherwise stdlib-only
    try:
        from solidlsp.language_servers.wolfram_language_server import _find_wolfram_kernel
    except ImportError:
        return None if shutil.which("WolframKernel") is not None else "a WolframKernel (wolframscript alone is not enough)"
    try:
        _find_wolfram_kernel()
    except FileNotFoundError:
        return "a WolframKernel (wolframscript alone is not enough)"
    return None


def _pwsh_discovery_check() -> str | None:
    # mirrors PowerShellLanguageServer._get_pwsh_path: PATH first, then fixed per-OS install
    # locations such as ~/.dotnet/tools/pwsh; falls back to a PATH lookup when solidlsp is not
    # importable, since this script is otherwise stdlib-only
    try:
        from solidlsp.language_servers.powershell_language_server import PowerShellLanguageServer
    except ImportError:
        return None if shutil.which("pwsh") is not None else "PowerShell 7 (pwsh)"
    if PowerShellLanguageServer._get_pwsh_path() is not None:
        return None
    return "PowerShell 7 (pwsh on PATH or in a standard install location)"


TOOLCHAIN_REQUIREMENTS: list[ToolchainRequirement] = [
    # jvm batch (see MARKERS_JVM in .github/workflows/pytest.yml)
    ToolchainRequirement(("scala",), ("java", "metals|cs|coursier"), "JDK + Metals (a global metals, or cs/coursier to bootstrap it)"),
    ToolchainRequirement(
        ("groovy",),
        (),
        "a Groovy language-server JAR named by GROOVY_LS_JAR_PATH (run on Serena's managed JRE)",
        extra_check=_groovy_ls_jar_check,
    ),
    ToolchainRequirement(
        ("bsl",),
        ("java",),
        "JDK 21+ (bsl_language_server.py; suite currently always-disabled in test/conftest.py as flaky)",
        min_java=21,
        extra_check=_suite_always_disabled_check,
    ),
    ToolchainRequirement(
        ("nextflow",),
        (),
        "JDK 17+ resolved the way the server resolves it: JAVA_HOME/bin/java, then the PATH",
        extra_check=_nextflow_java_check,
    ),
    ToolchainRequirement(
        ("clojure",), ("java", "clojure"), "JDK + a functional tools.deps Clojure CLI (probed)", extra_check=_clojure_cli_check
    ),
    ToolchainRequirement(
        ("csharp",),
        ("dotnet",),
        ".NET SDK 8+ and a 10+ runtime (the Roslyn server ships as net10.0; loading the SDK-style net8.0 test project needs an SDK)",
        min_dotnet_runtime=10,
        min_dotnet_sdk=8,
    ),
    ToolchainRequirement(
        ("fsharp",),
        ("dotnet",),
        ".NET SDK with an 8+ runtime (fsautocomplete; suite currently always-disabled in test/conftest.py as unreliable)",
        min_dotnet_runtime=8,
        extra_check=_suite_always_disabled_check,
    ),
    # native batch
    ToolchainRequirement(("go",), ("go", "gopls"), "Go toolchain + gopls (go install golang.org/x/tools/gopls@latest)"),
    ToolchainRequirement(
        ("rust",),
        ("cargo",),
        "Rust toolchain + rust-analyzer (rustup, the PATH, or a standard install location — the provider's search order)",
        extra_check=_rust_analyzer_check,
    ),
    ToolchainRequirement(("zig",), ("zig", "zls"), "Zig + ZLS (the suite skips on native Windows)", extra_check=_windows_disabled_check),
    ToolchainRequirement(
        ("cpp",), ("clangd",), "clangd (part of the cpp suite launches it unconditionally; ccls is an optional extra server)"
    ),
    ToolchainRequirement(
        ("pascal",),
        ("fpc",),
        "Free Pascal (fpc + fpc-source); pasls is downloaded for linux/macOS x64+arm64 and Windows x64",
        extra_check=_pascal_pasls_check,
    ),
    ToolchainRequirement(
        ("swift",), ("swift",), "Swift, which bundles sourcekit-lsp (the suite is enabled on macOS only)", extra_check=_macos_only_check
    ),
    # other-langs batch
    ToolchainRequirement(("ruby",), ("ruby", "gem|ruby-lsp"), "Ruby (a global ruby-lsp is used if present, else gem installs it)"),
    ToolchainRequirement(
        ("php",),
        ("php", "node", "npm"),
        "PHP 8.1+ with Node.js/npm (intelephense, the default php server, runs on node; phpactor is the conditional extra)",
        min_php=(8, 1),
    ),
    ToolchainRequirement(
        ("powershell",),
        (),
        "PowerShell 7 (discovered the way the server does: PATH or a standard install location)",
        extra_check=_pwsh_discovery_check,
    ),
    ToolchainRequirement(("elixir",), ("elixir", "erl", "mix"), "Elixir + Erlang/OTP + mix (the fixture runs mix deps.get/compile)"),
    ToolchainRequirement(
        ("erlang",),
        ("erl", "rebar3", "erlang_ls"),
        "Erlang/OTP + rebar3 (the fixture compiles with it) + erlang_ls; the suite is disabled on native Windows",
        extra_check=_windows_disabled_check,
    ),
    ToolchainRequirement(
        ("dart",),
        (),
        "Dart (Serena downloads its pinned SDK on win/mac x64+arm64 and linux x64; other platforms cannot run the suite)",
        extra_check=_dart_managed_sdk_check,
    ),
    ToolchainRequirement(("deno",), ("deno",), "Deno v2 (deno lsp ships with the CLI)"),
    ToolchainRequirement(
        ("haxe",), ("haxe", "node"), "Haxe + Node.js (the downloaded haxe server is server.js, run via node; neko is never invoked)"
    ),
    ToolchainRequirement(
        ("haskell",),
        ("ghc", "cabal", "haskell-language-server-wrapper"),
        "GHC + cabal + the HLS wrapper (CI runs Haskell tests on Linux only)",
    ),
    ToolchainRequirement(("terraform",), ("terraform",), "Terraform CLI"),
    ToolchainRequirement(("rego",), ("regal",), "Regal"),
    ToolchainRequirement(
        ("ansible",),
        ("ansible", "node", "npm"),
        "ansible-core + Node.js with npm (ansible-lint only matters when the optional linting setting is on); no native Windows support",
        extra_check=_windows_disabled_check,
    ),
    ToolchainRequirement(("gleam",), ("gleam",), "Gleam compiler (bundles `gleam lsp`)"),
    ToolchainRequirement(("systemverilog",), ("verible-verilog-ls",), "Verible"),
    ToolchainRequirement(("qml",), ("qmlls6|qmlls",), "Qt qmlls, qmlls6 preferred (CI runs QML tests on Linux only)"),
    ToolchainRequirement(
        ("matlab",),
        ("node",),
        "MATLAB R2021b+ (discovered via MATLAB_PATH or a standard install dir) + Node.js for its language server",
        extra_check=_matlab_installation_check,
    ),
    ToolchainRequirement(
        ("hlsl",),
        (),
        "shader-language-server (prebuilt for win x64/arm64 + linux x64; macOS builds via cargo; other platforms need a system binary)",
        extra_check=_hlsl_server_availability_check,
    ),
    ToolchainRequirement(
        ("wolfram",),
        (),
        "Mathematica 13.0+ or Wolfram Engine 12.1+ (kernel discovery, not wolframscript)",
        extra_check=_wolfram_kernel_check,
    ),
    ToolchainRequirement(("crystal",), ("crystalline",), "Crystalline (not auto-installed by Serena; crystal tests skip without it)"),
    # niche batch
    ToolchainRequirement(("julia",), ("julia",), "Julia (plus the LanguageServer.jl package)"),
    ToolchainRequirement(
        ("r",), ("R",), "R + the languageserver package (probed; CI uses Rscript only to install it)", extra_check=_r_languageserver_check
    ),
    ToolchainRequirement(
        ("perl",),
        ("perl",),
        "Perl + the Perl::LanguageServer module (probed; CI skips Perl tests on Windows)",
        extra_check=_perl_language_server_check,
    ),
    ToolchainRequirement(("lean4",), ("lean", "lake"), "Lean 4 via elan (lean runs the server; the test fixture is built with lake)"),
    ToolchainRequirement(
        ("nix",),
        ("nix", "nixd"),
        "Nix + nixd (the provider refuses to start without the nix CLI, even with nixd already on the PATH)",
    ),
    ToolchainRequirement(
        ("ocaml",), ("opam",), "opam + ocaml-lsp-server resolved in the active switch (probed)", extra_check=_ocamllsp_check
    ),
    # catch-all batch: npm-distributed language servers need a Node.js runtime
    ToolchainRequirement(
        ("typescript", "vue", "angular", "svelte", "yaml", "json", "html", "scss"),
        ("node", "npm"),
        "Node.js (npm-distributed language servers; Angular and Svelte fixtures also run npm installs)",
    ),
    # same npm-distributed servers, but each pulls a mandatory helper binary whose upstream
    # platform set is narrower than Serena's -- and a missing build RAISES, it does not skip
    ToolchainRequirement(
        ("bash",),
        ("node", "npm"),
        "Node.js + a ShellCheck release for this platform (linux/macOS x64+arm64, Windows x64)",
        extra_check=_bash_shellcheck_check,
    ),
    ToolchainRequirement(
        ("solidity",),
        ("node", "npm"),
        "Node.js + a foundry forge npm package for this platform (no Windows arm64 build)",
        extra_check=_solidity_forge_check,
    ),
    ToolchainRequirement(
        ("elm",),
        ("elm", "elm-language-server|node", "elm-language-server|npm"),
        "Elm plus either a system elm-language-server or node+npm for Serena to install it",
    ),
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


def _python_version_in_range(requires_python: str) -> tuple[bool, list[str]]:
    """
    :param requires_python: the requires-python specifier from pyproject.toml (e.g. ">=3.11, <3.15")
    :return: whether the running interpreter satisfies every constraint this function
        understands, and the constraints it could not parse. Unparsed constraints are
        REPORTED rather than skipped: silently treating an unrecognised ``!=3.13.*`` as
        satisfied would tell a contributor their interpreter is fine when the project
        excludes it.
    """
    current = sys.version_info[:2]
    satisfied = True
    unparsed: list[str] = []
    for constraint in requires_python.split(","):
        if not constraint.strip():
            continue
        match = re.fullmatch(r"\s*(>=|<=|<|>)\s*(\d+)\.(\d+)\s*", constraint)
        if match is None:
            unparsed.append(constraint.strip())
            continue
        operator, bound = match.group(1), (int(match.group(2)), int(match.group(3)))
        if operator == ">=" and current < bound:
            satisfied = False
        if operator == ">" and current <= bound:
            satisfied = False
        if operator == "<" and current >= bound:
            satisfied = False
        if operator == "<=" and current > bound:
            satisfied = False
    return satisfied, unparsed


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
    in_range, unparsed = _python_version_in_range(requires_python)
    if not in_range:
        print(f"  FAIL     Python {python_version} does not satisfy the project requirement '{requires_python}'")
        ok = False
    elif unparsed:
        print(f"  NOTE     Python {python_version} satisfies the bounds this script understands in '{requires_python}';")
        print(f"           it could not check: {', '.join(unparsed)}")
    else:
        print(f"  OK       Python {python_version} (project requires {requires_python})")

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


def _evaluate_toolchains() -> list[tuple[ToolchainRequirement, list[str]]]:
    """
    :return: every requirement paired with what it is missing on this machine (an empty list
        when the requirement is satisfied). One evaluation, so the printed report and the
        ``--markers`` expression can never disagree about what is runnable.
    """
    return [(requirement, requirement.unsatisfied()) for requirement in TOOLCHAIN_REQUIREMENTS]


def _runnable_markers(language_markers: list[str], evaluated: list[tuple[ToolchainRequirement, list[str]]]) -> list[str]:
    """
    :param language_markers: the names of all registered language markers
    :param evaluated: the requirement/missing pairs from :func:`_evaluate_toolchains`
    :return: the markers whose required toolchains are all present, in registration order
    """
    blocked = {marker for requirement, missing in evaluated if missing for marker in requirement.markers}
    return [marker for marker in language_markers if marker not in blocked]


def _report_toolchains(language_markers: list[str], evaluated: list[tuple[ToolchainRequirement, list[str]]]) -> list[str]:
    """
    Prints the per-toolchain report and computes the runnable markers.

    :param language_markers: the names of all registered language markers
    :param evaluated: the requirement/missing pairs from :func:`_evaluate_toolchains`
    :return: the markers whose required toolchains are all present, in registration order
    """
    for requirement, missing in evaluated:
        status = "OK  " if not missing else "MISS"
        detail = requirement.note if not missing else f"{requirement.note} — missing: {', '.join(missing)}"
        print(f"  {status}     {', '.join(requirement.markers):<55} {detail}")

    covered = {marker for requirement in TOOLCHAIN_REQUIREMENTS for marker in requirement.markers}
    uncovered = [marker for marker in language_markers if marker not in covered]
    if uncovered:
        print()
        print(f"  No local toolchain is known to be required for: {', '.join(uncovered)}")
        print("  (Serena installs or bundles these language servers itself on first use.)")

    return _runnable_markers(language_markers, evaluated)


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--markers", action="store_true", help="print only the pytest -m expression of runnable language markers")
    args = parser.parse_args()

    pyproject = _read_pyproject()
    language_markers = _language_markers(pyproject)

    if args.markers:
        runnable = _runnable_markers(language_markers, _evaluate_toolchains())
        if not runnable:
            # an empty expression is NOT an empty selection: `pytest -m ""` applies no filter
            # at all and runs the entire suite, the exact opposite of what this machine can do
            print("no language marker is runnable on this machine; see the full report", file=sys.stderr)
            return 1
        print(" or ".join(runnable))
        return 0

    print("Core environment")
    core_ok = _check_core_environment(pyproject)
    print()
    print("Installed serena vs. this checkout")
    _check_install_skew(pyproject)
    print()
    print("Language toolchains (mirroring test/conftest.py's availability guards and the language servers' own requirements)")
    runnable = _report_toolchains(language_markers, _evaluate_toolchains())
    print()
    print(f"Runnable language markers ({len(runnable)}/{len(language_markers)}):")
    if runnable:
        print(f'  uv run pytest test -m "{" or ".join(runnable)}"')
    else:
        print("  none — install a toolchain above; an empty -m expression would run the whole suite instead of nothing")

    return 0 if core_ok else 1


if __name__ == "__main__":
    sys.exit(main())
