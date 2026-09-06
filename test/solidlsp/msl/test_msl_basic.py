"""
Basic integration tests for the mSL (mIRC Scripting Language) language server.

Tests validate document symbols, references, and definitions for aliases, events,
raw events, menus, dialogs, and CTCP handlers using the mSL test repository.
"""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest

from solidlsp import SolidLanguageServer
from solidlsp.ls_config import LanguageServerId
from test.conftest import start_ls_context
from test.solidlsp.conftest import format_symbol_for_assert, has_malformed_name, request_all_symbols

pytestmark = [pytest.mark.msl]


class TestMslDocumentSymbols:
    """Test document symbol retrieval for mSL constructs."""

    @pytest.mark.parametrize("language_server", [LanguageServerId.MSL], indirect=True)
    def test_ls_is_running(self, language_server: SolidLanguageServer) -> None:
        """Test that the language server starts successfully."""
        assert language_server.is_running()

    @pytest.mark.parametrize("language_server", [LanguageServerId.MSL], indirect=True)
    def test_document_symbols_main(self, language_server: SolidLanguageServer) -> None:
        """Test that document symbols are returned for the main file."""
        doc_symbols = language_server.request_document_symbols("main.mrc")
        all_symbols, root_symbols = doc_symbols.get_all_symbols_and_roots()

        symbol_names = [s.get("name") for s in all_symbols if s.get("name")]
        assert "greet" in symbol_names, f"greet alias not found. Found: {symbol_names}"
        assert "calculate.doubloons" in symbol_names, f"calculate.doubloons alias not found. Found: {symbol_names}"
        assert "show.player.info" in symbol_names, f"show.player.info alias not found. Found: {symbol_names}"

    @pytest.mark.parametrize("language_server", [LanguageServerId.MSL], indirect=True)
    def test_document_symbols_events(self, language_server: SolidLanguageServer) -> None:
        """Test that event handlers, raw events, and menus are detected in the main file."""
        doc_symbols = language_server.request_document_symbols("main.mrc")
        all_symbols, root_symbols = doc_symbols.get_all_symbols_and_roots()

        symbol_names = [s.get("name") for s in all_symbols if s.get("name")]
        # Check for on *:TEXT and on *:JOIN events
        on_events = [n for n in symbol_names if n.startswith("on ")]
        assert len(on_events) >= 2, f"Expected at least 2 event handlers. Found: {on_events}"
        # Check for raw event
        raw_events = [n for n in symbol_names if n.startswith("raw ")]
        assert len(raw_events) >= 1, f"Expected at least 1 raw event handler. Found: {raw_events}"
        # Check for menu
        menus = [n for n in symbol_names if n.startswith("menu ")]
        assert len(menus) >= 1, f"Expected at least 1 menu. Found: {menus}"

    @pytest.mark.parametrize("language_server", [LanguageServerId.MSL], indirect=True)
    def test_document_symbols_utils(self, language_server: SolidLanguageServer) -> None:
        """Test that document symbols are returned for the utils file."""
        doc_symbols = language_server.request_document_symbols("utils.mrc")
        all_symbols, root_symbols = doc_symbols.get_all_symbols_and_roots()

        symbol_names = [s.get("name") for s in all_symbols if s.get("name")]
        assert "format.coins" in symbol_names, f"format.coins alias not found. Found: {symbol_names}"
        assert "is.admin" in symbol_names, f"is.admin alias not found. Found: {symbol_names}"
        assert "welcome.message" in symbol_names, f"welcome.message alias not found. Found: {symbol_names}"

    @pytest.mark.parametrize("language_server", [LanguageServerId.MSL], indirect=True)
    def test_document_symbols_dialog_and_ctcp(self, language_server: SolidLanguageServer) -> None:
        """Test that dialog and CTCP handler definitions are detected."""
        doc_symbols = language_server.request_document_symbols("utils.mrc")
        all_symbols, root_symbols = doc_symbols.get_all_symbols_and_roots()

        symbol_names = [s.get("name") for s in all_symbols if s.get("name")]
        assert "dialog settings" in symbol_names, f"dialog settings not found. Found: {symbol_names}"
        # Check for CTCP handler
        ctcp_events = [n for n in symbol_names if n.startswith("ctcp ")]
        assert len(ctcp_events) >= 1, f"Expected at least 1 ctcp handler. Found: {ctcp_events}"

    @pytest.mark.parametrize("language_server", [LanguageServerId.MSL], indirect=True)
    def test_find_symbol(self, language_server: SolidLanguageServer) -> None:
        """Test that the full symbol tree contains expected symbols from both files."""
        from solidlsp.ls_utils import SymbolUtils

        symbols = language_server.request_full_symbol_tree()
        assert SymbolUtils.symbol_tree_contains_name(symbols, "greet"), "greet not found in symbol tree"
        assert SymbolUtils.symbol_tree_contains_name(symbols, "format.coins"), "format.coins not found in symbol tree"
        assert SymbolUtils.symbol_tree_contains_name(symbols, "show.player.info"), "show.player.info not found in symbol tree"

    @pytest.mark.parametrize("language_server", [LanguageServerId.MSL], indirect=True)
    def test_bare_symbol_names(self, language_server: SolidLanguageServer) -> None:
        """Test that symbol names do not contain unexpected formatting characters."""
        all_symbols = request_all_symbols(language_server)
        malformed_symbols = []
        for s in all_symbols:
            # mSL symbols can contain periods (e.g., calculate.doubloons) and
            # colons/spaces in event names (e.g., "on *:TEXT"), so allow those
            if has_malformed_name(s, period_allowed=True, colon_allowed=True, whitespace_allowed=True):
                malformed_symbols.append(s)
        if malformed_symbols:
            pytest.fail(
                f"Found malformed symbols: {[format_symbol_for_assert(sym) for sym in malformed_symbols]}",
                pytrace=False,
            )

    @pytest.mark.parametrize("language_server", [LanguageServerId.MSL], indirect=True)
    def test_find_references_within_file(self, language_server: SolidLanguageServer) -> None:
        """Test that references to 'greet' are found within main.mrc."""
        file_path = "main.mrc"
        all_symbols, _ = language_server.request_document_symbols(file_path).get_all_symbols_and_roots()
        greet_symbol = next((s for s in all_symbols if s.get("name") == "greet"), None)
        assert greet_symbol is not None, "Could not find 'greet' symbol in main.mrc"

        sel_start = greet_symbol["selectionRange"]["start"]
        refs = language_server.request_references(file_path, sel_start["line"], sel_start["character"])

        assert refs, f"Expected non-empty references for greet but got {refs=}"

        actual_locations = [
            {
                "uri_suffix": os.path.basename(ref.get("relativePath", ref.get("uri", ""))),
                "line": ref["range"]["start"]["line"],
            }
            for ref in refs
        ]

        # greet is called on line 13 (0-indexed) in main.mrc: `greet $nick`
        call_site = {"uri_suffix": "main.mrc", "line": 13}
        assert call_site in actual_locations, f"Expected reference to greet at line 13 in main.mrc, got {actual_locations}"

    @pytest.mark.parametrize("language_server", [LanguageServerId.MSL], indirect=True)
    def test_find_references_across_files(self, language_server: SolidLanguageServer) -> None:
        """Test that references to 'format.coins' are found across main.mrc and utils.mrc."""
        # format.coins is defined in utils.mrc but called in both main.mrc and utils.mrc
        file_path = "utils.mrc"
        all_symbols, _ = language_server.request_document_symbols(file_path).get_all_symbols_and_roots()
        fc_symbol = next((s for s in all_symbols if s.get("name") == "format.coins"), None)
        assert fc_symbol is not None, "Could not find 'format.coins' symbol in utils.mrc"

        sel_start = fc_symbol["selectionRange"]["start"]
        refs = language_server.request_references(file_path, sel_start["line"], sel_start["character"])

        assert refs, f"Expected non-empty references for format.coins but got {refs=}"

        actual_locations = [
            {
                "uri_suffix": os.path.basename(ref.get("relativePath", ref.get("uri", ""))),
                "line": ref["range"]["start"]["line"],
            }
            for ref in refs
        ]

        # Verify cross-file: at least one reference is in main.mrc (different file from definition)
        main_refs = [loc for loc in actual_locations if loc["uri_suffix"] == "main.mrc"]
        assert len(main_refs) >= 1, f"Expected at least 1 reference in main.mrc, got {main_refs}"

    @pytest.mark.parametrize("language_server", [LanguageServerId.MSL], indirect=True)
    def test_workspace_symbol(self, language_server: SolidLanguageServer) -> None:
        """Test that workspace symbol search returns results."""
        result = language_server.request_workspace_symbol("greet")
        assert result is not None, "Workspace symbol search returned None"
        assert len(result) > 0, "Workspace symbol search returned no results"
        assert any("greet" in str(s.get("name", "")) for s in result), f"Expected at least one result containing 'greet', got {result}"


