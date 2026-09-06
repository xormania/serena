from solidlsp.ls_exceptions import InvalidTextLocationError
from solidlsp.lsp_protocol_handler.lsp_types import PositionEncodingKind


class LSPPositionConverter:
    """Convert columns between LSP code units and Python code points for a snapshot of file lines."""

    def __init__(self, lines: list[str], encoding: PositionEncodingKind = PositionEncodingKind.UTF16):
        self.lines = lines
        self._encoding = encoding

    def _get_line(self, line: int, column: int) -> str:
        if line < 0 or column < 0:
            raise InvalidTextLocationError(f"Negative position: {line=}, {column=}")
        if line == len(self.lines) and column == 0:
            # retain the whole-line EOF position used by text insertion and deletion
            return ""
        if line >= len(self.lines):
            raise InvalidTextLocationError(f"Position outside file: {line=}, {column=}")
        return self.lines[line].removesuffix("\n").removesuffix("\r")

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
        text = self._get_line(line, column)
        if text.isascii() or self._encoding == PositionEncodingKind.UTF32:
            return min(column, len(text))

        # reject positions inside an encoded character instead of editing a neighbouring character
        units = 0
        for index, char in enumerate(text):
            if units == column:
                return index
            units += self._code_units(char)
            if units > column:
                raise InvalidTextLocationError(f"Position splits a {self._encoding.value} character: {line=}, {column=}")
        return len(text)

    def to_lsp_column(self, line: int, column: int) -> int:
        """Convert a Python string offset to an LSP column, clamping offsets beyond the line end."""
        text = self._get_line(line, column)
        if text.isascii() or self._encoding == PositionEncodingKind.UTF32:
            return min(column, len(text))
        return sum(self._code_units(char) for char in text[:column])
