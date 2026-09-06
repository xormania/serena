from array import array
from bisect import bisect_left
from collections.abc import Sequence

from solidlsp.ls_exceptions import InvalidTextLocationError
from solidlsp.lsp_protocol_handler.lsp_types import PositionEncodingKind


class LSPPositionConverter:
    """
    Convert columns between LSP code units and Python code points for a snapshot of file lines.

    Boundary tables are built once per queried line and shared by both conversion directions.
    """

    def __init__(self, lines: list[str], encoding: PositionEncodingKind = PositionEncodingKind.UTF16):
        self.lines = list(lines)
        self._encoding = encoding
        self._line_offsets: dict[int, Sequence[int]] = {}

    def _get_line_offsets(self, line: int, column: int) -> Sequence[int]:
        if line < 0 or column < 0:
            raise InvalidTextLocationError(f"Negative position: {line=}, {column=}")
        if line == len(self.lines) and column == 0:
            # retain the whole-line EOF position used by text insertion and deletion
            return range(1)
        if line >= len(self.lines):
            raise InvalidTextLocationError(f"Position outside file: {line=}, {column=}")
        if line in self._line_offsets:
            return self._line_offsets[line]

        # inspect and trim a line only once, including on the identity path
        text = self.lines[line].removesuffix("\n").removesuffix("\r")
        if self._encoding == PositionEncodingKind.UTF32 or text.isascii():
            offsets: Sequence[int] = range(len(text) + 1)
        else:
            # store one compact boundary per code point, not one entry per code unit
            boundaries = array("Q", [0])
            for char in text:
                boundaries.append(boundaries[-1] + self._code_units(char))
            offsets = boundaries

        # publish only the completed table so concurrent readers cannot observe a partial index
        self._line_offsets[line] = offsets
        return offsets

    def _code_units(self, char: str) -> int:
        value = ord(char)
        if self._encoding == PositionEncodingKind.UTF16:
            return 2 if value > 0xFFFF else 1
        if self._encoding == PositionEncodingKind.UTF8:
            if value <= 0x7F:
                return 1
            if value <= 0x7FF:
                return 2
            return 3 if value <= 0xFFFF else 4
        return 1

    def to_python_column(self, line: int, column: int) -> int:
        """
        Convert an LSP column to a Python string offset, clamping columns beyond the line end.

        :raises InvalidTextLocationError: if the position splits an encoded character or has an invalid line or negative column
        """
        offsets = self._get_line_offsets(line, column)
        if isinstance(offsets, range):
            return min(column, len(offsets) - 1)
        if column >= offsets[-1]:
            return len(offsets) - 1

        # reject positions inside an encoded character instead of editing a neighbouring character
        index = bisect_left(offsets, column)
        if offsets[index] != column:
            raise InvalidTextLocationError(f"Position splits a {self._encoding.value} character: {line=}, {column=}")
        return index

    def to_lsp_column(self, line: int, column: int) -> int:
        """Convert a Python string offset to an LSP column, clamping offsets beyond the line end."""
        offsets = self._get_line_offsets(line, column)
        return offsets[min(column, len(offsets) - 1)]
