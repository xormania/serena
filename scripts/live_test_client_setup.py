"""
Live breadth test for ``serena setup <client>`` against the MCP client CLIs actually installed on
this machine — the breadth counterpart of ``live_test_grok.py``, which probes a single integration
in depth. For every applicable ``ClientSetupHandler`` (claude-code, codebuddy, codex, grok), the
real registration lifecycle is exercised:

1. detect the client CLI and record its version,
2. refuse to touch a client that already has a ``serena`` MCP server registered,
3. back up the client's user-level configuration file (where its location is known),
4. run ``serena setup <client>`` — the exact code path a user runs,
5. verify the registration actually landed and carries the expected server command,
6. remove the registration again and verify the client is back at its baseline,
   restoring the backed-up configuration if it is not.

Safety properties (mirroring ``live_test_grok.py``):

* **Zero inference cost.** No client session is ever started; only registration management
  commands run.
* **State-preserving.** Every add is paired with a removal, the baseline is verified at the end,
  and a client that already has a ``serena`` registration is skipped, never touched. If a probe
  aborts after mutating, removal and configuration restore are attempted before the script exits.
* **Credential-safe.** Configuration backups (which may carry tokens) are written 0600 inside a
  fresh private 0700 directory and deleted once the baseline is confirmed intact; they are kept
  only when a probe fails, and the report then points to them. Restored configuration files keep
  their pre-probe permissions.

With ``--record <dir>``, each probe additionally writes a JSON snapshot of the client's observable
command surface (CLI version, every command executed with its exit code and output) — a re-runnable
record of how the client behaves *today*, suitable for diffing across client releases, e.g. from a
scheduled CI job. Snapshots contain command transcripts, which can include the registration lines
of other configured MCP servers — review them before committing or sharing.

Usage::

    uv run python scripts/live_test_client_setup.py                 # probe all detected clients
    uv run python scripts/live_test_client_setup.py --client codex  # probe a single client
    uv run python scripts/live_test_client_setup.py --list          # only show which clients are detected
    uv run python scripts/live_test_client_setup.py --record out/   # additionally write JSON snapshots

Run it via ``uv run`` so that the ``serena`` executable under test is the one from this checkout.

Exit code: 1 if any probed client failed, 0 otherwise (skipped and undetected clients do not fail).
"""

import argparse
import json
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

from serena.config.client_setup import ClientSetupHandler, client_setup_handlers

COMMAND_TIMEOUT_SECONDS = 120


def _kill_process_tree(process: subprocess.Popen) -> None:
    """
    :param process: a child started with its own session (POSIX); its whole process tree is
        terminated -- setup shells out to the client CLI, and a surviving descendant could
        write its registration after the rollback has run
    """
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        # Windows has no process groups to signal; taskkill /T walks the descendant tree
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], check=False, capture_output=True)
        process.kill()


def _drain(process: subprocess.Popen, timeout: int = 5) -> None:
    """
    :param process: an already-killed child whose pipes are being closed
    :param timeout: seconds to wait for EOF before giving up

    Reaps the child without waiting forever. ``communicate()`` returns only at EOF on every
    pipe, and EOF needs every inherited write end closed -- a grandchild that called
    ``setsid`` itself escapes the process-group kill and can hold them open indefinitely,
    which would wedge the probe after it has already mutated the client.
    """
    try:
        process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        pass


def _install_unwinding_signal_handlers() -> None:
    """
    Makes SIGTERM and SIGHUP unwind instead of killing the process outright.

    Python's default disposition for both terminates without raising, so no ``finally``
    runs: closing the terminal mid-probe would skip the rollback, leave the client
    registered and leave a credential-bearing backup in a temp directory the user was never
    told about. Raising ``SystemExit`` puts them on the same footing as Ctrl-C.
    """

    def unwind(signum: int, _frame: object) -> None:
        raise SystemExit(f"terminated by signal {signum}")

    for name in ("SIGTERM", "SIGHUP"):
        signum = getattr(signal, name, None)
        if signum is not None:
            try:
                signal.signal(signum, unwind)
            except (OSError, ValueError):  # not the main thread, or unsupported here
                pass


"""generous per-command cap; `mcp list` implementations may health-check the registered servers"""


