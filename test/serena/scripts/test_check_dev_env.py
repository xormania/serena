"""Behavior tests for the dev-environment doctor (check_dev_env.py).

Each scenario states a machine condition (Given), evaluates a requirement or version probe
(When), and asserts that the verdict names exactly what the condition implies (Then). No
real toolchain is consulted: PATH lookups and version probes are replaced per scenario.
"""

import os
import subprocess
import sys

import pytest


def _which_map(available: dict[str, str]):
    """A shutil.which replacement resolving only the given commands"""
    return lambda command: available.get(command)


class TestRequirementVerdicts:
    """A requirement's verdict lists exactly the unmet parts, by name and version."""

    def test_an_absent_command_is_named_in_the_verdict(self, doctor, monkeypatch) -> None:
        """Given a required executable that is not installed, when the requirement is
        evaluated, then the verdict names that executable.
        """
        monkeypatch.setattr(doctor.shutil, "which", _which_map({}))
        requirement = doctor.ToolchainRequirement(("x",), ("somecompiler",), "note")
        assert requirement.unsatisfied() == ["somecompiler"]

    def test_any_pipe_separated_alternative_satisfies_the_requirement(self, doctor, monkeypatch) -> None:
        """Given a requirement accepting qmlls6 or qmlls, when only qmlls6 is installed,
        then nothing is unmet — and with neither installed, the verdict shows both names.
        """
        requirement = doctor.ToolchainRequirement(("qml",), ("qmlls6|qmlls",), "note")
        monkeypatch.setattr(doctor.shutil, "which", _which_map({"qmlls6": "/usr/bin/qmlls6"}))
        assert requirement.unsatisfied() == []
        monkeypatch.setattr(doctor.shutil, "which", _which_map({}))
        assert requirement.unsatisfied() == ["qmlls6|qmlls"]

    def test_a_too_old_java_is_reported_with_required_and_found_versions(self, doctor, monkeypatch) -> None:
        """Given java installed at major 17 against a declared minimum of 21, when the
        requirement is evaluated, then the verdict reads 'java >= 21 (found 17)'.
        """
        monkeypatch.setattr(doctor.shutil, "which", _which_map({"java": "/usr/bin/java"}))
        monkeypatch.setattr(doctor, "_java_major_version", lambda: 17)
        requirement = doctor.ToolchainRequirement(("java",), ("java",), "note", min_java=21)
        assert requirement.unsatisfied() == ["java >= 21 (found 17)"]

    def test_a_java_meeting_the_minimum_is_not_reported(self, doctor, monkeypatch) -> None:
        """Given java installed at exactly the declared minimum, then nothing is unmet."""
        monkeypatch.setattr(doctor.shutil, "which", _which_map({"java": "/usr/bin/java"}))
        monkeypatch.setattr(doctor, "_java_major_version", lambda: 21)
        requirement = doctor.ToolchainRequirement(("java",), ("java",), "note", min_java=21)
        assert requirement.unsatisfied() == []

    def test_a_too_old_php_is_reported_with_required_and_found_versions(self, doctor, monkeypatch) -> None:
        """Given PHP 7.4 installed against a declared minimum of 8.1, then the verdict
        reads 'php >= 8.1 (found 7.4)'.
        """
        monkeypatch.setattr(doctor.shutil, "which", _which_map({"php": "/usr/bin/php"}))
        monkeypatch.setattr(doctor, "_php_version", lambda: (7, 4))
        requirement = doctor.ToolchainRequirement(("php",), ("php",), "note", min_php=(8, 1))
        assert requirement.unsatisfied() == ["php >= 8.1 (found 7.4)"]

    def test_the_newest_installed_dotnet_runtime_decides_the_verdict(self, doctor, monkeypatch) -> None:
        """Given .NET runtimes 8 and 10 installed against a minimum of 10, nothing is
        unmet; given only 8, the verdict reads 'dotnet runtime >= 10 (found 8)'.
        """
        monkeypatch.setattr(doctor.shutil, "which", _which_map({"dotnet": "/usr/bin/dotnet"}))
        requirement = doctor.ToolchainRequirement(("csharp",), ("dotnet",), "note", min_dotnet_runtime=10)
        monkeypatch.setattr(doctor, "_dotnet_runtime_majors", lambda: {8, 10})
        assert requirement.unsatisfied() == []
        monkeypatch.setattr(doctor, "_dotnet_runtime_majors", lambda: {8})
        assert requirement.unsatisfied() == ["dotnet runtime >= 10 (found 8)"]

    def test_platform_matrix_checks_reject_hosts_without_a_managed_strategy(self, doctor, monkeypatch) -> None:
        """Given a linux-arm64 host with neither toolchain on the PATH, both matrix-modelled
        rows name what is missing — dart's managed SDK and hlsl's prebuilt server cover
        linux only on x86_64; given linux-x86_64, both are satisfied with nothing installed.
        """
        monkeypatch.setattr(doctor.sys, "platform", "linux")
        monkeypatch.setattr(doctor.platform, "machine", lambda: "aarch64")
        # a PATH dart must not rescue an off-matrix host: the provider goes straight to its
        # dependency table and never resolves a system dart
        monkeypatch.setattr(doctor.shutil, "which", _which_map({"dart": "/usr/bin/dart"}))
        assert doctor._dart_managed_sdk_check() == "a platform in the managed-SDK matrix (the provider does not use a system dart)"
        monkeypatch.setattr(doctor.shutil, "which", _which_map({}))
        assert doctor._hlsl_server_availability_check() == (
            "a system shader-language-server (no prebuilt binary or build path exists for this platform)"
        )
        monkeypatch.setattr(doctor.platform, "machine", lambda: "x86_64")
        assert doctor._dart_managed_sdk_check() is None
        assert doctor._hlsl_server_availability_check() is None

    def test_rust_analyzer_is_found_in_the_providers_fallback_locations(self, doctor, monkeypatch, tmp_path) -> None:
        """Given neither rustup nor rust-analyzer on the PATH but an executable binary in
        ~/.cargo/bin, the check accepts it — the provider searches its common locations
        after the PATH, and which() alone missed them; with that binary gone it reports
        rust-analyzer missing. The machine-wide locations are neutralised so the verdict
        comes from the code rather than from whatever this host has in /usr/local.
        """
        monkeypatch.setattr(doctor.shutil, "which", _which_map({}))
        monkeypatch.setattr(doctor, "RUST_ANALYZER_FIXED_PATHS", ())
        monkeypatch.setattr(doctor.Path, "home", classmethod(lambda cls: tmp_path))
        assert doctor._rust_analyzer_check() == "rust-analyzer (via rustup, the PATH, or a standard install location)"
        (tmp_path / ".cargo" / "bin").mkdir(parents=True)
        binary = tmp_path / ".cargo" / "bin" / ("rust-analyzer.exe" if os.name == "nt" else "rust-analyzer")
        binary.write_text("#!/bin/sh\n")
        binary.chmod(0o755)
        assert doctor._rust_analyzer_check() is None

    def test_mandatory_helper_binaries_gate_platforms_their_upstream_skips(self, doctor, monkeypatch) -> None:
        """Given Windows on arm64, the rows whose servers download a mandatory helper report
        it missing — ShellCheck, foundry forge and pasls publish no build there, and the
        provider RAISES rather than skipping, so the marker must not be called runnable;
        on Windows x64 the same rows are satisfied, and a pasls already on the PATH rescues
        the pascal row anywhere.
        """
        monkeypatch.setattr(doctor.sys, "platform", "win32")
        monkeypatch.setattr(doctor.platform, "machine", lambda: "ARM64")
        monkeypatch.setattr(doctor.shutil, "which", _which_map({}))
        assert doctor._bash_shellcheck_check() == "a Windows arm64 build of ShellCheck (none is published)"
        assert doctor._solidity_forge_check() == "a Windows arm64 build of foundry forge (none is published)"
        assert doctor._pascal_pasls_check() == "a Windows arm64 build of pasls (none is published)"
        monkeypatch.setattr(doctor.shutil, "which", _which_map({"pasls": "C:/tools/pasls.exe"}))
        assert doctor._pascal_pasls_check() is None
        monkeypatch.setattr(doctor.platform, "machine", lambda: "AMD64")
        monkeypatch.setattr(doctor.shutil, "which", _which_map({}))
        assert doctor._bash_shellcheck_check() is None
        assert doctor._solidity_forge_check() is None

    def test_nextflow_java_resolves_through_java_home_before_the_path(self, doctor, monkeypatch, tmp_path) -> None:
        """Given a JDK 17 exposed only through JAVA_HOME (nothing on the PATH), the nextflow
        check accepts it — the server consults $JAVA_HOME/bin/java first; given only a
        too-old PATH java, the verdict names the resolved major.
        """
        java_bin = tmp_path / "jdk" / "bin"
        java_bin.mkdir(parents=True)
        (java_bin / ("java.exe" if os.name == "nt" else "java")).write_text("#!/bin/sh\n")
        monkeypatch.setenv("JAVA_HOME", str(tmp_path / "jdk"))
        monkeypatch.setattr(doctor.shutil, "which", _which_map({}))
        monkeypatch.setattr(doctor, "_java_major_version", lambda exe="java": 17)
        assert doctor._nextflow_java_check() is None

        # BOTH present and disagreeing: this is the scenario that actually pins the ORDER.
        # With only one source present at a time, an inverted implementation passes too.
        def major_of(executable="java"):
            return 17 if str(tmp_path) in str(executable) else 11

        monkeypatch.setattr(doctor.shutil, "which", _which_map({"java": "/usr/bin/java"}))
        monkeypatch.setattr(doctor, "_java_major_version", major_of)
        assert doctor._nextflow_java_check() is None  # JAVA_HOME's 17 decides, not the PATH's 11
        monkeypatch.setattr(doctor, "_java_major_version", lambda executable="java": 11 if str(tmp_path) in str(executable) else 17)
        # JAVA_HOME's 11 decides even though a newer java sits on the PATH: the provider takes
        # the first candidate that exists and version-checks THAT one, with no fall-through
        assert doctor._nextflow_java_check() == "java >= 17 for nextflow (found 11 via the server's resolution order)"

        monkeypatch.delenv("JAVA_HOME")
        monkeypatch.setattr(doctor, "_java_major_version", lambda executable="java": 11)
        assert doctor._nextflow_java_check() == "java >= 17 for nextflow (found 11 via the server's resolution order)"

    def test_a_runtime_only_dotnet_does_not_satisfy_an_sdk_minimum(self, doctor, monkeypatch) -> None:
        """Given a machine with a satisfying runtime but no SDK, the verdict names the
        missing SDK — a runtime alone cannot load the SDK-style test project; given SDK 8
        alongside, nothing is unmet.
        """
        monkeypatch.setattr(doctor.shutil, "which", _which_map({"dotnet": "/usr/bin/dotnet"}))
        requirement = doctor.ToolchainRequirement(("csharp",), ("dotnet",), "note", min_dotnet_runtime=10, min_dotnet_sdk=8)
        monkeypatch.setattr(doctor, "_dotnet_runtime_majors", lambda: {10})
        monkeypatch.setattr(doctor, "_dotnet_sdk_majors", lambda: None)
        assert requirement.unsatisfied() == [
            "dotnet SDK >= 8 (no installed SDK could be determined — a runtime alone cannot load projects)"
        ]
        monkeypatch.setattr(doctor, "_dotnet_sdk_majors", lambda: {8})
        assert requirement.unsatisfied() == []

    def test_an_undeterminable_version_is_reported_as_such_not_as_satisfied(self, doctor, monkeypatch) -> None:
        """Given java present but its version unreadable, when the requirement declares a
        minimum, then the verdict says so — presence alone never satisfies a version gate.
        """
        monkeypatch.setattr(doctor.shutil, "which", _which_map({"java": "/usr/bin/java"}))
        monkeypatch.setattr(doctor, "_java_major_version", lambda: None)
        requirement = doctor.ToolchainRequirement(("java",), ("java",), "note", min_java=21)
        assert requirement.unsatisfied() == ["java >= 21 (the installed version could not be determined)"]

    def test_a_failing_availability_predicate_is_named_in_the_verdict(self, doctor, monkeypatch) -> None:
        """Given a requirement whose conftest-mirroring predicate reports something missing,
        when the requirement is evaluated, then the verdict carries that description.
        """
        monkeypatch.setattr(doctor.shutil, "which", _which_map({"R": "/usr/bin/R"}))
        requirement = doctor.ToolchainRequirement(("r",), ("R",), "note", extra_check=lambda: "the R package 'languageserver'")
        assert requirement.unsatisfied() == ["the R package 'languageserver'"]

    def test_the_availability_predicate_is_skipped_while_commands_are_already_missing(self, doctor, monkeypatch) -> None:
        """Given a requirement whose executable is absent, when it is evaluated, then the
        verdict names the executable and the (possibly expensive) predicate never runs.
        """
        monkeypatch.setattr(doctor.shutil, "which", _which_map({}))
        ran = []
        requirement = doctor.ToolchainRequirement(("r",), ("R",), "note", extra_check=lambda: ran.append(1) or "unreachable")
        assert requirement.unsatisfied() == ["R"]
        assert ran == []


