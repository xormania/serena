import pytest

from solidlsp.ls_config import LanguageServerId
from solidlsp.ls_exceptions import InvalidTextLocationError, SolidLSPException
from solidlsp.ls_process import LanguageServerInterface
from solidlsp.lsp_protocol_handler.lsp_types import PositionEncodingKind
from solidlsp.position_encoding import LSPPositionConverter


@pytest.mark.parametrize(
    "encoding,columns",
    [
        (PositionEncodingKind.UTF16, [0, 1, 2, 4, 6, 7]),
        (PositionEncodingKind.UTF8, [0, 1, 3, 7, 11, 12]),
        (PositionEncodingKind.UTF32, [0, 1, 2, 3, 4, 5]),
    ],
)
def test_position_columns_round_trip(encoding: PositionEncodingKind, columns: list[int]) -> None:
    positions = LSPPositionConverter(["aé😀𐐀z"], encoding)
    for python_column, protocol_column in enumerate(columns):
        assert positions.to_lsp_column(0, python_column) == protocol_column
        assert positions.to_python_column(0, protocol_column) == python_column


@pytest.mark.parametrize("line", ["plain", "é😀", "", "é😀\r"])
def test_position_columns_clamp_to_line_end(line: str) -> None:
    positions = LSPPositionConverter([line])
    content = line.removesuffix("\r")
    assert positions.to_python_column(0, 999) == len(content)
    assert positions.to_lsp_column(0, 999) == len(content.encode("utf-16-le")) // 2


@pytest.mark.parametrize("encoding,column", [(PositionEncodingKind.UTF16, 2), (PositionEncodingKind.UTF8, 2)])
def test_position_inside_encoded_character_is_rejected(encoding: PositionEncodingKind, column: int) -> None:
    positions = LSPPositionConverter(["a😀z"], encoding)
    with pytest.raises(InvalidTextLocationError):
        positions.to_python_column(0, column)


def test_position_at_start_of_line_after_eof() -> None:
    positions = LSPPositionConverter(["a😀"])
    assert positions.to_python_column(1, 0) == 0
    assert positions.to_lsp_column(1, 0) == 0


@pytest.mark.parametrize("line,column", [(-1, 0), (0, -1), (1, 1), (2, 0)])
def test_invalid_position_is_rejected(line: int, column: int) -> None:
    positions = LSPPositionConverter(["a😀"])
    with pytest.raises(InvalidTextLocationError):
        positions.to_python_column(line, column)
    with pytest.raises(InvalidTextLocationError):
        positions.to_lsp_column(line, column)


class _InitializingServer(LanguageServerInterface):
    """In-process protocol peer returning a configurable initialize result."""

    def __init__(self, capabilities: dict):
        super().__init__(LanguageServerId.PYTHON, lambda _: 0)
        self.capabilities = capabilities

    def is_running(self) -> bool:
        return True

    def _start(self) -> None:
        pass

    def _stop(self, timeout: float) -> None:
        pass

    def _send_payload(self, payload: dict) -> None:
        self._receive_payload({"jsonrpc": "2.0", "id": payload["id"], "result": {"capabilities": self.capabilities}})


@pytest.mark.parametrize("encoding", list(PositionEncodingKind))
def test_initialize_records_selected_position_encoding(encoding: PositionEncodingKind) -> None:
    server = _InitializingServer({"positionEncoding": encoding.value})
    assert server.position_encoding == PositionEncodingKind.UTF16
    result = server.send_request("initialize", {"capabilities": {"general": {"positionEncodings": [encoding.value]}}})
    assert result == {"capabilities": {"positionEncoding": encoding.value}}
    assert server.position_encoding == encoding

    # a subsequent initialization without a selection must restore the protocol default
    server.capabilities = {}
    server.send_request("initialize", {"capabilities": {}})
    assert server.position_encoding == PositionEncodingKind.UTF16


@pytest.mark.parametrize("encoding", ["utf-8", "utf-32", "unknown"])
def test_initialize_rejects_unadvertised_position_encoding(encoding: str) -> None:
    server = _InitializingServer({"positionEncoding": encoding})
    with pytest.raises(SolidLSPException, match="unadvertised position encoding"):
        server.send_request("initialize", {"capabilities": {}})


def test_initialize_rejects_unknown_position_encoding() -> None:
    server = _InitializingServer({"positionEncoding": "unknown"})
    with pytest.raises(SolidLSPException, match="Unsupported language server position encoding"):
        server.send_request("initialize", {"capabilities": {"general": {"positionEncodings": ["unknown"]}}})
