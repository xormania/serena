#!/usr/bin/env python3
"""
Live breadth test for ``serena setup <client>`` against the MCP client CLIs actually installed on
this machine — the breadth counterpart of ``live_test_grok.py``, which probes a single integration
in depth. For every applicable ``ClientSetupHandler`` (claude-code, codebuddy, codex, grok), the
real registration lifecycle is exercised:

1. detect the client CLI and record its version,
2. back up the client's user-level configuration file (where its location is known), before any
   client command runs — a command that merely lists registrations can create the file it reads,
3. refuse to touch a client that already has a ``serena`` MCP server registered, or whose config
   is hardlinked (no restore of one can avoid either detaching its twin or truncating both),
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

Usage::

    uv run python scripts/live_test_client_setup.py                 # probe all detected clients
    uv run python scripts/live_test_client_setup.py --client codex  # probe a single client
    uv run python scripts/live_test_client_setup.py --list          # only show which clients are detected

Run it via ``uv run`` so that the ``serena`` executable under test is the one from this checkout.

Exit code: 1 if any probed client failed, 0 otherwise (skipped and undetected clients do not fail).
"""

import argparse
import contextlib
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import threading
from collections.abc import Iterator
from dataclasses import dataclass, field
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


@contextlib.contextmanager
def _uninterruptible_cleanup() -> Iterator[None]:
    """
    Holds SIGTERM/SIGHUP for the duration of a kill-and-reap sequence.

    Making those signals unwind gave them a new place to land: arriving midway through the
    cleanup, the SystemExit escapes into ``Popen.__exit__``, whose ``wait()`` has no timeout
    and is being asked about a child that has just proved it hangs. Deferring delivery until
    the child is dead keeps the cleanup that protects the rollback from being preempted by a
    second unwind.
    """
    if not hasattr(signal, "pthread_sigmask"):
        yield
        return
    blocked = {
        s for s in (getattr(signal, "SIGTERM", None), getattr(signal, "SIGHUP", None), getattr(signal, "SIGINT", None)) if s is not None
    }
    previous = signal.pthread_sigmask(signal.SIG_BLOCK, blocked)
    try:
        yield
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, previous)


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


def _is_applicable_within_timeout(handler: ClientSetupHandler, timeout: int | None = None) -> bool | None:
    """
    :param handler: the client setup handler whose detection predicate to evaluate
    :param timeout: seconds to allow the predicate; the module's command timeout by default,
        read HERE rather than bound as a default argument, which would freeze it at import
    :return: what the predicate answered, or None if it did not answer in time

    ``is_applicable`` shells out through ``execute_shell_command``, which waits without a
    timeout -- so a client CLI that hangs in its own version probe would hang this script
    before the bounded runner ever gets a turn. The predicate is upstream's and stays
    authoritative; it is merely given a deadline, on a daemon thread so an unresponsive
    client cannot keep the interpreter alive either.
    """
    answer: list[bool] = []

    def evaluate() -> None:
        with contextlib.suppress(Exception):
            answer.append(handler.is_applicable())

    thread = threading.Thread(target=evaluate, daemon=True)
    thread.start()
    thread.join(COMMAND_TIMEOUT_SECONDS if timeout is None else timeout)
    return answer[0] if answer else None