class TestVersionProbes:
    """The version probes read the output shapes real tools print."""

    @pytest.mark.parametrize(
        ("stderr", "expected"),
        [
            ('openjdk version "21.0.2" 2024-01-16', 21),
            ('java version "1.8.0_402"', 8),
            ("nothing that looks like a version", None),
        ],
    )
    def test_java_version_output_shapes(self, doctor, monkeypatch, stderr: str, expected: int | None) -> None:
        """Given the version banners modern and 1.x-era JVMs print (on stderr), the probe
        reads the major version, or None when there is none to read.
        """
        monkeypatch.setattr(doctor.subprocess, "run", lambda argv, **kwargs: subprocess.CompletedProcess(argv, 0, stdout="", stderr=stderr))
        assert doctor._java_major_version() == expected

    @pytest.mark.parametrize(
        ("stdout", "expected"),
        [
            ("PHP 8.3.6 (cli) (built: Jan 01 2026)", (8, 3)),
            ("PHP 7.4.33 (cli)", (7, 4)),
            ("no php here", None),
        ],
    )
    def test_php_version_output_shapes(self, doctor, monkeypatch, stdout: str, expected: tuple[int, int] | None) -> None:
        """Given php --version's banner, the probe reads (major, minor)."""
        monkeypatch.setattr(doctor.subprocess, "run", lambda argv, **kwargs: subprocess.CompletedProcess(argv, 0, stdout=stdout, stderr=""))
        assert doctor._php_version() == expected

    def test_dotnet_runtimes_are_read_from_netcore_lines_only(self, doctor, monkeypatch) -> None:
        """Given dotnet --list-runtimes output carrying both NETCore and AspNetCore lines,
        the probe collects the NETCore majors only.
        """
        listing = (
            "Microsoft.AspNetCore.App 8.0.16 [/usr/share/dotnet]\n"
            "Microsoft.NETCore.App 8.0.16 [/usr/share/dotnet]\n"
            "Microsoft.NETCore.App 10.0.0 [/usr/share/dotnet]\n"
        )
        monkeypatch.setattr(
            doctor.subprocess, "run", lambda argv, **kwargs: subprocess.CompletedProcess(argv, 0, stdout=listing, stderr="")
        )
        assert doctor._dotnet_runtime_majors() == {8, 10}

    def test_dotnet_sdk_majors_are_read_one_per_line(self, doctor, monkeypatch) -> None:
        """Given dotnet --list-sdks output, the probe collects the SDK majors; given no
        output (a runtime-only installation), it reports None rather than an empty set.
        """
        listing = "8.0.412 [/usr/lib/dotnet/sdk]\n10.0.100 [/usr/lib/dotnet/sdk]\n"
        monkeypatch.setattr(
            doctor.subprocess, "run", lambda argv, **kwargs: subprocess.CompletedProcess(argv, 0, stdout=listing, stderr="")
        )
        assert doctor._dotnet_sdk_majors() == {8, 10}
        monkeypatch.setattr(doctor.subprocess, "run", lambda argv, **kwargs: subprocess.CompletedProcess(argv, 0, stdout="", stderr=""))
        assert doctor._dotnet_sdk_majors() is None


