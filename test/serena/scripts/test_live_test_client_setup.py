"""Behavior tests for the live client-setup probe (live_test_client_setup.py).

The probe's contract: a client is left exactly as it was found, whatever happens
mid-lifecycle, and a verdict is never reported on evidence that was not actually observed.
Every scenario drives ClientProbe with a scripted command runner — no real client CLI is
involved. Faults planted into the filesystem are asserted to have landed before the
behavior under test runs.
"""

import contextlib
import os
import signal
import stat
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

EXPECTED_COMMAND = "serena start-mcp-server --context=fake"

posix_only = pytest.mark.skipif(sys.platform == "win32", reason="asserts POSIX file modes")


def _probe(probe_module, backup_dir: Path, config_path: Path | None = None):
    handler = SimpleNamespace(name="fake", is_applicable=lambda: True, get_mcp_server_command=lambda: EXPECTED_COMMAND)
    spec = probe_module.ClientProbeSpec(("stub", "list"), ("stub", "remove"), config_path)
    return probe_module.ClientProbe(handler, spec, Path("serena"), backup_dir)


def _run_lifecycle(probe_module, probe, after_add: tuple[int, str], final: tuple[int, str] = (0, ""), baseline: tuple[int, str] = (0, "")):
    """Drive the full lifecycle, answering by WHAT was asked rather than by call position:
    the registration queries get baseline / after-add / final in that order, everything else
    (version, setup, remove, any emergency-restore command) gets a bland success. Scripting
    by position would bind these tests to the incidental order of unrelated commands.
    """
    list_responses = iter([baseline, after_add, final])
    calls: list[tuple[str, ...]] = []

    def scripted(argv: tuple[str, ...]):
        calls.append(argv)
        if argv == probe.spec.list_argv:
            try:
                returncode, stdout = next(list_responses)
            except StopIteration:  # a further query after the scripted three (rollback paths)
                returncode, stdout = 0, ""
        else:
            returncode, stdout = 0, "1.0" if "--version" in argv else ""
        return probe_module.ExecutedCommand(argv, returncode, stdout, "")

    probe._run = scripted
    return probe.run(), calls


