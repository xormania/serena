"""Behavior tests for the live client-setup probe (live_test_client_setup.py).

The probe's contract: a client is left exactly as it was found, whatever happens
mid-lifecycle, and a verdict is never reported on evidence that was not actually observed.
Every scenario drives ClientProbe with a scripted command runner — no real client CLI is
involved. Faults planted into the filesystem are asserted to have landed before the
behavior under test runs.
"""

import os
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
    """Drive the full lifecycle with scripted responses for the six commands it issues:
    --version, baseline list, setup, list after add, remove, final list.
    """
    responses = iter([(0, "1.0"), baseline, (0, ""), after_add, (0, ""), final])
    calls: list[tuple[str, ...]] = []

    def scripted(argv: tuple[str, ...]):
        try:
            returncode, stdout = next(responses)
        except StopIteration:  # emergency-restore commands issued after the scripted six
            returncode, stdout = 0, ""
        calls.append(argv)
        return probe_module.ExecutedCommand(argv, returncode, stdout, "")

    probe._run = scripted
    return probe.run(), calls


class TestLifecycleVerdicts:
    """A verdict is only ever reported on observed evidence."""

    def test_a_clean_lifecycle_passes_and_names_the_verified_command(self, probe_module, tmp_path) -> None:
        """Given a client that registers, echoes the expected command, and removes
        cleanly, when the lifecycle runs, then the probe PASSes and notes the command.
        """
        result, _ = _run_lifecycle(probe_module, _probe(probe_module, tmp_path), after_add=(0, f"serena  {EXPECTED_COMMAND}"))
        assert result.status == probe_module.Status.PASS
        assert any("expected command:" in note for note in result.notes)

    def test_a_column_formatted_command_is_verified_token_by_token(self, probe_module, tmp_path) -> None:
        """Given a client that renders the command as table columns (codex does), when
        every expected token appears in the serena row, then the probe PASSes and notes
        the reformatting.
        """
        result, _ = _run_lifecycle(
            probe_module, _probe(probe_module, tmp_path), after_add=(0, "serena  serena   start-mcp-server --context=fake")
        )
        assert result.status == probe_module.Status.PASS
        assert any("reformatted by the client" in note for note in result.notes)

    def test_a_wrong_registered_command_fails_naming_the_missing_parts(self, probe_module, tmp_path) -> None:
        """Given a client whose serena row echoes a different command, when the lifecycle
        runs, then the probe FAILs naming the absent parts, and the rollback still runs.
        """
        result, calls = _run_lifecycle(
            probe_module, _probe(probe_module, tmp_path), after_add=(0, "serena  serena start-mcp-server --context=WRONG")
        )
        assert result.status == probe_module.Status.FAIL
        assert "lacks expected parts: --context=fake" in result.detail
        assert calls[-1] == ("stub", "remove")

    def test_a_token_that_only_prefixes_a_longer_token_does_not_verify(self, probe_module, tmp_path) -> None:
        """Given a reformatted row whose token extends an expected one ('--context=fake-extra'
        for expected '--context=fake'), the probe FAILs naming the missing part — substring
        membership would have accepted the prefix as a match.
        """
        result, _ = _run_lifecycle(
            probe_module, _probe(probe_module, tmp_path), after_add=(0, "serena  serena   start-mcp-server --context=fake-extra")
        )
        assert result.status == probe_module.Status.FAIL
        assert "--context=fake" in result.detail

    def test_a_suffixed_command_fails_even_when_listed_verbatim_but_extended(self, probe_module, tmp_path) -> None:
        """Given a row that lists the expected command verbatim except its last token grew a
        suffix ('--context=fake-extra'), the probe FAILs — the exact-match branch takes this
        path (single-spaced, so it is a plain substring hit) and must enforce token
        boundaries just like the reformatted branch.
        """
        result, _ = _run_lifecycle(probe_module, _probe(probe_module, tmp_path), after_add=(0, f"serena  {EXPECTED_COMMAND}-extra"))
        assert result.status == probe_module.Status.FAIL
        assert "--context=fake" in result.detail

    def test_tokens_on_another_servers_row_do_not_verify_the_registration(self, probe_module, tmp_path) -> None:
        """Given the expected tokens appearing only on another server's row, when the
        lifecycle runs, then the serena registration is not reported as verified.
        """
        listing = "othertool  foo start-mcp-server --context=fake\nserena  serena"
        result, _ = _run_lifecycle(probe_module, _probe(probe_module, tmp_path), after_add=(0, listing))
        assert result.status == probe_module.Status.PASS
        assert not any("expected command" in note for note in result.notes)
        assert any("does not expose command text" in note for note in result.notes)

    def test_output_without_command_text_yields_a_note_not_a_verdict(self, probe_module, tmp_path) -> None:
        """Given a client whose list output carries no command text at all, when the
        lifecycle runs, then the probe PASSes with an explicit not-verifiable note.
        """
        result, _ = _run_lifecycle(probe_module, _probe(probe_module, tmp_path), after_add=(0, "serena"))
        assert result.status == probe_module.Status.PASS
        assert any("does not expose command text" in note for note in result.notes)

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
        assert probe._backup_path is not None and probe._backup_path.is_file()

    @posix_only
    def test_the_clean_path_restores_bytes_and_permissions(self, probe_module, tmp_path) -> None:
        """Given a client that rewrote the config's bytes and loosened its mode, when the
        baseline is verified, then both the bytes and the pre-probe mode return.
        """
        probe, config_path = self._restore_probe(probe_module, tmp_path)
        original = b'{"perm": "test"}'
        config_path.write_bytes(original)
        config_path.chmod(0o600)
        probe._backup_config()
        config_path.write_bytes(b'{"perm": "mutated"}')
        config_path.chmod(0o644)
        assert stat.S_IMODE(config_path.stat().st_mode) == 0o644  # the plant landed
        probe._verify_config_baseline()
        assert config_path.read_bytes() == original
        assert stat.S_IMODE(config_path.stat().st_mode) == 0o600

    @posix_only
    def test_an_emergency_recreate_restores_the_original_mode_not_the_umask(self, probe_module, tmp_path) -> None:
        """Given a client that deleted its config mid-lifecycle, when emergency restore
        recreates it from backup, then the file carries the pre-probe 0600 mode rather
        than whatever the process umask would grant.
        """
        probe, config_path = self._restore_probe(probe_module, tmp_path)
        original = b'{"perm": "test"}'
        config_path.write_bytes(original)
        config_path.chmod(0o600)
        probe._backup_config()
        config_path.unlink()
        assert not config_path.is_file()  # the plant landed
        probe._emergency_restore()
        assert config_path.read_bytes() == original
        assert stat.S_IMODE(config_path.stat().st_mode) == 0o600

    @posix_only
    def test_an_emergency_recreate_restores_a_wider_mode_than_the_temp_files(self, probe_module, tmp_path) -> None:
        """Given a config whose pre-probe mode was 0644, when emergency restore recreates it
        from backup, then it carries 0644 — the atomic temp file starts owner-only, so the
        pre-probe mode must be applied explicitly, not inherited from the temp.
        """
        probe, config_path = self._restore_probe(probe_module, tmp_path)
        original = b'{"perm": "wide"}'
        config_path.write_bytes(original)
        config_path.chmod(0o644)
        probe._backup_config()
        config_path.unlink()
        assert not config_path.is_file()  # the plant landed
        probe._emergency_restore()
        assert config_path.read_bytes() == original
        assert stat.S_IMODE(config_path.stat().st_mode) == 0o644

    @posix_only
    def test_a_symlinked_config_keeps_its_link_and_target_after_restore(self, probe_module, tmp_path) -> None:
        """Given a config managed as a symlink into a dotfiles tree, when emergency restore
        rewrites it, then the link is still a link, its target carries the pre-probe bytes,
        and no regular file has replaced the link — the restore writes through to the
        resolved target.
        """
        dotfiles = tmp_path / "dotfiles"
        dotfiles.mkdir()
        target = dotfiles / "config.json"
        original = b'{"linked": true}'
        target.write_bytes(original)
        link = tmp_path / "config.json"
        link.symlink_to(target)
        probe = _probe(probe_module, tmp_path, link)
        probe._run = lambda argv: probe_module.ExecutedCommand(argv, 0, "", "")
        probe._backup_config()
        target.write_bytes(b'{"mutated": true}')  # the client wrote through the link
        probe._emergency_restore()
        assert link.is_symlink()
        assert target.read_bytes() == original

    @posix_only
    def test_a_link_replaced_by_an_identical_regular_file_is_recreated(self, probe_module, tmp_path) -> None:
        """Given a client that rewrites configs by atomic rename — replacing the symlinked
        config with a regular file whose bytes are IDENTICAL — when the clean lifecycle
        verifies the baseline, then the link is recreated: byte-identity alone must not
        declare the baseline intact while the user's dotfile link is gone.
        """
        dotfiles = tmp_path / "dotfiles"
        dotfiles.mkdir()
        target = dotfiles / "config.json"
        original = b'{"linked": true}'
        target.write_bytes(original)
        link = tmp_path / "config.json"
        link.symlink_to(target)
        probe = _probe(probe_module, tmp_path, link)
        calls = {"lists": 0}

        def link_replacing_run(argv):
            if "setup" in argv:
                link.unlink()
                link.write_bytes(original)  # same bytes, but the link is now a regular file
            if argv == ("stub", "list"):
                calls["lists"] += 1
                return probe_module.ExecutedCommand(argv, 0, f"serena  {EXPECTED_COMMAND}" if calls["lists"] == 2 else "", "")
            return probe_module.ExecutedCommand(argv, 0, "", "")

        probe._run = link_replacing_run
        result = probe.run()
        assert result.status == probe_module.Status.PASS
        assert link.is_symlink()
        assert os.readlink(link) == str(target)
        assert target.read_bytes() == original
        assert any("link was recreated" in note for note in result.notes)

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
