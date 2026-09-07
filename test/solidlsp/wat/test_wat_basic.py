"""Behavior tests for the WAT language-server integration."""

import json
import logging
import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest

from serena.agent import SerenaAgent
from serena.config.serena_config import SerenaConfig
from serena.tools.symbol_tools import FindSymbolTool, RenameSymbolTool
from solidlsp import SolidLanguageServer
from solidlsp.ls_config import LanguageServerId
from solidlsp.ls_types import Position, SymbolKind
from test.conftest import get_repo_path, start_ls_context

pytestmark = pytest.mark.wat


@pytest.fixture(scope="module")
def wat_server(tmp_path_factory: pytest.TempPathFactory) -> Iterator[SolidLanguageServer]:
    repo = tmp_path_factory.mktemp("wat")
    shutil.copytree(get_repo_path(LanguageServerId.WAT), repo, dirs_exist_ok=True)
    shutil.copyfile(repo / "arithmetic.wat", repo / "independent.wat")
    with start_ls_context(LanguageServerId.WAT, repo_path=str(repo)) as server:
        yield server


def test_document_symbols_and_complete_bodies(wat_server: SolidLanguageServer) -> None:
    symbols, roots = wat_server.request_document_symbols("arithmetic.wat").get_all_symbols_and_roots()
    assert [(s["name"], s["kind"]) for s in roots] == [("$arithmetic", SymbolKind.Module)]
    assert [s["name"] for s in roots[0]["children"]] == ["$add", "$twice", "$numeric", "func 3"]
    by_name = {s["name"]: s for s in symbols}
    add_body = by_name["$add"].get("body")
    assert add_body is not None
    assert add_body.get_text() == (
        "(func $add (param $left i32) (param $right i32) (result i32)\n    local.get $left\n    local.get $right\n    i32.add)"
    )
    anonymous_body = by_name["func 3"].get("body")
    assert anonymous_body is not None
    assert anonymous_body.get_text() == "(func (result i32)\n    i32.const 7)"
    assert by_name["$add"].get("selectionRange") == {"start": {"line": 1, "character": 8}, "end": {"line": 1, "character": 12}}


@pytest.mark.parametrize("line", [9, 14], ids=["named", "numeric"])
def test_definition_from_named_and_numeric_calls(wat_server: SolidLanguageServer, line: int) -> None:
    definitions = wat_server.request_definition("arithmetic.wat", line, 9)
    assert [(d["relativePath"], d["range"]) for d in definitions] == [
        ("arithmetic.wat", {"start": {"line": 1, "character": 8}, "end": {"line": 1, "character": 12}})
    ]


def test_references_are_confined_to_the_document(wat_server: SolidLanguageServer) -> None:
    # open a second module with identically named declarations to check isolation
    with wat_server.open_file("independent.wat"):
        references = wat_server.request_references("arithmetic.wat", 1, 8)
    assert {(r["relativePath"], r["range"]["start"]["line"], r["range"]["start"]["character"]) for r in references} == {
        ("arithmetic.wat", 9, 9),
        ("arithmetic.wat", 14, 9),
    }


@pytest.mark.parametrize("prefix", ["", "(; café ;) "], ids=["ascii", "bmp"])
@pytest.mark.parametrize("newline", ["\n", "\r\n"], ids=["lf", "crlf-disk-input"])
def test_rename_preserves_numeric_calls_and_unrelated_text(wat_server: SolidLanguageServer, prefix: str, newline: str) -> None:
    # load a separate document for each case; SolidLSP normalizes disk newlines to LF
    filename = f"rename_{len(prefix)}_{len(newline)}.wat"
    original = (
        f"(module\n  {prefix}(func $add (result i32) i32.const 1)\n"
        "  (func $adder (result i32) call $add)\n"
        "  (func (result i32) call 0)\n  ;; $add in a comment must stay unchanged\n)\n"
    )
    path = Path(wat_server.repository_root_path) / filename
    path.write_bytes(original.replace("\n", newline).encode("utf-8"))
    expected = original.replace("(func $add ", "(func $sum ").replace("call $add)", "call $sum)")
    with wat_server.open_file(filename) as buffer:
        edit = wat_server.request_rename_symbol_edit(filename, 2, 34, "$sum")
        assert edit is not None
        changes = edit.get("changes")
        assert changes is not None
        assert set(changes) == {path.as_uri()}
        wat_server.apply_text_edits_to_file(filename, changes[path.as_uri()])
        assert buffer.contents == expected
        definitions = wat_server.request_definition(filename, 2, 34)
        assert len(definitions) == 1
        assert definitions[0]["range"]["start"] == {"line": 1, "character": 8 + len(prefix)}
        symbols = wat_server.request_document_symbols(filename).get_all_symbols_and_roots()[0]
        assert "$sum" in [s["name"] for s in symbols]
        assert "$adder" in [s["name"] for s in symbols]


def test_document_changes_refresh_symbols(wat_server: SolidLanguageServer) -> None:
    filename = "changes.wat"
    path = Path(wat_server.repository_root_path) / filename
    path.write_text("(module\n  (func $one)\n)\n", encoding="utf-8")
    with wat_server.open_file(filename) as buffer:
        wat_server.insert_text_at_position(filename, 2, 0, "  (func $two)\n")
        symbols = wat_server.request_document_symbols(filename).get_all_symbols_and_roots()[0]
        assert [s["name"] for s in symbols if s["kind"] == SymbolKind.Function] == ["$one", "$two"]
        wat_server.delete_text_between_positions(filename, Position(line=2, character=0), Position(line=3, character=0))
        assert buffer.contents == "(module\n  (func $one)\n)\n"
        symbols = wat_server.request_document_symbols(filename).get_all_symbols_and_roots()[0]
        assert [s["name"] for s in symbols if s["kind"] == SymbolKind.Function] == ["$one"]


@pytest.mark.parametrize("prefix", ["", "(; café ;) "], ids=["ascii", "bmp"])
def test_serena_tools_preserve_source_on_disk(tmp_path: Path, prefix: str) -> None:
    # use actual Serena tools against a disposable project
    body = "(func $add (result i32) i32.const 1)"
    source = f"(module\n  {prefix}{body}\n  (func $caller (result i32) call $add)\n)\n"
    path = tmp_path / "main.wat"
    path.write_text(source, encoding="utf-8")
    original_bytes = path.read_bytes()
    (tmp_path / ".serena").mkdir()
    (tmp_path / ".serena/project.yml").write_text("project_name: wat-tools\nlanguage_servers: [wat]\n", encoding="utf-8")
    config = SerenaConfig(log_level=logging.ERROR).with_headless_mode_overrides()
    agent = SerenaAgent(project=str(tmp_path), serena_config=config)
    try:
        agent.execute_task(lambda: None)
        find = agent.get_tool(FindSymbolTool)
        with find.symbol_dict_grouper.disabled_context():
            found = json.loads(find.apply(name_path_pattern="$add", relative_path="main.wat", include_body=True))
        assert len(found) == 1
        assert found[0]["body"] == body
        agent.get_tool(RenameSymbolTool).apply(name_path="$add", relative_path="main.wat", new_name="$sum")
        assert path.read_bytes() == original_bytes.replace(b"$add", b"$sum")
        with find.symbol_dict_grouper.disabled_context():
            renamed = json.loads(find.apply(name_path_pattern="$sum", relative_path="main.wat", include_body=True))
        assert len(renamed) == 1
        assert renamed[0]["body"] == body.replace("$add", "$sum")
    finally:
        agent.on_shutdown()
