"""The Agno example preserves project selection while providing standalone help."""

import importlib.util
import re
import runpy
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = _REPO_ROOT / "scripts" / "agno_agent.py"


class _AgentCreationObserved(BaseException):
    """Stops execution at agent construction, before any application effects."""


@dataclass
class _AgnoEnvironment:
    provider: ModuleType
    agent_os: Mock
    root: Path


@pytest.fixture
def agno_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> _AgnoEnvironment:
    """Load the real provider with the optional framework replaced at its boundary."""

    class FrameworkObject:
        def __init__(self, *args: object, **kwargs: object) -> None:
            self.functions: dict[str, object] = {}

    external_classes = {
        "agno.agent": "Agent",
        "agno.db.sqlite": "SqliteDb",
        "agno.memory": "MemoryManager",
        "agno.models.base": "Model",
        "agno.tools.function": "Function",
        "agno.tools.toolkit": "Toolkit",
        "agno.models.anthropic.claude": "Claude",
        "agno.models.google.gemini": "Gemini",
        "agno.os": "AgentOS",
    }
    for module_name, class_name in external_classes.items():
        parts = module_name.split(".")
        for length in range(1, len(parts) + 1):
            name = ".".join(parts[:length])
            if name not in sys.modules:
                module = ModuleType(name)
                module.__path__ = []
                monkeypatch.setitem(sys.modules, name, module)
        monkeypatch.setattr(sys.modules[module_name], class_name, FrameworkObject, raising=False)

    agent_os = Mock()
    monkeypatch.setattr(sys.modules["agno.os"], "AgentOS", agent_os)

    provider_path = _REPO_ROOT / "src" / "serena" / "agno.py"
    spec = importlib.util.spec_from_file_location("serena.agno", provider_path)
    assert spec is not None and spec.loader is not None
    provider = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "serena.agno", provider)
    spec.loader.exec_module(provider)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SERENA_HOME", str(tmp_path / "serena-home"))
    monkeypatch.setattr(provider, "REPO_ROOT", str(tmp_path))
    monkeypatch.setattr(provider, "load_dotenv", lambda: False)
    monkeypatch.setattr(provider.SerenaAgentContext, "load", lambda name: object())
    return _AgnoEnvironment(provider=provider, agent_os=agent_os, root=tmp_path)


@pytest.mark.parametrize(
    ("arguments", "project"),
    [
        ([], None),
        (["--project", "project with spaces"], "project with spaces"),
        (["--project-file", "configs/project.yml"], "configs/project.yml"),
        (["--project=relative-project"], "relative-project"),
        (["--project-file=configs/project.yml"], "configs/project.yml"),
    ],
)
def test_project_selection_reaches_agent_construction(
    arguments: list[str], project: str | None, agno_environment: _AgnoEnvironment, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Both project options reach the real provider's normalized selection."""

    def observe_agent(project_path: str | None, **kwargs: object) -> None:
        raise _AgentCreationObserved(project_path)

    monkeypatch.setattr(agno_environment.provider, "SerenaAgent", observe_agent)
    monkeypatch.setattr(sys, "argv", [str(_SCRIPT), *arguments])
    with pytest.raises(_AgentCreationObserved) as observed:
        runpy.run_path(str(_SCRIPT), run_name="__main__")

    expected = str((agno_environment.root / project).resolve()) if project is not None else None
    assert observed.value.args == (expected,)
    agno_environment.agent_os.assert_not_called()


@pytest.fixture
def without_agno(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Make optional framework imports unavailable even if extras are installed."""
    for name in tuple(sys.modules):
        if name == "agno" or name.startswith("agno."):
            monkeypatch.delitem(sys.modules, name)
    monkeypatch.setitem(sys.modules, "agno", None)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SERENA_HOME", str(tmp_path / "serena-home"))


@pytest.mark.parametrize("help_flag", ["-h", "--help"])
def test_help_documents_project_options_without_optional_framework(
    help_flag: str, without_agno: None, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Help describes both supported options without constructing an application."""
    monkeypatch.setattr(sys, "argv", [str(_SCRIPT), help_flag])
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_path(str(_SCRIPT), run_name="__main__")
    assert exit_info.value.code == 0
    output = capsys.readouterr()
    assert re.search(r"--project(?:\s|=)", output.out)
    assert re.search(r"--project-file(?:\s|=)", output.out)
    assert output.err == ""


@pytest.mark.parametrize(
    "arguments",
    [
        ["--project"],
        ["--project-file"],
        ["--project", "one", "--project-file", "two"],
        ["--unknown-option"],
    ],
)
def test_invalid_options_fail_before_application_startup(
    arguments: list[str], without_agno: None, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Invalid, incomplete and conflicting options report command-line errors."""
    monkeypatch.setattr(sys, "argv", [str(_SCRIPT), *arguments])
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_path(str(_SCRIPT), run_name="__main__")
    assert exit_info.value.code == 2
    assert "error:" in capsys.readouterr().err


def test_server_reimport_reuses_agent_with_foreign_arguments(agno_environment: _AgnoEnvironment, monkeypatch: pytest.MonkeyPatch) -> None:
    """The server can reload the exported app without parsing its own argv."""
    application_agent = Mock()
    application_agent.get_exposed_tool_instances.return_value = []
    agent_factory = Mock(return_value=application_agent)
    monkeypatch.setattr(agno_environment.provider, "SerenaAgent", agent_factory)
    monkeypatch.setattr(sys, "argv", [str(_SCRIPT)])
    runpy.run_path(str(_SCRIPT), run_name="__main__")
    (initial_agent,) = agno_environment.agent_os.call_args.kwargs["agents"]
    agno_environment.agent_os.reset_mock()
    monkeypatch.setattr(sys, "argv", ["uvicorn", "agno_agent:app", "--port", "9876"])

    result = runpy.run_path(str(_SCRIPT), run_name="agno_agent")

    assert result["app"] is agno_environment.agent_os.return_value.get_app.return_value
    (reimported_agent,) = agno_environment.agent_os.call_args.kwargs["agents"]
    assert reimported_agent is initial_agent
    agent_factory.assert_called_once()
    agno_environment.agent_os.return_value.serve.assert_not_called()
