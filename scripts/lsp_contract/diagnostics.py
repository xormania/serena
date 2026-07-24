"""Stable diagnostics for contract extraction and validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExtractionError(RuntimeError):
    """Error raised when a repository source shape cannot be extracted safely."""

    path: Path
    line: int
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"