@pytest.fixture(params=["plain", "é", "😀😀😀"], ids=["ascii", "bmp", "non_bmp"])
def unicode_prefix(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture(params=["\n", "\r\n"], ids=["lf", "crlf"])
def line_ending(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture
def unicode_project(tmp_path: Path, unicode_prefix: str, line_ending: str) -> Path:
    definitions = line_ending.join([f"alias foo {{ echo {unicode_prefix} }}", f"on *:TEXT:{unicode_prefix}:#:{{ echo handled }}"])
    calls = line_ending.join(["alias caller {", f"  echo {unicode_prefix} | foo", "}"])
    (tmp_path / "definitions.mrc").write_bytes(definitions.encode("utf-8"))
    (tmp_path / "calls.mrc").write_bytes(calls.encode("utf-8"))
    return tmp_path


@pytest.fixture
def unicode_language_server(unicode_project: Path) -> Iterator[SolidLanguageServer]:
    with start_ls_context(ls_id=LanguageServerId.MSL, repo_path=str(unicode_project)) as language_server:
        yield language_server


@pytest.mark.parametrize(
    "unicode_prefix",
    ["plain", "é", "😀😀😀", "A\u0085B\u2028C\u2029D"],
    ids=["ascii", "bmp", "non_bmp", "unicode_separators"],
    indirect=True,
)
def test_unicode_symbol_ranges(unicode_language_server: SolidLanguageServer, unicode_prefix: str) -> None:
    language_server = unicode_language_server
    symbols = language_server.request_document_symbols("definitions.mrc").root_symbols
    alias, event = symbols
    alias_text = f"alias foo {{ echo {unicode_prefix} }}"
    event_text = f"on *:TEXT:{unicode_prefix}:#:{{ echo handled }}"
    event_header = f"on *:TEXT:{unicode_prefix}:#:{{"

    assert "body" in alias and "location" in alias
    assert "body" in event and "location" in event and "selectionRange" in event
    assert alias["body"].get_text() == alias_text
    assert event["body"].get_text() == event_text
    assert alias["location"]["range"]["end"] == {"line": 0, "character": len(alias_text.encode("utf-16-le")) // 2}
    assert event["selectionRange"] == {
        "start": {"line": 1, "character": 0},
        "end": {"line": 1, "character": len(event_header.encode("utf-16-le")) // 2},
    }

    # workspace and non-alias reference responses carry the same protocol ranges
    workspace_symbols = language_server.request_workspace_symbol(event["name"])
    assert workspace_symbols is not None
    assert len(workspace_symbols) == 1
    assert "location" in workspace_symbols[0]
    assert workspace_symbols[0]["location"]["range"] == event["location"]["range"]
    references = language_server.request_references("definitions.mrc", 1, 0)
    assert len(references) == 1
    assert references[0]["range"] == event["location"]["range"]


@pytest.mark.parametrize(
    "unicode_prefix",
    ["plain", "é", "😀😀😀", "A\u0085B\u2028C\u2029D"],
    ids=["ascii", "bmp", "non_bmp", "unicode_separators"],
    indirect=True,
)
def test_unicode_lookup_positions(unicode_language_server: SolidLanguageServer, unicode_prefix: str) -> None:
    language_server = unicode_language_server
    call_start = len(f"  echo {unicode_prefix} | ".encode("utf-16-le")) // 2

    # query a call on a separate line so the declaration cannot mask its column
    definitions = language_server.request_definition("calls.mrc", 1, call_start)
    assert len(definitions) == 1
    assert definitions[0]["relativePath"] == "definitions.mrc"
    assert definitions[0]["range"] == {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 11}}
    hover = language_server.request_hover("calls.mrc", 1, call_start)
    assert hover is not None
    assert "foo" in str(hover["contents"])
    references = language_server.request_references("calls.mrc", 1, call_start)
    assert sorted((reference["relativePath"], reference["range"]) for reference in references) == [
        ("calls.mrc", {"start": {"line": 1, "character": call_start}, "end": {"line": 1, "character": call_start + 3}}),
        ("definitions.mrc", {"start": {"line": 0, "character": 6}, "end": {"line": 0, "character": 9}}),
    ]


def test_unicode_incremental_edit(
    unicode_language_server: SolidLanguageServer,
    unicode_project: Path,
    unicode_prefix: str,
) -> None:
    language_server = unicode_language_server
    alias_text = f"alias foo {{ echo {unicode_prefix} }}"
    original = (unicode_project / "definitions.mrc").read_bytes()
    with language_server.open_file("definitions.mrc") as file_buffer:
        original_contents = file_buffer.contents
        symbol = language_server.request_document_symbols("definitions.mrc", file_buffer).root_symbols[0]
        assert "location" in symbol
        end = symbol["location"]["range"]["end"]

        # insert after the complete symbol, then query the server's edited document
        cursor = language_server.insert_text_at_position("definitions.mrc", end["line"], end["character"], " ; appended")
        expected = original_contents.replace(alias_text, alias_text + " ; appended", 1)
        assert file_buffer.contents == expected
        assert cursor == {"line": 0, "character": len((alias_text + " ; appended").encode("utf-16-le")) // 2}
        symbols = language_server.request_document_symbols("definitions.mrc", file_buffer).root_symbols
        assert "body" in symbols[0] and "body" in symbols[1]
        assert symbols[0]["body"].get_text() == alias_text
        assert symbols[1]["body"].get_text() == f"on *:TEXT:{unicode_prefix}:#:{{ echo handled }}"

        # deletion must use the same units and restore the buffer snapshot
        assert language_server.delete_text_between_positions("definitions.mrc", end, cursor) == " ; appended"
        assert file_buffer.contents == original_contents
    assert (unicode_project / "definitions.mrc").read_bytes() == original
    reopened = language_server.request_document_symbols("definitions.mrc").root_symbols[0]
    assert "body" in reopened
    assert reopened["body"].get_text() == alias_text


@pytest.mark.parametrize(
    "contents,end",
    [
        ("", {"line": 0, "character": 0}),
        ("; first\n; last", {"line": 1, "character": 6}),
        ("; first\n; last\n", {"line": 2, "character": 0}),
        ("; 😀", {"line": 0, "character": 4}),
    ],
    ids=["empty", "no_final_newline", "final_newline", "non_bmp"],
)
def test_file_symbol_end(tmp_path: Path, contents: str, end: dict[str, int]) -> None:
    (tmp_path / "file.mrc").write_bytes(contents.encode("utf-8"))
    with start_ls_context(ls_id=LanguageServerId.MSL, repo_path=str(tmp_path)) as language_server:
        tree = language_server.request_full_symbol_tree()
        file_symbol = tree[0]["children"][0]
        expected = {"start": {"line": 0, "character": 0}, "end": end}
        assert "location" in file_symbol and "selectionRange" in file_symbol
        assert file_symbol["location"]["relativePath"] == "file.mrc"
        assert file_symbol["location"]["range"] == expected
        assert file_symbol["selectionRange"] == expected
