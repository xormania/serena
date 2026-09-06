"""The news builder deploys only when explicitly given ``--deploy``."""

import json
import os
import runpy
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import pytest

_SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "build_news_json.py"


@dataclass
class _NewsEnvironment:
    news_dir: Path
    execute_command: Mock


@pytest.fixture
def news_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> _NewsEnvironment:
    """Provide disposable news files and capture external deployment requests."""
    # prepare existing output and an input whose build would change it
    news_dir = tmp_path / "news"
    news_dir.mkdir()
    (news_dir / "20260906.html").write_text("  <p>New release</p>\n", encoding="utf-8")
    (news_dir / "news.json").write_text('{"existing": "unchanged"}', encoding="utf-8")

    # redirect the script's configuration and command boundary to the fixture
    class NewsPaths:
        def __init__(self) -> None:
            self.news_dir = str(news_dir)

    config_module = ModuleType("serena.config.serena_config")
    monkeypatch.setattr(config_module, "SerenaPaths", NewsPaths, raising=False)
    monkeypatch.setitem(sys.modules, "serena.config.serena_config", config_module)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HADES_USER", "test-publisher")
    execute_command = Mock(return_value=0)
    monkeypatch.setattr(os, "system", execute_command)
    return _NewsEnvironment(news_dir=news_dir, execute_command=execute_command)


@pytest.mark.parametrize("argument", ["--d", "--de", "--dep", "--depl", "--deplo"])
def test_abbreviated_deploy_is_rejected_before_building(
    argument: str,
    news_environment: _NewsEnvironment,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Abbreviations report an error without replacing news or requesting deployment."""
    monkeypatch.setattr(sys, "argv", [str(_SCRIPT), argument])
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_path(str(_SCRIPT), run_name="__main__")

    assert exit_info.value.code == 2
    assert argument in capsys.readouterr().err
    assert json.loads((news_environment.news_dir / "news.json").read_text(encoding="utf-8")) == {"existing": "unchanged"}
    news_environment.execute_command.assert_not_called()


@pytest.mark.parametrize("deploy", [False, True], ids=["build-only", "exact-deploy"])
def test_build_requires_exact_deploy_flag_to_publish(
    deploy: bool, news_environment: _NewsEnvironment, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Normal builds produce JSON, and only the exact flag additionally requests SCP."""
    arguments = ["--deploy"] if deploy else []
    monkeypatch.setattr(sys, "argv", [str(_SCRIPT), *arguments])
    runpy.run_path(str(_SCRIPT), run_name="__main__")

    assert json.loads((news_environment.news_dir / "news.json").read_text(encoding="utf-8")) == {"20260906": "<p>New release</p>"}
    if deploy:
        news_environment.execute_command.assert_called_once_with(
            "scp news/news.json test-publisher@hades:/var/www/html/oraios-software/serena_news.json"
        )
    else:
        news_environment.execute_command.assert_not_called()
