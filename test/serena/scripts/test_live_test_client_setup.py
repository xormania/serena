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