class TestLifecycleVerdicts:
    """A verdict is only ever reported on observed evidence."""

    @pytest.mark.timeout(30)
    def test_a_client_whose_detection_hangs_is_skipped_not_waited_on(self, probe_module, tmp_path, monkeypatch) -> None:
        """Given a client CLI that hangs inside its own detection predicate, when the probe
        runs, then it SKIPs after the deadline instead of waiting forever — that predicate
        shells out without a timeout, so it is the one call that can outlast the bounded
        runner and hang the whole script.
        """
        monkeypatch.setattr(probe_module, "COMMAND_TIMEOUT_SECONDS", 1)
        probe = _probe(probe_module, tmp_path)
        issued: list[tuple[str, ...]] = []
        probe._run = lambda argv: issued.append(argv) or probe_module.ExecutedCommand(argv, 0, "", "")
        probe.handler.is_applicable = lambda: time.sleep(300) or True  # never answers in time
        result = probe.run()
        assert result.status == probe_module.Status.SKIP
        assert "did not answer" in result.detail
        assert issued == []  # nothing was run against a client we could not even detect

    def test_a_client_that_already_has_serena_is_skipped_untouched(self, probe_module, tmp_path) -> None:
        """Given the client already carries a serena registration, when the probe runs, then
        it SKIPs without issuing setup — this is the guard that keeps the probe off a live
        user setup, and mutating one would be the worst thing this script could do.
        """
        probe = _probe(probe_module, tmp_path)
        issued: list[tuple[str, ...]] = []

        def recording_run(argv):
            issued.append(argv)
            if argv == ("stub", "list"):
                return probe_module.ExecutedCommand(argv, 0, f"serena  {EXPECTED_COMMAND}", "")
            return probe_module.ExecutedCommand(argv, 0, "", "")

        probe._run = recording_run
        result = probe.run()
        assert result.status == probe_module.Status.SKIP
        assert "already registered" in result.detail
        assert not any("setup" in argv for argv in issued)

    def test_an_unreadable_baseline_skips_rather_than_mutating(self, probe_module, tmp_path) -> None:
        """Given the baseline registration query fails, when the probe runs, then it SKIPs
        without issuing setup — empty output from a failed query must never be read as
        'no serena registered here', which is the misreading that would license a mutation.
        """
        probe = _probe(probe_module, tmp_path)
        issued: list[tuple[str, ...]] = []

        def failing_baseline_run(argv):
            issued.append(argv)
            if argv == ("stub", "list"):
                return probe_module.ExecutedCommand(argv, 1, "", "cli exploded")
            return probe_module.ExecutedCommand(argv, 0, "", "")

        probe._run = failing_baseline_run
        result = probe.run()
        assert result.status == probe_module.Status.SKIP
        assert "cannot query registrations" in result.detail
        assert not any("setup" in argv for argv in issued)

    # What a client's list output says about serena's registration, and the verdict each
    # shape must produce. One contract, so one table: every row is a real client behaviour
    # (codex renders columns; a wrong or extended command must not pass; another server's
    # row is not evidence about ours) and the verdict is what the probe is allowed to claim.
    @pytest.mark.parametrize(
        ("case", "serena_row_output", "expected_status", "expected_evidence"),
        [
            ("verbatim", f"serena  {EXPECTED_COMMAND}", "PASS", "expected command:"),
            ("column-formatted", "serena  serena   start-mcp-server --context=fake", "PASS", "reformatted by the client"),
            ("wrong command", "serena  serena start-mcp-server --context=WRONG", "FAIL", "lacks expected parts: --context=fake"),
            ("token merely prefixed", "serena  serena   start-mcp-server --context=fake-extra", "FAIL", "--context=fake"),
            ("verbatim but suffixed", f"serena  {EXPECTED_COMMAND}-extra", "FAIL", "--context=fake"),
            (
                "tokens only on another row",
                "othertool  foo start-mcp-server --context=fake\nserena  serena",
                "PASS",
                "does not expose command text",
            ),
            ("no command text at all", "serena", "PASS", "does not expose command text"),
        ],
        ids=lambda value: value if isinstance(value, str) and " " in value and "serena" not in value else None,
    )
    def test_the_registered_command_is_verified_from_what_the_client_shows(
        self, probe_module, tmp_path, case: str, serena_row_output: str, expected_status: str, expected_evidence: str
    ) -> None:
        """Given each shape a client's list output takes, the probe reaches the verdict the
        evidence supports — and never a stronger one.
        """
        result, calls = _run_lifecycle(probe_module, _probe(probe_module, tmp_path), after_add=(0, serena_row_output))
        assert result.status == getattr(probe_module.Status, expected_status)
        evidence = result.detail + " ".join(result.notes)
        assert expected_evidence in evidence
        if expected_status == "FAIL":
            assert calls[-1] == ("stub", "remove")  # a failed verification still rolls back
        if case == "tokens only on another row":
            assert not any("expected command:" in note for note in result.notes)

    def test_a_failed_final_query_fails_with_the_rollback_still_armed(self, probe_module, tmp_path) -> None:
        """Given a final registration query that exits nonzero, when the lifecycle runs,
        then its empty output is not read as proof of removal: the probe FAILs and the
        emergency rollback still runs.
        """
        result, calls = _run_lifecycle(
            probe_module, _probe(probe_module, tmp_path), after_add=(0, f"serena  {EXPECTED_COMMAND}"), final=(1, "")
        )
        assert result.status == probe_module.Status.FAIL
        assert "cannot verify the removal" in result.detail
        assert calls[-1] == ("stub", "remove")

    def test_losing_another_servers_registration_fails_even_without_a_config_file(self, probe_module, tmp_path) -> None:
        """Given a client with no known config file whose other registration vanished during
        the lifecycle, when the final list is compared with the baseline, then the probe
        FAILs instead of declaring the baseline restored on serena's absence alone.
        """
        result, calls = _run_lifecycle(
            probe_module,
            _probe(probe_module, tmp_path),
            baseline=(0, "othertool  foo --serve"),
            after_add=(0, f"othertool  foo --serve\nserena  {EXPECTED_COMMAND}"),
            final=(0, ""),
        )
        assert result.status == probe_module.Status.FAIL
        assert "registration set differs from the baseline" in result.detail
        assert calls[-1] == ("stub", "remove")

    def test_a_rewritten_registration_fails_even_when_the_name_survives(self, probe_module, tmp_path) -> None:
        """Given a client with no known config file whose other registration kept its name
        but changed its command during the lifecycle, when the final list is compared with
        the baseline, then the probe FAILs — records are compared, not names.
        """
        result, calls = _run_lifecycle(
            probe_module,
            _probe(probe_module, tmp_path),
            baseline=(0, "othertool  foo --serve"),
            after_add=(0, f"othertool  foo --serve\nserena  {EXPECTED_COMMAND}"),
            final=(0, "othertool  foo --other"),
        )
        assert result.status == probe_module.Status.FAIL
        assert "registration set differs from the baseline" in result.detail
        assert calls[-1] == ("stub", "remove")

    def test_a_preserved_registration_set_passes_and_is_noted(self, probe_module, tmp_path) -> None:
        """Given a client with no known config file whose other registration survived the
        lifecycle untouched, when the final list matches the baseline, then the probe
        PASSes and notes the comparison.
        """
        result, _ = _run_lifecycle(
            probe_module,
            _probe(probe_module, tmp_path),
            baseline=(0, "othertool  foo --serve"),
            after_add=(0, f"othertool  foo --serve\nserena  {EXPECTED_COMMAND}"),
            final=(0, "othertool  foo --serve"),
        )
        assert result.status == probe_module.Status.PASS
        assert any("registration set matches the baseline" in note for note in result.notes)

    def test_a_failed_query_after_add_fails_rather_than_misdiagnosing(self, probe_module, tmp_path) -> None:
        """Given a registration query that fails right after setup, when the lifecycle
        runs, then the probe reports the query failure, not a missing registration.
        """
        result, calls = _run_lifecycle(probe_module, _probe(probe_module, tmp_path), after_add=(1, ""))
        assert result.status == probe_module.Status.FAIL
        assert "cannot verify the registration landed" in result.detail
        assert calls[-1] == ("stub", "remove")