@dataclass(frozen=True)
class ClientProbeSpec:
    """Client-specific knowledge for the registration lifecycle: how to list and remove MCP server
    registrations, and where the user-level configuration file lives.
    """

    list_argv: tuple[str, ...]
    """the command that lists the registered MCP servers"""
    remove_argv: tuple[str, ...]
    """the command that removes the ``serena`` MCP server registration"""
    user_config_path: Path | None = None
    """the user-level configuration file mutated by add/remove, or None if unknown
    (baseline verification then relies on the registration list only)"""


def client_probe_specs() -> dict[str, ClientProbeSpec]:
    """
    :return: the per-client lifecycle knowledge, built at call time so that ``Path.home()``
        reflects the current environment rather than the one at import
    """
    return {
        "claude-code": ClientProbeSpec(
            ("claude", "mcp", "list"),
            ("claude", "mcp", "remove", "--scope", "user", "serena"),
            # claude keeps .claude.json under CLAUDE_CONFIG_DIR when set (verified live:
            # CLAUDE_CONFIG_DIR=<tmp> claude mcp list creates <tmp>/.claude.json) -- backing
            # up the home-directory path would guard a file the client never touches
            Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home()) / ".claude.json",
        ),
        # untested mirror of claude-code (CodeBuddy's setup handler is command-compatible)
        "codebuddy": ClientProbeSpec(
            ("codebuddy", "mcp", "list"),
            ("codebuddy", "mcp", "remove", "--scope", "user", "serena"),
        ),
        "codex": ClientProbeSpec(
            ("codex", "mcp", "list"),
            ("codex", "mcp", "remove", "serena"),
            # codex resolves its home from CODEX_HOME when set (verified live: codex names
            # the override as its codex_home and lists from there; `codex mcp add` writes
            # $CODEX_HOME/config.toml). serena's handler shells out to the codex CLI, so
            # the CLI's resolution is the one that counts
            Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex") / "config.toml",
        ),
        "grok": ClientProbeSpec(
            ("grok", "mcp", "list"),
            ("grok", "mcp", "remove", "--scope", "user", "serena"),
            Path.home() / ".grok" / "config.toml",
        ),
    }