def _install_unwinding_signal_handlers() -> None:
    """
    Makes SIGTERM and SIGHUP unwind instead of killing the process outright.

    Python's default disposition for both terminates without raising, so no ``finally``
    runs: closing the terminal mid-probe would skip the rollback, leave the client
    registered and leave a credential-bearing backup in a temp directory the user was never
    told about. Raising ``SystemExit`` puts them on the same footing as Ctrl-C.

    An inherited ``SIG_IGN`` is left alone: ``nohup``-style launchers ignore SIGHUP on
    purpose so a detached run survives the terminal closing, and overriding that would abort
    exactly the unattended runs this script documents.
    """

    def unwind(signum: int, _frame: object) -> None:
        raise SystemExit(f"terminated by signal {signum}")

    for name in ("SIGTERM", "SIGHUP"):
        signum = getattr(signal, name, None)
        if signum is None:
            continue
        try:
            if signal.getsignal(signum) is signal.SIG_IGN:
                continue
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
            # claude keeps .claude.json under CLAUDE_CONFIG_DIR when set; the home-directory
            # path would guard a file the client never touches
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
            # the codex CLI resolves its home from CODEX_HOME, and serena shells out to that CLI
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

    def _run(self, argv: tuple[str, ...]) -> ExecutedCommand:
        # execute, record in the transcript, and echo for the live reader. On POSIX the child gets
        # its own process group so a timeout kills the WHOLE tree: an orphaned grandchild
        # finishing its registration after the rollback would silently undo it
        print(f"    $ {' '.join(argv)}", flush=True)
        try:
            with subprocess.Popen(
                argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=(os.name == "posix")
            ) as process:
                try:
                    stdout, stderr = process.communicate(timeout=COMMAND_TIMEOUT_SECONDS)
                    executed = ExecutedCommand(argv, process.returncode, stdout, stderr)
                except subprocess.TimeoutExpired:
                    with _uninterruptible_cleanup():
                        _kill_process_tree(process)
                        _drain(process)
                    executed = ExecutedCommand(argv, -1, "", f"timed out after {COMMAND_TIMEOUT_SECONDS}s; the process tree was terminated")
                except BaseException:
                    # a Ctrl-C reaches this process but NOT the detached child, and Popen would
                    # then wait on it untimed: kill the tree and reap, then keep unwinding
                    with _uninterruptible_cleanup():
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
        """Records everything about the config that a restore will need to put back.

        Called BEFORE the first client command, because a mere registration query can create a
        config (verified live: ``CLAUDE_CONFIG_DIR=<tmp> claude mcp list`` creates
        ``<tmp>/.claude.json``). Deciding afterwards what the user had would record the probe's
        own side effect as pre-existing state, and then faithfully preserve it.
        """
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
        # restores must write THROUGH a symlinked config, never replace the link with a regular
        # file: the target is resolved now, and the link's shape and literal target recorded so a
        # client that replaces the link can be undone too
        self._config_restore_path = config_path.resolve()
        self._backup_path = self.backup_dir / f"{self.handler.name}-{config_path.name}"
        self._backup_path.write_bytes(config_path.read_bytes())
        self._backup_path.chmod(stat.S_IRUSR | stat.S_IWUSR)

    def _hardlinked_config_reason(self) -> str | None:
        """
        :return: why a config cannot be probed safely, or None when it can. A hardlinked config
            (some dotfile managers make them) has no restore this probe is willing to perform:
            the atomic path installs a NEW inode, silently detaching the other name and leaving
            it holding whatever the client wrote, while writing through the inode means a
            truncate whose interruption empties EVERY name of the file. Refusing is the only
            option that cannot damage the user's config.
        """
        config_path = self.spec.user_config_path
        if config_path is None or not self._config_existed:
            return None
        # stat() deliberately follows the link: it is the target's link count that matters
        if config_path.stat().st_nlink > 1:
            return (
                f"{config_path} is hardlinked (another name shares its inode) — refusing to touch a config this probe cannot restore safely"
            )
        return None

    def _remove_config_created_by_probe(self) -> None:
        # delete what the probe's setup call created (the baseline had no config file)
        config_path = self.spec.user_config_path
        if config_path is None or self._config_existed:
            return
        if self._config_was_symlink:
            # the baseline was a DANGLING link, and it must survive both undo paths: a
            # write-through that created the target, and a writer that replaced the link itself
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
        # atomic and owner-only from the first byte: mkstemp starts at 0600 and the pre-probe mode
        # goes on before the replace, so the config is never briefly readable by other users
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
        # the temp file is created INSIDE the guard that removes it: creating it first leaves a
        # window in which an interrupt strands a temp file beside the user's credentials
        temp_name: str | None = None
        try:
            fd, temp_name = tempfile.mkstemp(dir=str(restore_path.parent), prefix=f".{restore_path.name}.")
            with os.fdopen(fd, "wb") as temp_file:
                temp_file.write(self._backup_path.read_bytes())
            if self._config_mode is not None:
                os.chmod(temp_name, self._config_mode)
            os.replace(temp_name, restore_path)
        except BaseException:
            if temp_name is not None:
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
                # a client rewrite and a concurrent edit by another process are indistinguishable
                # on opaque bytes, so the note DISCLOSES that a concurrent change was rolled back
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
        # best-effort rollback after a failed mutation -- and it may not raise: this runs from a
        # finally, where an exception discards the verdict and the clients still to be probed
        try:
            # signals are DEFERRED for the whole rollback, not merely caught: SystemExit and
            # KeyboardInterrupt are BaseExceptions, and either would abort the restore halfway
            with _uninterruptible_cleanup():
                removal = self._run(self.spec.remove_argv)
                if removal.returncode != 0:
                    # the rollback's own failure, and for a client with no config path (codebuddy)
                    # this command IS the whole rollback -- silence here would report the original
                    # failure while leaving a registration the probe put there
                    self._notes.append(
                        f"EMERGENCY REMOVAL FAILED ({' '.join(self.spec.remove_argv)} exited {removal.returncode})"
                        " — the client may still carry a serena registration"
                    )
                    print(f"    !! emergency removal exited {removal.returncode}; the client may still be registered", flush=True)
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

    def _skip_without_probing(self, detail: str, cli_version: str | None = None) -> ProbeResult:
        """Skips a client, releasing whatever inspecting it already took.

        Every SKIP after the backup goes through here rather than returning directly: the backup
        is a credential-bearing copy, and a run that leaves one behind makes main() report that
        state was kept because a probe failed, when none ran. Inspection can also have created
        the config it read, which is undone for the same reason.
        """
        self._remove_config_created_by_probe()
        if self._backup_path is not None:
            self._backup_path.unlink(missing_ok=True)
            self._backup_path = None
        return self._result(Status.SKIP, detail, cli_version)

    def run(self) -> ProbeResult:
        """
        :return: the outcome of the full add/verify/remove/verify lifecycle for this client
        """
        # detection, via the same predicate `serena setup` uses -- under a deadline, since it
        # shells out without one
        applicable = _is_applicable_within_timeout(self.handler)
        if applicable is None:
            return self._result(Status.SKIP, f"client detection did not answer within {COMMAND_TIMEOUT_SECONDS}s; not probing")
        if not applicable:
            return self._result(Status.NOT_DETECTED, "client CLI not found or not functional")
        # captured before ANY client command runs: a command that only reads registrations can
        # still create the file it reads (claude mcp list does), and capturing afterwards would
        # take the probe's own side effect for the user's state. An unreadable config skips this
        # client rather than aborting the run
        try:
            self._backup_config()
        except OSError as e:
            return self._skip_without_probing(f"the user config could not be backed up ({e}); not probing")
        # ...and one this probe has no safe way to put back is not probed at all
        hardlinked_config = self._hardlinked_config_reason()
        if hardlinked_config is not None:
            return self._skip_without_probing(hardlinked_config)

        version_command = self._run((self.spec.list_argv[0], "--version"))
        cli_version = version_command.stdout.strip() or None

        # baseline: never touch a client that already has a serena registration
        baseline = self._run(self.spec.list_argv)
        if baseline.returncode != 0:
            return self._skip_without_probing(
                f"cannot query registrations ({' '.join(self.spec.list_argv)} exited {baseline.returncode})", cli_version
            )
        if self._serena_registered(baseline.stdout):
            return self._skip_without_probing("a serena MCP server is already registered — refusing to touch a live setup", cli_version)

        mutated = False
        try:
            # arm the rollback BEFORE the mutating command: an interrupt can arrive after the
            # registration was already written, and the finally below must still restore
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
                # the client may reformat the command text (codex renders columns), so verify it
                # token by token -- whole tokens, or ``--context=x`` would be satisfied by a row
                # carrying ``--context=x-extra``. An executable swapped while the row keeps its
                # ``serena`` name still matches; exact parsing is live_test_grok.py's job
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
            # restored and CONFIRMED before the rollback is disarmed: a client reserialization
            # plus an interrupt in between would otherwise leave the rewritten bytes in place
            self._verify_config_baseline()
            mutated = False
        finally:
            if mutated:
                self._emergency_restore()

        return self._result(Status.PASS, "add/verify/remove lifecycle completed; baseline confirmed", cli_version)


def main() -> int:
    _install_unwinding_signal_handlers()
    specs = client_probe_specs()
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--client", choices=sorted(specs), help="probe only this client")
    parser.add_argument("--list", action="store_true", help="only report which client CLIs are detected; do not probe")
    args = parser.parse_args()

    handlers = [h for h in client_setup_handlers if args.client is None or h.name == args.client]

    if args.list:
        for handler in handlers:
            detected = _is_applicable_within_timeout(handler)
            print(f"  {handler.name:<12} {'detected' if detected else '-' if detected is not None else 'no answer in time'}")
        return 0

    serena_executable = shutil.which("serena")
    if serena_executable is None:
        print("No serena executable on the PATH; run this script via `uv run` from the repository root.")
        return 2
    print(f"serena executable under test: {serena_executable}")

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
    finally:
        # ALWAYS dispose of the backup directory, interrupt included: it holds credential-bearing
        # copies in a temp dir the user was never told about
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