class TestClientSpecs:
    """The specs must name the configs the CLIs actually mutate."""

    def test_client_homes_follow_their_env_overrides(self, probe_module, monkeypatch, tmp_path) -> None:
        """Given CODEX_HOME and CLAUDE_CONFIG_DIR point at custom directories, the specs
        track the configs the CLIs would actually write — backing up ~/.codex while the
        client mutates $CODEX_HOME would guard the wrong file; without the overrides, the
        home-directory defaults stand.
        """
        monkeypatch.setenv("CODEX_HOME", str(tmp_path / "codexhome"))
        monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "claudehome"))
        specs = probe_module.client_probe_specs()
        assert specs["codex"].user_config_path == tmp_path / "codexhome" / "config.toml"
        assert specs["claude-code"].user_config_path == tmp_path / "claudehome" / ".claude.json"
        monkeypatch.delenv("CODEX_HOME")
        monkeypatch.delenv("CLAUDE_CONFIG_DIR")
        specs = probe_module.client_probe_specs()
        assert specs["codex"].user_config_path == Path.home() / ".codex" / "config.toml"
        assert specs["claude-code"].user_config_path == Path.home() / ".claude.json"


class TestRecordDirectory:
    """--record writes credential-bearing transcripts, so where it writes them matters."""

    @posix_only
    def test_a_symlinked_record_directory_is_refused(self, probe_module, monkeypatch, tmp_path, capsys) -> None:
        """Given --record names a pre-existing symlink to a directory, when the script runs,
        then it refuses: mkdir(exist_ok=True) accepts such a link, and every snapshot write
        would then be redirected through it — the leaf-only O_NOFOLLOW guard cannot see that.
        """
        victim_dir = tmp_path / "victim"
        victim_dir.mkdir()
        link = tmp_path / "records"
        link.symlink_to(victim_dir)
        monkeypatch.setattr(probe_module.sys, "argv", ["live_test_client_setup.py", "--record", str(link)])
        monkeypatch.setattr(probe_module.shutil, "which", lambda name: "/usr/bin/serena")
        assert probe_module.main() == 2
        assert "symlink" in capsys.readouterr().err