class TestCoreEnvironment:
    """The core checks decide the exit code, so what they accept has to be exact."""

    def test_bounds_are_checked_and_unknown_constraints_are_reported_not_assumed(self, doctor) -> None:
        """Given a specifier this script fully understands, the verdict is the bounds check;
        given one carrying an exclusion it cannot parse, the constraint comes back named —
        silently treating it as satisfied would clear an interpreter the project excludes.
        """
        current = ".".join(str(c) for c in sys.version_info[:2])
        assert doctor._python_version_in_range(">=3.11, <3.15") == (True, [])
        assert doctor._python_version_in_range(f">={current}") == (True, [])
        assert doctor._python_version_in_range(">=99.0")[0] is False
        assert doctor._python_version_in_range(f">=3.11, !={current}.*") == (True, [f"!={current}.*"])

    def test_the_exit_code_follows_the_core_checks_only(self, doctor, monkeypatch, capsys) -> None:
        """Given the core checks fail, main exits 1; given they pass, main exits 0 even when
        toolchains are missing — a missing compiler is information, not a failed environment.
        """
        monkeypatch.setattr(doctor.sys, "argv", ["check_dev_env.py"])
        monkeypatch.setattr(doctor, "_check_install_skew", lambda pyproject: None)
        monkeypatch.setattr(doctor, "_report_toolchains", lambda markers, evaluated: [])
        monkeypatch.setattr(doctor, "_check_core_environment", lambda pyproject: False)
        assert doctor.main() == 1
        monkeypatch.setattr(doctor, "_check_core_environment", lambda pyproject: True)
        assert doctor.main() == 0
        assert "none —" in capsys.readouterr().out