class Status(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    NOT_DETECTED = "NOT DETECTED"


@dataclass
class ExecutedCommand:
    """The observable outcome of one command executed against a client (or the serena CLI)."""

    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

    def as_dict(self) -> dict:
        return {"argv": list(self.argv), "returncode": self.returncode, "stdout": self.stdout, "stderr": self.stderr}


@dataclass
class ProbeResult:
    """The outcome of probing one client's registration lifecycle."""

    client: str
    status: Status
    detail: str
    cli_version: str | None = None
    notes: list[str] = field(default_factory=list)
    transcript: list[ExecutedCommand] = field(default_factory=list)


class ClientProbe:
    """Exercises the full ``serena setup`` registration lifecycle against one installed client,
    leaving the client exactly as it was found.
    """

    def __init__(self, handler: ClientSetupHandler, spec: ClientProbeSpec, serena_executable: Path, backup_dir: Path) -> None:
        self.handler = handler
        self.spec = spec
        self.serena_executable = serena_executable
        self.backup_dir = backup_dir
        self._transcript: list[ExecutedCommand] = []
        self._notes: list[str] = []
        self._backup_path: Path | None = None
        self._config_existed = False
        self._config_mode: int | None = None
        self._config_restore_path: Path | None = None
        self._config_was_symlink = False
        self._config_link_target: str | None = None
        self._config_hardlinked = False

    def _run(self, argv: tuple[str, ...]) -> ExecutedCommand:
        # execute, record in the transcript, and echo for the live reader. On POSIX the child
        # gets its own process group so a timeout can terminate the WHOLE tree: setup shells
        # out to the client CLI, and an orphaned grandchild finishing its registration AFTER
        # the rollback would silently undo the cleanup.
        print(f"    $ {' '.join(argv)}", flush=True)
        try:
            with subprocess.Popen(
                argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=(os.name == "posix")
            ) as process:
                try:
                    stdout, stderr = process.communicate(timeout=COMMAND_TIMEOUT_SECONDS)
                    executed = ExecutedCommand(argv, process.returncode, stdout, stderr)
                except subprocess.TimeoutExpired:
                    _kill_process_tree(process)
                    _drain(process)
                    executed = ExecutedCommand(argv, -1, "", f"timed out after {COMMAND_TIMEOUT_SECONDS}s; the process tree was terminated")
                except BaseException:
                    # a Ctrl-C reaches this process but NOT the detached child (own session),
                    # and the Popen context manager would then wait on it without any timeout,
                    # keeping the emergency restore from ever running -- kill the tree, reap,
                    # and let the interrupt continue unwinding
                    _kill_process_tree(process)
                    _drain(process)
                    raise
        except OSError as e:
            executed = ExecutedCommand(argv, -1, "", str(e))
        self._transcript.append(executed)
        return executed

    @staticmethod
    def _serena_registered(list_output: str) -> bool:
        """
        :param list_output: the stdout of the client's list command
        :return: whether a ``serena`` MCP server registration appears in it
        """
        return re.search(r"^\s*serena\b", list_output, re.MULTILINE) is not None

    @staticmethod
    def _serena_row(list_output: str) -> str:
        """
        :param list_output: the stdout of the client's list command
        :return: the lines of the output that belong to the ``serena`` registration
        """
        return "\n".join(line for line in list_output.splitlines() if re.match(r"\s*serena\b", line))

    @staticmethod
    def _registration_records(list_output: str) -> set[str]:
        """
        :param list_output: the stdout of the client's list command
        :return: the whitespace-normalized nonempty lines — full registration records, so that a
            rewritten command on another server's row is a difference, not only a lost name
            (header lines cancel out when two outputs of the same client are compared)
        """
        return {" ".join(line.split()) for line in list_output.splitlines() if line.strip()}

    def _backup_config(self) -> None:
        # snapshot the user-level config file (0600, inside the private backup dir) before mutating
        config_path = self.spec.user_config_path
        if config_path is None:
            self._notes.append("no known user-config path for this client; baseline is verified via the registration list only")
            return
        # a DANGLING symlink is not a file, but it is still the user's link: record its shape
        # first, so cleanup removes what setup created through it and never the link itself
        self._config_was_symlink = config_path.is_symlink()
        if self._config_was_symlink:
            self._config_link_target = os.readlink(config_path)
        self._config_existed = config_path.is_file()
        if not self._config_existed:
            self._notes.append(
                f"{config_path} was a dangling symlink before the probe"
                if self._config_was_symlink
                else f"{config_path} did not exist before the probe"
            )
            return
        config_stat = config_path.stat()
        self._config_mode = stat.S_IMODE(config_stat.st_mode)
        # a hardlinked config (dotfile managers use them) must be restored THROUGH its inode:
        # os.replace would install a new one, leaving the twin permanently carrying whatever
        # the client wrote while the probed path looked pristine
        self._config_hardlinked = config_stat.st_nlink > 1
        # restores must write through a symlinked config (dotfile trees), never replace the
        # link itself with a regular file -- so the restore target is resolved NOW, and the
        # link's shape and literal target are recorded so a client that atomically replaces
        # the link with a regular file can be undone too
        self._config_restore_path = config_path.resolve()
        self._backup_path = self.backup_dir / f"{self.handler.name}-{config_path.name}"
        self._backup_path.write_bytes(config_path.read_bytes())
        self._backup_path.chmod(stat.S_IRUSR | stat.S_IWUSR)

    def _remove_config_created_by_probe(self) -> None:
        # delete what the probe's setup call created (the baseline had no config file)
        config_path = self.spec.user_config_path
        if config_path is None or self._config_existed:
            return
        if self._config_was_symlink:
            # the baseline was a DANGLING link. Two client behaviours to undo, and the link
            # must survive both: a write-through created the target, or an atomic-rename
            # writer replaced the link itself with a regular file
            if not config_path.is_symlink():
                if config_path.exists():
                    config_path.unlink()
                assert self._config_link_target is not None
                config_path.symlink_to(self._config_link_target)
                self._notes.append(f"the client replaced the dangling symlink at {config_path} with a file; the link was recreated")
                return
            target = config_path.resolve()
            if target.is_file():
                target.unlink()
                self._notes.append(f"removed {target}, created through the pre-existing symlink at {config_path}")
            return
        if config_path.is_file():
            config_path.unlink()
            self._notes.append(f"removed {config_path}, which the probe had created")

    def _restore_config_bytes(self) -> None:
        # restore the backup atomically, owner-only from the first byte: recreating a deleted
        # config with write_bytes would land at the process umask -- credentials readable by
        # other users until a later chmod. mkstemp starts 0600; the pre-probe mode goes onto
        # the temp file BEFORE it atomically replaces the config, so no wider-than-intended
        # window ever exists and an interruption leaves only a 0600 temp file behind.
        assert self._backup_path is not None and self.spec.user_config_path is not None
        config_path = self.spec.user_config_path
        if self._config_was_symlink and not config_path.is_symlink():
            # the client replaced the symlink with a regular file (atomic-rename writers do);
            # remove the impostor and recreate the recorded link, preserving a relative target
            if config_path.exists() or config_path.is_symlink():
                config_path.unlink()
            assert self._config_link_target is not None
            config_path.symlink_to(self._config_link_target)
            self._notes.append("the client replaced the config symlink with a regular file; the link was recreated")
        # the resolved target recorded at backup time: replacing the config PATH would clobber
        # a symlinked dotfile with a regular file
        restore_path = self._config_restore_path or self.spec.user_config_path
        if self._config_hardlinked:
            # write THROUGH the inode: os.replace would install a new one and leave the
            # hardlinked twin holding whatever the client wrote. Atomicity is traded for
            # link preservation here, and the backup survives a failure mid-write
            fd = os.open(restore_path, os.O_WRONLY | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0))
            with os.fdopen(fd, "wb") as config_file:
                config_file.write(self._backup_path.read_bytes())
            if self._config_mode is not None:
                os.chmod(restore_path, self._config_mode)
            self._notes.append("the config is hardlinked; it was restored through its inode so the other name keeps the baseline")
            return
        fd, temp_name = tempfile.mkstemp(dir=str(restore_path.parent), prefix=f".{restore_path.name}.")
        try:
            with os.fdopen(fd, "wb") as temp_file:
                temp_file.write(self._backup_path.read_bytes())
            if self._config_mode is not None:
                os.chmod(temp_name, self._config_mode)
            os.replace(temp_name, restore_path)
        except BaseException:
            try:
                os.unlink(temp_name)
            except OSError:
                pass
            raise

    def _verify_config_baseline(self) -> None:
        # after a clean lifecycle, ensure the config file is back at its pre-probe state
        config_path = self.spec.user_config_path
        if config_path is None:
            return
        if not self._config_existed:
            self._remove_config_created_by_probe()
            return
        assert self._backup_path is not None
        bytes_intact = config_path.is_file() and config_path.read_bytes() == self._backup_path.read_bytes()
        # identical bytes are not enough: a client that rewrites configs by atomic rename
        # replaces a symlinked config with a regular file while preserving every byte
        link_shape_intact = not self._config_was_symlink or config_path.is_symlink()
        if bytes_intact and link_shape_intact:
            self._notes.append("user config is byte-identical to the baseline")
        else:
            if not bytes_intact:
                # boundary: on opaque bytes the client's own rewrite and a concurrent edit by
                # another process are indistinguishable; the byte-restore contract wins, and the
                # note DISCLOSES that concurrent changes (if any) were rolled back with it
                self._notes.append(
                    "user config restored from backup: its bytes changed during the probe. A client rewrite and a"
                    " concurrent edit by another process look the same, so any concurrent change was rolled back"
                    " too -- avoid editing client configs while the probe runs"
                )
            self._restore_config_bytes()
        if self._config_mode is not None and stat.S_IMODE(config_path.stat().st_mode) != self._config_mode:
            config_path.chmod(self._config_mode)
            self._notes.append("user config permissions restored to the pre-probe mode")
        self._backup_path.unlink()
        self._backup_path = None

    def _emergency_restore(self) -> None:
        # best-effort rollback for a probe that failed after mutating the client -- and
        # best-effort means it may not raise: this runs from a finally, so an exception here
        # would discard the in-flight verdict (its detail, notes and transcript), abandon the
        # remaining clients, and tell the user about the restore instead of the failure
        try:
            self._run(self.spec.remove_argv)
            if self._backup_path is not None and self.spec.user_config_path is not None:
                self._restore_config_bytes()
                self._notes.append(f"user config restored from backup after failure; backup kept at {self._backup_path}")
            else:
                self._remove_config_created_by_probe()
        except Exception as e:
            self._notes.append(f"EMERGENCY RESTORE FAILED ({e}) — the client may still be mutated; backup kept at {self._backup_path}")
            print(f"    !! emergency restore failed: {e}", flush=True)
            print(f"    !! the client may still carry a serena registration; backup kept at {self._backup_path}", flush=True)

    def _result(self, status: Status, detail: str, cli_version: str | None = None) -> ProbeResult:
        return ProbeResult(self.handler.name, status, detail, cli_version, self._notes, self._transcript)

    def run(self) -> ProbeResult:
        """
        :return: the outcome of the full add/verify/remove/verify lifecycle for this client
        """
        # detection, via the same predicate `serena setup` uses
        if not self.handler.is_applicable():
            return self._result(Status.NOT_DETECTED, "client CLI not found or not functional")
        version_command = self._run((self.spec.list_argv[0], "--version"))
        cli_version = version_command.stdout.strip() or None

        # baseline: never touch a client that already has a serena registration
        baseline = self._run(self.spec.list_argv)
        if baseline.returncode != 0:
            return self._result(
                Status.SKIP, f"cannot query registrations ({' '.join(self.spec.list_argv)} exited {baseline.returncode})", cli_version
            )
        if self._serena_registered(baseline.stdout):
            return self._result(Status.SKIP, "a serena MCP server is already registered — refusing to touch a live setup", cli_version)

        self._backup_config()
        mutated = False
        try:
            # arm the rollback BEFORE the mutating command runs: an interrupt mid-setup may
            # arrive after the registration was already written, and the finally below must
            # then restore -- arming afterwards would skip it
            mutated = True
            # the real user-facing path: serena setup <client>
            setup = self._run((str(self.serena_executable), "setup", self.handler.name))
            if setup.returncode != 0:
                return self._result(Status.FAIL, f"serena setup {self.handler.name} exited {setup.returncode}", cli_version)

            # prove the registration actually landed before trusting anything downstream
            after_add = self._run(self.spec.list_argv)
            if after_add.returncode != 0:
                return self._result(
                    Status.FAIL,
                    f"cannot verify the registration landed ({' '.join(self.spec.list_argv)} exited {after_add.returncode})",
                    cli_version,
                )
            if not self._serena_registered(after_add.stdout):
                return self._result(Status.FAIL, "serena setup succeeded but no registration is visible in the client", cli_version)
            expected_command = self.handler.get_mcp_server_command()
            serena_row = self._serena_row(after_add.stdout)
            # token boundaries on BOTH branches: a bare substring test would let a row carrying
            # ``--context=x-extra`` satisfy an expected ``--context=x``
            if f" {expected_command} " in f" {serena_row} ":
                self._notes.append(f"registration carries the expected command: {expected_command}")
            elif "start-mcp-server" in serena_row:
                # the client echoes command text, but possibly reformatted (codex renders columns), so
                # verify token by token within the serena row -- whole tokens, not substrings, or
                # ``--context=x`` would be satisfied by a row carrying ``--context=x-extra``. Boundary:
                # an executable swapped while the row keeps its ``serena`` name would still match; exact
                # command-field parsing is the deep single-client instrument's job (live_test_grok.py).
                row_tokens = set(serena_row.split())
                missing_parts = [part for part in expected_command.split() if part not in row_tokens]
                if missing_parts:
                    return self._result(
                        Status.FAIL, f"the registered command lacks expected parts: {', '.join(missing_parts)}", cli_version
                    )
                self._notes.append(f"registration carries the expected command (reformatted by the client): {expected_command}")
            else:
                self._notes.append("registration present; the client's list output does not expose command text")

            # revert, and prove the reversion landed too
            removal = self._run(self.spec.remove_argv)
            if removal.returncode != 0:
                return self._result(
                    Status.FAIL, f"removal exited {removal.returncode} — a serena registration may be left behind", cli_version
                )
            final = self._run(self.spec.list_argv)
            if final.returncode != 0:
                return self._result(
                    Status.FAIL, f"cannot verify the removal ({' '.join(self.spec.list_argv)} exited {final.returncode})", cli_version
                )
            if self._serena_registered(final.stdout):
                return self._result(Status.FAIL, "serena is still registered after removal", cli_version)
            if self.spec.user_config_path is None:
                # no config file to byte-compare, so the registration list is the only baseline:
                # every record present before the probe must still be present, unchanged, and none added
                if self._registration_records(final.stdout) != self._registration_records(baseline.stdout):
                    return self._result(
                        Status.FAIL, "the registration set differs from the baseline — another server's entry changed", cli_version
                    )
                self._notes.append("registration set matches the baseline")
            # the baseline must be restored and CONFIRMED before the rollback is disarmed:
            # a client reserialization plus an interrupt in between would otherwise leave the
            # rewritten bytes in place with the finally already skipping the restore
            self._verify_config_baseline()
            mutated = False
        finally:
            if mutated:
                self._emergency_restore()

        return self._result(Status.PASS, "add/verify/remove lifecycle completed; baseline confirmed", cli_version)