class TestStatePreservation:
    """Whatever happens, the client's configuration returns to its pre-probe state."""

    @staticmethod
    def _restore_probe(probe_module, tmp_path: Path):
        config_path = tmp_path / "config.json"
        probe = _probe(probe_module, tmp_path, config_path=config_path)
        probe._run = lambda argv: probe_module.ExecutedCommand(argv, 0, "", "")
        return probe, config_path

    def test_a_config_created_by_the_probe_is_deleted_when_the_probe_fails(self, probe_module, tmp_path) -> None:
        """Given no config existed before the probe and its setup call created one, when
        emergency restore runs, then the created file is gone.
        """
        probe, config_path = self._restore_probe(probe_module, tmp_path)
        probe._backup_config()  # records that nothing existed
        config_path.write_text('{"created": "by probe"}')
        assert config_path.is_file() and config_path.stat().st_size > 0  # the plant landed
        probe._emergency_restore()
        assert not config_path.is_file()

    def test_a_pre_existing_config_is_restored_from_backup_and_the_backup_kept(self, probe_module, tmp_path) -> None:
        """Given a pre-existing config that the failed lifecycle rewrote, when emergency
        restore runs, then the original bytes return and the backup is kept for review.
        """
        probe, config_path = self._restore_probe(probe_module, tmp_path)
        original = b'{"original": true}'
        config_path.write_bytes(original)
        probe._backup_config()
        config_path.write_bytes(b'{"mutated": true}')
        assert config_path.read_bytes() != original  # the plant landed
        probe._emergency_restore()
        assert config_path.read_bytes() == original
        # the backup is kept for review, and the result SAYS where — that note and the file
        # on disk are the contract; the attribute holding the path is not
        assert any("backup kept at" in note for note in probe._result(probe_module.Status.FAIL, "x").notes)
        assert list(tmp_path.glob("fake-config.json"))

    @posix_only
    # The pre-probe mode must come back whether the client loosened it or deleted the file,
    # and whatever that mode was: 0600 catches a naive write inheriting the umask, 0644
    # catches a restore that inherits the owner-only temp file instead of applying the
    # recorded mode. One property, three ways for a client to break it.
    @posix_only
    @pytest.mark.parametrize(
        ("mode", "client_action"),
        [(0o600, "rewrite"), (0o600, "delete"), (0o644, "delete")],
        ids=["loosened-from-0600", "deleted-was-0600", "deleted-was-0644"],
    )
    def test_the_pre_probe_mode_and_bytes_come_back(self, probe_module, tmp_path, mode: int, client_action: str) -> None:
        """Given a config the client rewrote or deleted, when the probe restores it, then
        both its bytes and its pre-probe mode return.
        """
        probe, config_path = self._restore_probe(probe_module, tmp_path)
        original = b'{"perm": "test"}'
        config_path.write_bytes(original)
        config_path.chmod(mode)
        probe._backup_config()
        if client_action == "rewrite":
            config_path.write_bytes(b'{"perm": "mutated"}')
            config_path.chmod(0o644 if mode == 0o600 else 0o600)
            assert config_path.read_bytes() != original  # the plant landed
            probe._verify_config_baseline()
        else:
            config_path.unlink()
            assert not config_path.is_file()  # the plant landed
            probe._emergency_restore()
        assert config_path.read_bytes() == original
        assert stat.S_IMODE(config_path.stat().st_mode) == mode

    # A symlinked config has two independent properties a client can break: whether the path
    # is still a link, and what its target holds. Four shapes cover the matrix — the link may
    # exist or dangle, and the client may write THROUGH it or REPLACE it (atomic-rename
    # writers do) — and in every one the user's link must survive with the right content
    # behind it. Byte comparison alone sees none of this.
    @posix_only
    @pytest.mark.parametrize(
        ("target_exists", "client_replaces_the_link"),
        [(True, False), (True, True), (False, False), (False, True)],
        ids=["intact-written-through", "intact-replaced", "dangling-written-through", "dangling-replaced"],
    )
    def test_a_symlinked_config_survives_every_way_a_client_writes_it(
        self, probe_module, tmp_path, target_exists: bool, client_replaces_the_link: bool
    ) -> None:
        """Given a config managed as a symlink, when the lifecycle finishes, then the path is
        still that link, its target holds the pre-probe content, and nothing the probe caused
        is left behind.
        """
        dotfiles = tmp_path / "dotfiles"
        dotfiles.mkdir()
        target = dotfiles / "config.json"
        original = b'{"linked": true}'
        if target_exists:
            target.write_bytes(original)
        link = tmp_path / "config.json"
        link.symlink_to(target)
        probe = _probe(probe_module, tmp_path, link)
        calls = {"lists": 0}

        def writing_run(argv):
            if "setup" in argv:
                if client_replaces_the_link:
                    link.unlink()
                    # IDENTICAL bytes where there were any: an atomic-rename writer preserves
                    # content, so only the link's shape betrays the swap. Writing different
                    # bytes here would let the byte comparison catch it and leave the shape
                    # check unexercised
                    link.write_bytes(original if target_exists else b'{"written-by-rename": true}')
                else:
                    target.write_bytes(b'{"written-through": true}')  # written through the link
            if argv == ("stub", "list"):
                calls["lists"] += 1
                return probe_module.ExecutedCommand(argv, 0, f"serena  {EXPECTED_COMMAND}" if calls["lists"] == 2 else "", "")
            return probe_module.ExecutedCommand(argv, 0, "", "")

        probe._run = writing_run
        result = probe.run()
        assert result.status == probe_module.Status.PASS
        assert link.is_symlink()
        assert os.readlink(link) == str(target)
        if target_exists:
            assert target.read_bytes() == original
        else:
            assert not target.exists()  # a dangling link is left dangling, as it was found

    def test_an_interrupt_before_the_baseline_is_confirmed_still_restores(self, probe_module, tmp_path) -> None:
        """Given the client reserialized the config and an interrupt arrives while the
        baseline is being verified, when the probe unwinds, then emergency restore still
        runs — the rollback must stay armed until the baseline is confirmed, not be cleared
        on the strength of the registration checks alone.
        """
        config_path = tmp_path / "config.json"
        original = b'{"clean": true}'
        config_path.write_bytes(original)
        probe = _probe(probe_module, tmp_path, config_path)
        calls = {"lists": 0}

        def rewriting_run(argv):
            if "setup" in argv:
                config_path.write_bytes(b'{"client-reserialized": true}')
            if argv == ("stub", "list"):
                calls["lists"] += 1
                return probe_module.ExecutedCommand(argv, 0, f"serena  {EXPECTED_COMMAND}" if calls["lists"] == 2 else "", "")
            return probe_module.ExecutedCommand(argv, 0, "", "")

        probe._run = rewriting_run

        def interrupted_verify():
            raise KeyboardInterrupt

        probe._verify_config_baseline = interrupted_verify
        with pytest.raises(KeyboardInterrupt):
            probe.run()
        assert config_path.read_bytes() == original

    @posix_only
    def test_a_failed_backup_leaves_no_hidden_hardlink_behind(self, probe_module, tmp_path) -> None:
        """Given the backup fails after the config's inode was anchored, when the probe gives
        up, then no anchor is left in the user's config directory — it is a hidden hardlink to
        a possibly credential-bearing file, and this runs before the caller's cleanup exists,
        so nothing else would ever remove it.
        """
        config_path = tmp_path / "config.json"
        config_path.write_bytes(b'{"hardlinked": true}')
        os.link(config_path, tmp_path / "dotfiles-config.json")
        probe = _probe(probe_module, tmp_path, config_path)
        probe.backup_dir = tmp_path / "does-not-exist"  # the backup write will fail
        with pytest.raises(OSError):
            probe._backup_config()
        assert not list(tmp_path.glob(".config.json.serena-probe-link*"))

    @posix_only
    def test_the_inode_anchor_never_overwrites_something_already_there(self, probe_module, tmp_path) -> None:
        """Given a file already sitting where the probe would anchor the config's inode, when
        the backup runs, then that file is untouched and the anchor goes elsewhere — it could
        be an unrelated user file, or the recovery anchor an interrupted probe left behind,
        and destroying either to make room would be the opposite of preserving state.
        """
        config_path = tmp_path / "config.json"
        config_path.write_bytes(b'{"hardlinked": true}')
        os.link(config_path, tmp_path / "dotfiles-config.json")
        probe = _probe(probe_module, tmp_path, config_path)
        probe._run = lambda argv: probe_module.ExecutedCommand(argv, 0, "", "")
        squatter = tmp_path / f".config.json.serena-probe-link.{os.getpid()}.0"
        squatter.write_bytes(b"someone else's file")
        probe._backup_config()
        assert squatter.read_bytes() == b"someone else's file"
        assert probe._config_link_anchor is not None and probe._config_link_anchor != squatter

    @posix_only
    def test_an_atomic_rewrite_that_severs_a_hardlink_is_relinked(self, probe_module, tmp_path) -> None:
        """Given a hardlinked config and a client that rewrites it by atomic rename with
        BYTE-IDENTICAL content, when the lifecycle finishes, then the path is back on its
        original inode — the bytes match either way, so only the inode identity can see that
        the user's two names silently stopped being the same file.
        """
        config_path = tmp_path / "config.json"
        twin = tmp_path / "dotfiles-config.json"
        original = b'{"hardlinked": true}'
        config_path.write_bytes(original)
        os.link(config_path, twin)
        inode_before = config_path.stat().st_ino
        probe = _probe(probe_module, tmp_path, config_path)
        calls = {"lists": 0}

        def rename_writing_run(argv):
            if "setup" in argv:
                replacement = tmp_path / "incoming.json"
                replacement.write_bytes(original)  # same bytes, brand-new inode
                os.replace(replacement, config_path)
            if argv == ("stub", "list"):
                calls["lists"] += 1
                return probe_module.ExecutedCommand(argv, 0, f"serena  {EXPECTED_COMMAND}" if calls["lists"] == 2 else "", "")
            return probe_module.ExecutedCommand(argv, 0, "", "")

        probe._run = rename_writing_run
        result = probe.run()
        assert result.status == probe_module.Status.PASS
        assert config_path.stat().st_ino == inode_before == twin.stat().st_ino
        assert config_path.read_bytes() == original
        assert any("relinked" in note for note in result.notes)
        assert not list(tmp_path.glob(".config.json.serena-probe-link"))  # the anchor is cleaned up

    @posix_only
    def test_a_hardlinked_config_deleted_by_the_client_is_recreated(self, probe_module, tmp_path) -> None:
        """Given a hardlinked config the client then DELETED, when the probe restores it,
        then the file is back with the baseline bytes — writing through the inode is
        impossible once the path is gone, and a restore that only knows that trick would
        crash with a good backup in hand.
        """
        config_path = tmp_path / "config.json"
        twin = tmp_path / "dotfiles-config.json"
        original = b'{"hardlinked": true}'
        config_path.write_bytes(original)
        os.link(config_path, twin)
        probe = _probe(probe_module, tmp_path, config_path)
        probe._run = lambda argv: probe_module.ExecutedCommand(argv, 0, "", "")
        probe._backup_config()
        config_path.unlink()
        assert not config_path.exists()  # the plant landed
        probe._emergency_restore()
        assert config_path.read_bytes() == original

    @posix_only
    def test_a_deleted_hardlinked_config_is_recreated_even_without_an_anchor(self, probe_module, tmp_path) -> None:
        """Given a hardlinked config the client deleted, and no inode anchor to relink from
        (a filesystem that refused one), when the restore runs, then the file comes back —
        writing through an inode is impossible once the path is gone, so the restore must
        fall back to recreating it rather than raising with a good backup in hand.
        """
        config_path = tmp_path / "config.json"
        original = b'{"hardlinked": true}'
        config_path.write_bytes(original)
        os.link(config_path, tmp_path / "dotfiles-config.json")
        probe = _probe(probe_module, tmp_path, config_path)
        probe._run = lambda argv: probe_module.ExecutedCommand(argv, 0, "", "")
        probe._backup_config()
        probe._discard_link_anchor()  # as if the filesystem had refused the anchor
        config_path.unlink()
        probe._restore_config_bytes()
        assert config_path.read_bytes() == original

    @posix_only
    def test_an_unreadable_backup_leaves_a_hardlinked_config_intact(self, probe_module, tmp_path) -> None:
        """Given the backup has gone missing, when the hardlinked restore runs, then the
        config and its twin still hold what they held — reading the backup only after
        truncating would empty both names before discovering there was nothing to write.
        """
        config_path = tmp_path / "config.json"
        twin = tmp_path / "dotfiles-config.json"
        config_path.write_bytes(b'{"baseline": true}')
        os.link(config_path, twin)
        probe = _probe(probe_module, tmp_path, config_path)
        probe._run = lambda argv: probe_module.ExecutedCommand(argv, 0, "", "")
        probe._backup_config()
        config_path.write_bytes(b'{"client-wrote": true}')
        assert probe._backup_path is not None
        probe._backup_path.unlink()  # the backup disappears before the restore
        with pytest.raises(OSError):
            probe._restore_config_bytes()
        assert config_path.read_bytes() == b'{"client-wrote": true}'
        assert twin.read_bytes() == b'{"client-wrote": true}'

    @posix_only
    def test_a_hardlinked_restore_refuses_to_write_through_a_symlink(self, probe_module, tmp_path) -> None:
        """Given the config path became a symlink pointing at an unrelated file, when the
        hardlink restore runs, then it refuses rather than truncating the link's target —
        the inode write is the one restore path that opens by name without the atomic
        replace's protections.
        """
        config_path = tmp_path / "config.json"
        config_path.write_bytes(b'{"hardlinked": true}')
        os.link(config_path, tmp_path / "dotfiles-config.json")
        probe = _probe(probe_module, tmp_path, config_path)
        probe._run = lambda argv: probe_module.ExecutedCommand(argv, 0, "", "")
        probe._backup_config()
        victim = tmp_path / "victim.json"
        victim.write_text("precious")
        config_path.unlink()
        config_path.symlink_to(victim)
        with pytest.raises(OSError):
            probe._restore_config_bytes()
        assert victim.read_text() == "precious"

    @posix_only
    def test_a_hardlinked_config_is_restored_through_its_inode(self, probe_module, tmp_path) -> None:
        """Given the config is hardlinked into a dotfiles tree, when the probe restores it,
        then the twin name carries the baseline bytes too — an atomic replace would install a
        new inode and leave the twin holding whatever the client wrote.
        """
        config_path = tmp_path / "config.json"
        twin = tmp_path / "dotfiles-config.json"
        original = b'{"hardlinked": true}'
        config_path.write_bytes(original)
        os.link(config_path, twin)
        probe = _probe(probe_module, tmp_path, config_path)
        probe._run = lambda argv: probe_module.ExecutedCommand(argv, 0, "", "")
        probe._backup_config()
        with open(config_path, "wb") as mutated:  # in-place rewrite: the twin sees it too
            mutated.write(b'{"client-wrote": true}')
        assert twin.read_bytes() == b'{"client-wrote": true}'  # the plant landed
        probe._emergency_restore()
        assert config_path.read_bytes() == original
        assert twin.read_bytes() == original

    def test_a_failing_emergency_restore_keeps_the_probes_own_verdict(self, probe_module, tmp_path) -> None:
        """Given the rollback itself fails, when the probe unwinds, then the probe's own FAIL
        verdict survives with a loud note — raising from the finally would discard the
        verdict, its transcript, and every client still to be probed.
        """
        config_path = tmp_path / "config.json"
        config_path.write_bytes(b'{"clean": true}')
        probe = _probe(probe_module, tmp_path, config_path)
        calls = {"lists": 0}

        def failing_run(argv):
            if argv == ("stub", "list"):
                calls["lists"] += 1
                if calls["lists"] == 2:
                    return probe_module.ExecutedCommand(argv, 1, "", "boom")  # FAIL after mutating
            return probe_module.ExecutedCommand(argv, 0, "", "")

        probe._run = failing_run

        def exploding_restore():
            raise OSError("no space left on device")

        probe._restore_config_bytes = exploding_restore
        result = probe.run()
        assert result.status == probe_module.Status.FAIL
        assert "cannot verify the registration landed" in result.detail
        assert any("EMERGENCY RESTORE FAILED" in note for note in result.notes)

    def test_a_config_rewritten_during_the_lifecycle_is_restored_with_disclosure(self, probe_module, tmp_path) -> None:
        """Given a clean lifecycle during which the config's bytes changed (a client rewrite
        and a concurrent edit by another process are indistinguishable on opaque bytes), when
        the baseline is verified, then the backup is restored and the result DISCLOSES that
        any concurrent change was rolled back with it.
        """
        config_path = tmp_path / "config.json"
        original = b'{"clean": true}'
        config_path.write_bytes(original)
        probe = _probe(probe_module, tmp_path, config_path)
        calls = {"lists": 0}

        def rewriting_run(argv):
            if "setup" in argv:
                config_path.write_bytes(b'{"rewritten": true}')
            if argv == ("stub", "list"):
                calls["lists"] += 1
                return probe_module.ExecutedCommand(argv, 0, f"serena  {EXPECTED_COMMAND}" if calls["lists"] == 2 else "", "")
            return probe_module.ExecutedCommand(argv, 0, "", "")

        probe._run = rewriting_run
        result = probe.run()
        assert result.status == probe_module.Status.PASS
        assert config_path.read_bytes() == original
        assert any("concurrent" in note for note in result.notes)

    def test_an_interrupt_during_setup_still_restores_the_config(self, probe_module, tmp_path) -> None:
        """Given the user interrupts while serena setup is running, when the probe unwinds,
        then the config is restored from backup — the rollback must be armed BEFORE the
        mutating command, because the registration may already have been written.
        """
        config_path = tmp_path / "config.json"
        original = b'{"clean": true}'
        config_path.write_bytes(original)
        probe = _probe(probe_module, tmp_path, config_path)

        def interrupting_run(argv):
            if "setup" in argv:
                config_path.write_bytes(b'{"mutated": true}')  # the half-written registration
                raise KeyboardInterrupt
            return probe_module.ExecutedCommand(argv, 0, "", "")

        probe._run = interrupting_run
        with pytest.raises(KeyboardInterrupt):
            probe.run()
        assert config_path.read_bytes() == original

    @posix_only
    def test_a_timeout_kills_the_whole_process_tree(self, probe_module, tmp_path, monkeypatch) -> None:
        """Given a timed-out command whose child spawned a long-running grandchild, when
        _run gives up, then the grandchild is dead too — an orphan finishing its
        registration after the rollback would silently undo the cleanup.
        """
        pid_file = tmp_path / "grandchild.pid"
        monkeypatch.setattr(probe_module, "COMMAND_TIMEOUT_SECONDS", 2)
        probe = _probe(probe_module, tmp_path)
        # the grandchild detaches its stdio, as a daemonizing client would — otherwise its
        # inherited pipes keep communicate() blocked until it exits, masking the orphan
        executed = probe._run(("sh", "-c", f"sleep 60 >/dev/null 2>&1 & echo $! > {pid_file}; wait"))
        assert executed.returncode == -1 and "timed out" in executed.stderr
        grandchild = int(pid_file.read_text())
        for _ in range(40):  # SIGKILL is immediate, but init may not have reaped the orphan yet
            try:
                os.kill(grandchild, 0)
            except ProcessLookupError:
                break
            time.sleep(0.05)
        with pytest.raises(ProcessLookupError):
            os.kill(grandchild, 0)

    @posix_only
    @pytest.mark.timeout(20)
    def test_an_interrupt_mid_command_kills_the_detached_child(self, probe_module, tmp_path, monkeypatch) -> None:
        """Given Ctrl-C arrives while a command is running, when _run unwinds, then the
        detached child is dead — the child no longer receives the terminal's interrupt
        (own session), and leaving it running would keep the Popen context manager waiting
        without any timeout, so the emergency restore would never run. The 20s test timeout
        is load-bearing: without the interrupt handler this test hangs on the child.
        """
        pid_file = tmp_path / "child.pid"
        probe = _probe(probe_module, tmp_path)
        real_communicate = probe_module.subprocess.Popen.communicate
        calls = {"n": 0}

        def interrupting_communicate(popen_self, *args, **kwargs):
            calls["n"] += 1
            if calls["n"] == 1:
                deadline = time.time() + 5
                while not pid_file.is_file() and time.time() < deadline:
                    time.sleep(0.02)
                raise KeyboardInterrupt
            return real_communicate(popen_self, *args, **kwargs)

        monkeypatch.setattr(probe_module.subprocess.Popen, "communicate", interrupting_communicate)
        with pytest.raises(KeyboardInterrupt):
            probe._run(("sh", "-c", f"echo $$ > {pid_file}; sleep 300"))
        child = int(pid_file.read_text())
        for _ in range(40):
            try:
                os.kill(child, 0)
            except ProcessLookupError:
                break
            time.sleep(0.05)
        with pytest.raises(ProcessLookupError):
            os.kill(child, 0)

    @posix_only
    @pytest.mark.timeout(30)
    def test_a_timeout_returns_even_when_a_grandchild_holds_the_pipes(self, probe_module, tmp_path, monkeypatch) -> None:
        """Given a timed-out command whose grandchild escaped the process group with its own
        session AND still holds the inherited pipes, when _run gives up, then it returns
        rather than blocking forever on EOF — the probe has already mutated the client at
        this point, so a wedged reap would strand the rollback. The grandchild deliberately
        outlives this test's timeout, so an unbounded drain cannot resolve itself into a pass.
        """
        monkeypatch.setattr(probe_module, "COMMAND_TIMEOUT_SECONDS", 2)
        probe = _probe(probe_module, tmp_path)
        pid_file = tmp_path / "escaped.pid"
        # setsid puts the grandchild outside the killed group; it inherits stdout/stderr
        executed = probe._run(("sh", "-c", f"setsid sh -c 'echo $$ > {pid_file}; sleep 300' & sleep 300"))
        assert executed.returncode == -1 and "timed out" in executed.stderr
        # the escaped grandchild is this test's litter, not the probe's: clean it up rather
        # than leaving it running for five minutes after the suite finishes
        if pid_file.is_file():
            with contextlib.suppress(ProcessLookupError, ValueError):
                os.kill(int(pid_file.read_text().strip()), signal.SIGKILL)

    def test_sigterm_unwinds_instead_of_killing_the_process(self, probe_module) -> None:
        """Given the handlers this script installs, when SIGTERM arrives, then it raises
        rather than terminating silently — the default disposition would skip every finally,
        leaving the client registered and the backup unreported.
        """
        import signal as signal_module
        from collections.abc import Callable
        from typing import cast

        # SIGHUP does not exist on Windows — the script skips what a platform lacks, and so
        # must its test; SIGTERM is everywhere, so the unwinding contract is checked everywhere
        sighup = getattr(signal_module, "SIGHUP", None)
        signums = [signal_module.SIGTERM] + ([sighup] if sighup is not None else [])
        previous = {s: signal_module.getsignal(s) for s in signums}
        try:
            probe_module._install_unwinding_signal_handlers()
            installed = signal_module.getsignal(signal_module.SIGTERM)
            assert callable(installed)  # not SIG_DFL/SIG_IGN, which would kill the process instead
            with pytest.raises(SystemExit):
                cast(Callable[[int, object], None], installed)(signal_module.SIGTERM, None)

            # an inherited SIG_IGN is deliberate (nohup): installing over it would abort the
            # detached runs this script documents
            if sighup is not None:
                signal_module.signal(sighup, signal_module.SIG_IGN)
                probe_module._install_unwinding_signal_handlers()
                assert signal_module.getsignal(sighup) is signal_module.SIG_IGN
        finally:
            for signum, handler in previous.items():
                signal_module.signal(signum, handler)

    @posix_only
    def test_a_snapshot_never_writes_through_a_planted_symlink(self, probe_module, tmp_path) -> None:
        """Given the record directory already holds a symlink under the snapshot's name,
        when the snapshot is written, then it refuses and the link's target is untouched —
        following the link would truncate and chmod an unrelated file.
        """
        victim = tmp_path / "victim.json"
        victim.write_text('{"precious": true}')
        record_dir = tmp_path / "records"
        record_dir.mkdir()
        (record_dir / "stub.json").symlink_to(victim)
        result = probe_module.ProbeResult(client="stub", status=probe_module.Status.PASS, detail="ok")
        with pytest.raises(RuntimeError, match="symlink"):
            probe_module._write_snapshot(record_dir, result)
        assert victim.read_text() == '{"precious": true}'

    @posix_only
    def test_a_recorded_snapshot_is_owner_only_regardless_of_umask(self, probe_module, tmp_path) -> None:
        """Given a permissive umask, when a probe result is snapshotted via --record, then the
        JSON lands owner-only, because transcripts echo other servers' registration lines,
        which can carry credentials in commands or env values.
        """
        result = probe_module.ProbeResult(client="stub", status=probe_module.Status.PASS, detail="ok")
        old_umask = os.umask(0o000)
        try:
            snapshot_path = probe_module._write_snapshot(tmp_path, result)
        finally:
            os.umask(old_umask)
        assert snapshot_path.is_file()
        assert stat.S_IMODE(snapshot_path.stat().st_mode) == 0o600

    @posix_only
    def test_a_leftover_snapshot_with_a_looser_mode_is_tightened_before_content_lands(self, probe_module, tmp_path) -> None:
        """Given a snapshot file left by an earlier run with a permissive mode, when the
        probe snapshots over it, then the rewritten file is owner-only — creation-time
        modes only govern new files, so the leftover must be tightened explicitly.
        """
        leftover = tmp_path / "stub.json"
        leftover.write_text("{}")
        leftover.chmod(0o644)
        assert stat.S_IMODE(leftover.stat().st_mode) == 0o644  # the plant landed
        result = probe_module.ProbeResult(client="stub", status=probe_module.Status.PASS, detail="ok")
        snapshot_path = probe_module._write_snapshot(tmp_path, result)
        assert snapshot_path == leftover
        assert "transcript" in snapshot_path.read_text()  # the content really was rewritten
        assert stat.S_IMODE(snapshot_path.stat().st_mode) == 0o600
