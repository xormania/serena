import inspect
import re
from pathlib import Path

from serena.config.client_setup import ClientSetupHandlerGrok

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _extract_section(markdown: str, heading: str) -> str:
    """Extract the content under a top-level ## heading (simple and sufficient for our docs)."""
    pattern = rf"\n## {re.escape(heading)}\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, markdown, re.DOTALL)
    return match.group(1) if match else ""


def test_grok_docs_and_changelog_are_consistent():
    clients_doc = (PROJECT_ROOT / "docs/02-usage/030_clients.md").read_text()
    config_doc = (PROJECT_ROOT / "docs/02-usage/050_configuration.md").read_text()
    changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text()
    handler_source = inspect.getsource(ClientSetupHandlerGrok.apply)

    assert "\n## Grok\n" in clients_doc
    grok_section = _extract_section(clients_doc, "Grok")

    assert "030_clients.html#grok" in handler_source
    assert "serena setup grok" in grok_section
    assert "serena-hooks remind --client=grok" in grok_section
    assert "serena-hooks cleanup --client=grok" in grok_section

    assert re.search(r"`grok`", config_doc)

    changelog_lower = changelog.lower()
    assert "`grok`" in changelog_lower
    assert "serena setup grok" in changelog_lower
    assert "serena-hooks --client=grok" in changelog_lower