def _write_snapshot(record_dir: Path, result: ProbeResult) -> Path:
    """
    :param record_dir: the directory to write the snapshot into
    :param result: the probe result to snapshot
    :return: the path of the written snapshot
    """
    snapshot = {
        "client": result.client,
        "recorded_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "cli_version": result.cli_version,
        "status": result.status.value,
        "detail": result.detail,
        "notes": result.notes,
        "transcript": [executed.as_dict() for executed in result.transcript],
    }
    snapshot_path = record_dir / f"{result.client}.json"
    # transcripts echo other servers' registration lines, which can carry credentials in
    # commands or env values -- owner-only from the first byte, not chmod'd after the
    # content already sits readable; fchmod covers a leftover file from an earlier run,
    # whose looser mode O_CREAT would not correct
    # O_NOFOLLOW: following a pre-existing symlink here would truncate and chmod whatever
    # it points at -- arbitrary file destruction when recording into a shared directory
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(snapshot_path, flags, stat.S_IRUSR | stat.S_IWUSR)
    except OSError as e:
        if snapshot_path.is_symlink():
            raise RuntimeError(f"refusing to write through a pre-existing symlink at {snapshot_path}") from e
        raise
    if hasattr(os, "fchmod"):
        os.fchmod(fd, stat.S_IRUSR | stat.S_IWUSR)
    with os.fdopen(fd, "w", encoding="utf-8") as snapshot_file:
        snapshot_file.write(json.dumps(snapshot, indent=2) + "\n")
    return snapshot_path