class TestMarkersExpression:
    """--markers composes into `pytest -m "<expr>"`, so what it prints has to be safe there."""

    def test_no_runnable_markers_prints_nothing_and_fails(self, doctor, monkeypatch, capsys) -> None:
        """Given a machine where no marker is runnable, when --markers is asked for the
        expression, then stdout stays empty and the exit code is nonzero — printing an empty
        expression would be read by pytest as 'no filter' and run the entire suite, the exact
        opposite of what the machine can do.
        """
        monkeypatch.setattr(doctor.sys, "argv", ["check_dev_env.py", "--markers"])
        monkeypatch.setattr(doctor, "_runnable_markers", lambda markers, evaluated: [])
        assert doctor.main() == 1
        captured = capsys.readouterr()
        assert captured.out.strip() == ""
        assert "runnable" in captured.err

    def test_runnable_markers_are_printed_as_an_or_expression(self, doctor, monkeypatch, capsys) -> None:
        """Given two runnable markers, --markers prints exactly the pytest -m expression."""
        monkeypatch.setattr(doctor.sys, "argv", ["check_dev_env.py", "--markers"])
        monkeypatch.setattr(doctor, "_runnable_markers", lambda markers, evaluated: ["python", "go"])
        assert doctor.main() == 0
        assert capsys.readouterr().out.strip() == "python or go"


