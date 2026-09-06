from collections.abc import Iterator
from pathlib import Path

import pytest

from solidlsp import SolidLanguageServer
from solidlsp.ls_config import LanguageServerId
from solidlsp.lsp_protocol_handler.lsp_types import Position
from test.conftest import start_ls_context
from test.solidlsp.conftest import find_document_symbol

pytestmark = pytest.mark.python


@pytest.fixture(params=["x", "é", "😀"], ids=["ascii", "bmp", "non_bmp"])
def prefix(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture
def encoding_project(tmp_path: Path, prefix: str) -> Path:
    (tmp_path / "fixture.py").write_text(f'marker = "{prefix}"; target = 1\nresult = target\n', encoding="utf-8")
    (tmp_path / "consumer.py").write_text("from fixture import target\nresult = target\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def encoding_language_server(encoding_project: Path) -> Iterator[SolidLanguageServer]:
    with start_ls_context(ls_id=LanguageServerId.PYTHON, repo_path=str(encoding_project)) as language_server:
        yield language_server


def test_symbol_body_after_unicode(encoding_language_server: SolidLanguageServer) -> None:
    symbol = find_document_symbol(encoding_language_server, "fixture.py", "target")
    assert symbol["body"].get_text() == "target"

    defining_symbol = encoding_language_server.request_defining_symbol("consumer.py", 1, 9)
    assert defining_symbol is not None
    assert defining_symbol["name"] == "target"
    assert defining_symbol["body"].get_text() == "target"


@pytest.mark.parametrize("rename_from", ["declaration", "reference"])
def test_rename_after_unicode(
    encoding_language_server: SolidLanguageServer,
    encoding_project: Path,
    prefix: str,
    rename_from: str,
) -> None:
    language_server = encoding_language_server
    with language_server.open_file("fixture.py") as declaration, language_server.open_file("consumer.py") as consumer:
        # use the server's declaration position or an unambiguous ASCII reference
        if rename_from == "declaration":
            symbol = find_document_symbol(language_server, "fixture.py", "target")
            position = symbol["selectionRange"]["start"]
            relative_path = "fixture.py"
        else:
            position = Position(line=1, character=9)
            relative_path = "consumer.py"
        workspace_edit = language_server.request_rename_symbol_edit(relative_path, position["line"], position["character"], "renamed")
        assert workspace_edit is not None

        # apply the real server edits without changing their coordinates
        changes = dict(workspace_edit.get("changes") or {})
        for change in workspace_edit.get("documentChanges") or []:
            if "textDocument" in change:
                changes[change["textDocument"]["uri"]] = change["edits"]
        for relative_path in ("fixture.py", "consumer.py"):
            uri = (encoding_project / relative_path).as_uri()
            language_server.apply_text_edits_to_file(relative_path, changes[uri])
        assert declaration.contents == f'marker = "{prefix}"; renamed = 1\nresult = renamed\n'
        assert consumer.contents == "from fixture import renamed\nresult = renamed\n"

        # resolve the edited reference against the server's updated document
        defining_symbol = language_server.request_defining_symbol("consumer.py", 1, 9)
        assert defining_symbol is not None
        assert defining_symbol["name"] == "renamed"
        assert defining_symbol["body"].get_text() == "renamed"


def test_incremental_edits_after_unicode(encoding_language_server: SolidLanguageServer, prefix: str) -> None:
    language_server = encoding_language_server
    with language_server.open_file("fixture.py") as file_buffer:
        # insert at the declaration position supplied by the server
        symbol = find_document_symbol(language_server, "fixture.py", "target")
        start = symbol["selectionRange"]["start"]
        cursor = language_server.insert_text_at_position("fixture.py", start["line"], start["character"], "new_")
        assert file_buffer.contents == f'marker = "{prefix}"; new_target = 1\nresult = target\n'
        assert cursor == Position(line=start["line"], character=start["character"] + 4)
        inserted_symbol = find_document_symbol(language_server, "fixture.py", "new_target")
        assert inserted_symbol["body"].get_text() == "new_target"

        # delete the inserted prefix and verify the reference resolves again
        deleted = language_server.delete_text_between_positions("fixture.py", start, cursor)
        assert deleted == "new_"
        assert file_buffer.contents == f'marker = "{prefix}"; target = 1\nresult = target\n'
        defining_symbol = language_server.request_defining_symbol("fixture.py", 1, 9)
        assert defining_symbol is not None
        assert defining_symbol["name"] == "target"
        assert defining_symbol["body"].get_text() == "target"


@pytest.mark.parametrize("line_separator", ["", "\n", "\r\n", "\r"], ids=["single_line", "lf", "crlf", "cr"])
def test_insertion_cursor_uses_protocol_columns(encoding_language_server: SolidLanguageServer, prefix: str, line_separator: str) -> None:
    language_server = encoding_language_server
    inserted = f'prefix = "{prefix}"; '
    if line_separator:
        inserted = f'first = "{prefix}"{line_separator}{inserted}'
    expected_line = 1 if line_separator else 0
    expected_column = len(f'prefix = "{prefix}"; '.encode("utf-16-le")) // 2

    with language_server.open_file("fixture.py") as file_buffer:
        original = file_buffer.contents
        cursor = language_server.insert_text_at_position("fixture.py", 0, 0, inserted)
        assert file_buffer.contents == inserted + original
        assert cursor == Position(line=expected_line, character=expected_column)

        # reuse the returned cursor in both a server query and a local edit
        defining_symbol = language_server.request_defining_symbol("fixture.py", cursor["line"], cursor["character"])
        assert defining_symbol is not None
        assert defining_symbol["name"] == "marker"
        end = language_server.insert_text_at_position("fixture.py", cursor["line"], cursor["character"], "new_")
        assert file_buffer.contents == inserted + "new_" + original
        assert end == Position(line=expected_line, character=expected_column + 4)
