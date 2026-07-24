"""Pinned CUE contract-compiler runtime management."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import platform
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
import zipfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

log = logging.getLogger(__name__)
_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = _REPOSITORY_ROOT / "contract" / "cue-version.json"
DEFAULT_MANAGED_ROOT = Path.home() / ".serena" / "dev_tools" / "cue"
_ALLOWED_DOWNLOAD_HOSTS = frozenset({"github.com", "objects.githubusercontent.com", "release-assets.githubusercontent.com"})


class ChecksumMismatchError(RuntimeError):
    """Error raised when a CUE release archive does not match its pinned digest."""


@dataclass(frozen=True)
class CueRelease:
    """Pinned CUE release metadata."""

    version: str
    assets: Mapping[str, str]

    @classmethod
    def load(cls, path: Path) -> CueRelease:
        """Load and validate release metadata from *path*."""
        # load the pinned metadata
        raw = json.loads(path.read_text(encoding="utf-8"))
        version = raw.get("version")
        assets = raw.get("assets")

        # reject incomplete metadata
        if not isinstance(version, str) or not version.startswith("v"):
            raise ValueError(f"Invalid CUE version in {path}")
        if not isinstance(assets, dict) or not assets:
            raise ValueError(f"Invalid CUE asset map in {path}")
        if not all(isinstance(name, str) and isinstance(digest, str) and len(digest) == 64 for name, digest in assets.items()):
            raise ValueError(f"Invalid CUE asset digest in {path}")

        return cls(version=version, assets=assets)


@dataclass(frozen=True)
class CueRuntime:
    """Pinned CUE toolchain used to compile the repository contract."""

    config_path: Path = DEFAULT_CONFIG_PATH
    managed_root: Path = DEFAULT_MANAGED_ROOT

    @property
    def release(self) -> CueRelease:
        """Release metadata for this runtime."""
        return CueRelease.load(self.config_path)

    def _asset_name(self) -> str:
        """Release asset name for the current operating system and architecture."""
        # normalize the operating system
        system = platform.system().lower()
        system_names = {"linux": "linux", "darwin": "darwin", "windows": "windows"}
        if system not in system_names:
            raise RuntimeError(f"Unsupported CUE operating system: {platform.system()}")

        # normalize the machine architecture
        machine = platform.machine().lower()
        if machine in {"x86_64", "amd64"}:
            architecture = "amd64"
        elif machine in {"aarch64", "arm64"}:
            architecture = "arm64"
        else:
            raise RuntimeError(f"Unsupported CUE architecture: {platform.machine()}")

        extension = ".zip" if system == "windows" else ".tar.gz"
        return f"cue_{self.release.version}_{system_names[system]}_{architecture}{extension}"

    def _managed_binary(self) -> Path:
        """Managed binary path for the pinned release."""
        executable = "cue.exe" if os.name == "nt" else "cue"
        return self.managed_root / self.release.version / executable

    def _is_compatible(self, binary: Path) -> bool:
        """Whether *binary* runs and reports the pinned version."""
        if not binary.is_file():
            return False

        try:
            completed = subprocess.run([binary, "version"], check=False, capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.SubprocessError):
            return False

        return completed.returncode == 0 and self.release.version in completed.stdout

    @staticmethod
    def _sha256(path: Path) -> str:
        """Hexadecimal SHA-256 digest for *path*."""
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _extract_binary(archive_path: Path, asset_name: str, destination: Path) -> None:
        """Extract only the CUE executable from a release archive."""
        expected_name = "cue.exe" if asset_name.endswith(".zip") else "cue"

        # extract a regular ZIP member by basename
        if asset_name.endswith(".zip"):
            with zipfile.ZipFile(archive_path) as archive:
                candidates = [
                    member for member in archive.infolist() if not member.is_dir() and Path(member.filename).name == expected_name
                ]
                if len(candidates) != 1:
                    raise ValueError(f"Expected one {expected_name} in {asset_name}, found {len(candidates)}")
                with archive.open(candidates[0]) as source, destination.open("wb") as target:
                    shutil.copyfileobj(source, target)
            return

        # extract a regular tar member by basename
        with tarfile.open(archive_path, "r:*") as archive:
            candidates = [member for member in archive.getmembers() if member.isfile() and Path(member.name).name == expected_name]
            if len(candidates) != 1:
                raise ValueError(f"Expected one {expected_name} in {asset_name}, found {len(candidates)}")
            source = archive.extractfile(candidates[0])
            if source is None:
                raise ValueError(f"Could not read {expected_name} from {asset_name}")
            with source, destination.open("wb") as target:
                shutil.copyfileobj(source, target)

    def install_from_archive(
        self,
        archive_path: Path,
        *,
        asset_name: str,
        expected_sha256: str,
    ) -> Path:
        """Install a verified CUE binary from an already-downloaded archive."""
        # verify before extracting any bytes
        actual_sha256 = self._sha256(archive_path)
        if actual_sha256 != expected_sha256:
            raise ChecksumMismatchError(f"CUE archive sha256 mismatch for {asset_name}: expected {expected_sha256}, got {actual_sha256}")

        # extract into an isolated temporary directory
        target = self._managed_binary()
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="cue-install-", dir=self.managed_root) as temporary_directory:
            temporary_binary = Path(temporary_directory) / target.name
            self._extract_binary(archive_path, asset_name, temporary_binary)
            temporary_binary.chmod(0o755)
            os.replace(temporary_binary, target)

        return target

    def install(self) -> Path:
        """Download, verify, and atomically install the pinned CUE binary."""
        # reuse a compatible managed binary
        target = self._managed_binary()
        if self._is_compatible(target):
            return target

        # select the pinned release asset
        asset_name = self._asset_name()
        try:
            expected_sha256 = self.release.assets[asset_name]
        except KeyError as error:
            raise RuntimeError(f"No pinned digest for CUE asset {asset_name}") from error
        url = f"https://github.com/cue-lang/cue/releases/download/{self.release.version}/{asset_name}"

        # download to a temporary file without exposing partial installs
        self.managed_root.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(url, headers={"User-Agent": "serena-lsp-contract"})
        temporary_archive: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                prefix="cue-download-",
                suffix=Path(asset_name).suffix,
                dir=self.managed_root,
                delete=False,
            ) as stream:
                temporary_archive = Path(stream.name)
                with urllib.request.urlopen(request, timeout=60) as response:
                    hostname = urlparse(response.geturl()).hostname
                    if hostname not in _ALLOWED_DOWNLOAD_HOSTS:
                        raise RuntimeError(f"CUE release redirected to disallowed host: {hostname}")
                    shutil.copyfileobj(response, stream)

            return self.install_from_archive(temporary_archive, asset_name=asset_name, expected_sha256=expected_sha256)
        finally:
            if temporary_archive is not None:
                temporary_archive.unlink(missing_ok=True)

    def locate(self) -> Path:
        """Return a verified compatible CUE binary, installing it when absent."""
        # honor an explicit compatible override without fallback
        override = os.environ.get("SERENA_CUE")
        if override:
            binary = Path(override).expanduser().resolve()
            if not self._is_compatible(binary):
                raise RuntimeError(f"SERENA_CUE does not report {self.release.version}: {binary}")
            return binary

        # repair absent or stale managed state through the verified installer
        binary = self._managed_binary()
        if self._is_compatible(binary):
            return binary
        if binary.exists():
            log.warning("Replacing incompatible managed CUE binary at %s", binary)
        return self.install()

    def run(self, args: Sequence[str], input_files: Sequence[Path] = ()) -> tuple[int, str, str]:
        """Run CUE with arguments and optional input files."""
        command = [str(self.locate()), *args, *(str(path) for path in input_files)]
        completed = subprocess.run(command, cwd=_REPOSITORY_ROOT, check=False, capture_output=True, text=True)
        return completed.returncode, completed.stdout, completed.stderr


def locate() -> Path:
    """Return the repository's pinned CUE binary."""
    return CueRuntime().locate()


def install() -> Path:
    """Install and return the repository's pinned CUE binary."""
    return CueRuntime().install()


def run(args: Sequence[str], input_files: Sequence[Path] = ()) -> tuple[int, str, str]:
    """Run the repository's pinned CUE binary."""
    return CueRuntime().run(args, input_files)