class TestTableIntegrity:
    """The toolchain table cannot drift from the markers pyproject registers."""

    KNOWN_UNCOVERED_MARKERS = frozenset(
        {
            # verified per server: their language servers are installed or bundled by Serena
            # itself (cue/ada/al/luau download pinned releases for every platform Serena
            # runs on; marksman, texlab and taplo are downloaded binaries; fortls and
            # pyright run via uvx; msl ships a bundled server), so no local toolchain is
            # required. hlsl is NOT here: its download has a platform matrix, so it carries
            # a row of its own — a managed dependency only waives a language when it covers
            # every platform
            "ada",
            "al",
            "cue",
            "fortran",
            "latex",
            "luau",
            "markdown",
            "msl",
            "toml",
            # lua-language-server is downloaded by LuaLanguageServer itself when absent (lua_ls.py)
            "lua",
            # the managed Kotlin server ships bin/intellij-server with a bundled JBR (kotlin_language_server.py)
            "kotlin",
            # the default jdtls setup downloads the vscode-java bundle with its own JRE 21 (eclipse_jdtls.py)
            "java",
            # the language Serena itself runs on; the dev environment provides it
            "python",
        }
    )

    def test_every_marker_without_a_table_row_is_an_explicit_waiver(self, doctor) -> None:
        """Given the registered language markers and the toolchain table, every marker
        without a row is on the documented waiver list above — a newly added language
        cannot silently land in the no-requirement bucket, and a row cannot be dropped
        without the waiver saying why.
        """
        registered = doctor._language_markers(doctor._read_pyproject())
        covered = {marker for requirement in doctor.TOOLCHAIN_REQUIREMENTS for marker in requirement.markers}
        uncovered = {marker for marker in registered if marker not in covered}
        assert uncovered == self.KNOWN_UNCOVERED_MARKERS

    def test_every_marker_in_the_table_is_a_registered_language_marker(self, doctor) -> None:
        """Given the language markers registered in pyproject.toml, every marker named by
        a toolchain requirement is one of them — a removed or renamed language cannot
        leave a stale row behind unnoticed.
        """
        registered = set(doctor._language_markers(doctor._read_pyproject()))
        for requirement in doctor.TOOLCHAIN_REQUIREMENTS:
            unknown = set(requirement.markers) - registered
            assert not unknown, f"row '{requirement.note}' names unregistered markers: {sorted(unknown)}"