def main() -> int:
    _install_unwinding_signal_handlers()
    specs = client_probe_specs()
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--client", choices=sorted(specs), help="probe only this client")
    parser.add_argument("--list", action="store_true", help="only report which client CLIs are detected; do not probe")
    parser.add_argument("--record", metavar="DIR", help="write a JSON snapshot of each probed client's command surface into DIR")
    args = parser.parse_args()

    handlers = [h for h in client_setup_handlers if args.client is None or h.name == args.client]

    if args.list:
        for handler in handlers:
            print(f"  {handler.name:<12} {'detected' if handler.is_applicable() else '-'}")
        return 0

    serena_executable = shutil.which("serena")
    if serena_executable is None:
        print("No serena executable on the PATH; run this script via `uv run` from the repository root.")
        return 2
    print(f"serena executable under test: {serena_executable}")

    record_dir: Path | None = None
    if args.record is not None:
        record_dir = Path(args.record)
        record_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        # O_NOFOLLOW on the snapshot guards only the final component: a pre-existing record
        # directory that is itself a symlink (mkdir(exist_ok=True) accepts one) would
        # redirect every write, and one owned by another user is theirs to swap at will
        if record_dir.is_symlink():
            print(f"--record must not be a symlink: {record_dir}", file=sys.stderr)
            return 2
        if os.name == "posix" and record_dir.stat().st_uid != os.getuid():
            print(f"--record directory is owned by another user: {record_dir}", file=sys.stderr)
            return 2

    # one private 0700 directory holds all config backups for this run
    backup_dir = Path(tempfile.mkdtemp(prefix="serena-client-probe-"))

    results = []
    try:
        for handler in handlers:
            print(f"\n== {handler.name}")
            probe = ClientProbe(handler, specs[handler.name], Path(serena_executable), backup_dir)
            result = probe.run()
            results.append(result)
            print(f"  {result.status.value}: {result.detail}")
            if result.cli_version is not None:
                print(f"    client version: {result.cli_version}")
            for note in result.notes:
                print(f"    note: {note}")
            if record_dir is not None:
                print(f"    snapshot: {_write_snapshot(record_dir, result)}")
    finally:
        # ALWAYS dispose of the backup directory, interrupt included: emergency restore
        # retains credential-bearing backups, and an exception between backup and summary
        # must not leave a secret copy in a temp dir the user was never told about
        if not any(backup_dir.iterdir()):
            backup_dir.rmdir()
        else:
            print(f"\nBackups kept at {backup_dir} (a probe failed or restored state); review and delete manually.")

    print("\nSummary:")
    for result in results:
        print(f"  {result.client:<12} {result.status.value}")
    return 1 if any(result.status == Status.FAIL for result in results) else 0


if __name__ == "__main__":
    sys.exit(main())
