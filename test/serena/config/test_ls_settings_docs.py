"""
Guards the language-server settings documentation against drift.

Every pinned dependency version that a user can override through ``ls_specific_settings`` must be
documented in the configuration guide, in its own backend's section, together with the default the
code actually uses.

The manifest below is deliberately explicit rather than derived by scanning source. Backends reach
their overridable versions through at least four different shapes -- ``self._custom_settings.get``,
a locally bound ``CustomLSSettings``, a chained ``get_ls_specific_settings(...).get(...)``, and
declarative ``version_setting_key=`` registration on a shared dependency provider -- so any pattern
match silently under-reports, and an under-reporting scan produces a test that is green because it
looked at half the codebase. The manifest is instead pinned to source by
:func:`test_manifest_entries_exist_in_source` and protected against omissions by
:func:`test_every_pinned_version_constant_is_classified`.

Scope: the contract covers overridable pins expressed as *named version constants* anywhere under
``language_servers/`` (subpackages included). Backends whose default is an inline literal inside a
``.get(...)`` call -- currently ``clangd_version``, ``verible_version`` and the Svelte/Vue
TypeScript pins -- are documented in the configuration guide but sit outside this guard, because a
literal carries no name for the classification sweep to hold on to.
"""

import re
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIGURATION_DOC = PROJECT_ROOT / "docs/02-usage/050_configuration.md"
LANGUAGE_SERVERS_DIR = PROJECT_ROOT / "src/solidlsp/language_servers"

#: matches a pinned version, e.g. ``DEFAULT_TAPLO_VERSION = "0.10.0"``. Leading indentation is
#: permitted because some backends declare their pins inside a class rather than at module level
#: (``eclipse_jdtls`` does); anchoring at column 0 hid those from this guard entirely.
VERSION_CONSTANT_PATTERN = re.compile(r'^[ \t]*(_?[A-Z][A-Z0-9_]*VERSION[A-Z0-9_]*)\s*=\s*"([^"]+)"', re.MULTILINE)


@dataclass(frozen=True)
class _Setting:
    """A user-overridable pinned dependency version and where it must be documented."""

    module: str
    """the module under src/solidlsp/language_servers that owns the pin"""
    doc_section: str
    """the exact '#### <heading>' under which it must be documented"""
    key: str
    """the ls_specific_settings key that overrides it"""
    constant: str
    """the module-level constant holding the default"""


#: the reviewed contract; extend it whenever a backend gains an overridable pinned version
OVERRIDABLE_VERSIONS: list[_Setting] = [
    _Setting("ada_language_server", "Ada", "als_version", "DEFAULT_ALS_VERSION"),
    _Setting("al_language_server", "AL", "al_extension_version", "DEFAULT_AL_EXTENSION_VERSION"),
    _Setting("angular_language_server", "Angular", "angular_language_server_version", "DEFAULT_ANGULAR_LANGUAGE_SERVER_VERSION"),
    _Setting("angular_language_server", "Angular", "angular_language_service_version", "DEFAULT_ANGULAR_LANGUAGE_SERVICE_VERSION"),
    _Setting("angular_language_server", "Angular", "typescript_language_server_version", "DEFAULT_TYPESCRIPT_LANGUAGE_SERVER_VERSION"),
    _Setting("angular_language_server", "Angular", "typescript_version", "DEFAULT_TYPESCRIPT_VERSION"),
    _Setting("ansible_language_server", "Ansible", "ansible_language_server_version", "DEFAULT_ANSIBLE_LANGUAGE_SERVER_VERSION"),
    _Setting("basedpyright_server", "Python", "basedpyright_version", "BASEDPYRIGHT_VERSION"),
    _Setting("bash_language_server", "Bash", "bash_language_server_version", "DEFAULT_BASH_LANGUAGE_SERVER_VERSION"),
    _Setting("bsl_language_server", "BSL (1C:Enterprise / OneScript)", "bsl_ls_version", "DEFAULT_BSL_LS_VERSION"),
    _Setting("clojure_lsp", "Clojure", "clojure_lsp_version", "DEFAULT_CLOJURE_LSP_VERSION"),
    _Setting(
        "csharp_language_server", "C# (Roslyn Language Server)", "csharp_language_server_version", "DEFAULT_CSHARP_LANGUAGE_SERVER_VERSION"
    ),
    _Setting("cue_language_server", "CUE", "cue_version", "DEFAULT_CUE_VERSION"),
    _Setting("dart_language_server", "Dart", "dart_sdk_version", "DEFAULT_DART_SDK_VERSION"),
    _Setting("eclipse_jdtls", "Java (`eclipse.jdt.ls`)", "gradle_version", "DEFAULT_GRADLE_VERSION"),
    _Setting("eclipse_jdtls", "Java (`eclipse.jdt.ls`)", "vscode_java_version", "DEFAULT_VSCODE_JAVA_VERSION"),
    _Setting("elixir_tools/elixir_tools", "Elixir", "expert_version", "EXPERT_VERSION"),
    _Setting("elm_language_server", "Elm", "elm_compiler_version", "DEFAULT_ELM_COMPILER_VERSION"),
    _Setting("elm_language_server", "Elm", "elm_language_server_version", "DEFAULT_ELM_LANGUAGE_SERVER_VERSION"),
    _Setting("fortran_language_server", "Fortran", "fortls_version", "FORTLS_VERSION"),
    _Setting("fsharp_language_server", "F#", "fsautocomplete_version", "DEFAULT_FSAUTOCOMPLETE_VERSION"),
    _Setting("groovy_language_server", "Groovy", "vscode_java_version", "DEFAULT_VSCODE_JAVA_VERSION"),
    _Setting("haxe_language_server", "Haxe", "version", "DEFAULT_VSHAXE_VERSION"),
    _Setting("hlsl_language_server", "HLSL", "version", "_DEFAULT_VERSION"),
    _Setting("intelephense", "PHP (`Intelephense`)", "intelephense_version", "DEFAULT_INTELEPHENSE_VERSION"),
    _Setting("json_language_server", "JSON", "json_language_server_version", "DEFAULT_JSON_LANGUAGE_SERVER_VERSION"),
    _Setting("kotlin_language_server", "Kotlin", "kotlin_lsp_version", "DEFAULT_KOTLIN_LSP_VERSION"),
    _Setting("lua_ls", "Lua", "lua_language_server_version", "DEFAULT_LUA_LS_VERSION"),
    _Setting("luau_lsp", "Luau", "luau_lsp_version", "DEFAULT_LUAU_LSP_VERSION"),
    _Setting("marksman", "Markdown", "marksman_version", "DEFAULT_MARKSMAN_VERSION"),
    _Setting("matlab_language_server", "MATLAB", "matlab_extension_version", "DEFAULT_MATLAB_EXTENSION_VERSION"),
    _Setting("nextflow_language_server", "Nextflow", "nextflow_ls_version", "DEFAULT_NEXTFLOW_LS_VERSION"),
    _Setting("omnisharp", "C# (`OmniSharp`)", "omnisharp_version", "DEFAULT_OMNISHARP_VERSION"),
    _Setting("omnisharp", "C# (`OmniSharp`)", "razor_omnisharp_version", "DEFAULT_RAZOR_OMNISHARP_VERSION"),
    _Setting("pascal_server", "Pascal (`pasls`)", "pasls_version", "PASLS_VERSION"),
    _Setting("phpactor", "PHP (`Phpactor`)", "phpactor_version", "DEFAULT_PHPACTOR_VERSION"),
    _Setting("phpantom", "PHP (`PHPantom`)", "phpantom_version", "DEFAULT_PHPANTOM_VERSION"),
    _Setting("powershell_language_server", "PowerShell", "pses_version", "DEFAULT_PSES_VERSION"),
    _Setting("powershell_language_server", "PowerShell", "psscriptanalyzer_version", "PSSCRIPTANALYZER_VERSION"),
    _Setting("pyrefly_server", "Python", "pyrefly_version", "PYREFLY_VERSION"),
    _Setting("pyright_server", "Python", "pyright_version", "PYRIGHT_VERSION"),
    _Setting("ruby_lsp", "Ruby", "ruby_lsp_version", "RUBY_LSP_VERSION"),
    _Setting("scala_language_server", "Scala", "metals_version", "DEFAULT_METALS_VERSION"),
    _Setting("solidity_language_server", "Solidity", "forge_version", "DEFAULT_FORGE_VERSION"),
    _Setting("solidity_language_server", "Solidity", "solidity_language_server_version", "DEFAULT_SOLIDITY_LANGUAGE_SERVER_VERSION"),
    _Setting("some_sass_language_server", "SCSS / Sass / CSS", "some_sass_version", "DEFAULT_PACKAGE_VERSION"),
    _Setting("taplo_server", "TOML", "taplo_version", "DEFAULT_TAPLO_VERSION"),
    _Setting("terraform_ls", "Terraform", "terraform_ls_version", "DEFAULT_TERRAFORM_LS_VERSION"),
    _Setting("ty_server", "Python", "ty_version", "TY_VERSION"),
    _Setting(
        "typescript_language_server", "TypeScript", "typescript_language_server_version", "DEFAULT_TYPESCRIPT_LANGUAGE_SERVER_VERSION"
    ),
    _Setting("typescript_language_server", "TypeScript", "typescript_version", "DEFAULT_TYPESCRIPT_VERSION"),
    _Setting("vscode_html_language_server", "HTML", "vscode_langservers_version", "DEFAULT_PACKAGE_VERSION"),
    _Setting("vts_language_server", "TypeScript via `vtsls`", "vtsls_version", "DEFAULT_VTSLS_VERSION"),
    _Setting("yaml_language_server", "YAML", "yaml_language_server_version", "DEFAULT_YAML_LANGUAGE_SERVER_VERSION"),
]

#: pinned versions that are deliberately NOT user-overridable, with the reason they are excluded
NON_OVERRIDABLE_REASONS: dict[str, str] = {
    "_INITIAL_VERSION": "frozen first-install pin for HLSL",
    "INITIAL_": "frozen first-install pin; by convention never bumped (see eclipse_jdtls for the spec)",
    "_SHELLCHECK_VERSION": "transitive tool of bash-language-server; not exposed as a setting",
    "TEXLAB_VERSION": "no override is wired up for texlab",
}


def _module_source(module: str) -> str:
    return (LANGUAGE_SERVERS_DIR / f"{module}.py").read_text(encoding="utf-8")


def _default_of(setting: _Setting) -> str:
    """
    Resolves a manifest entry's default from source, following one level of aliasing.

    :param setting: the manifest entry
    :return: the pinned default value
    """
    source = _module_source(setting.module)
    constants = dict(VERSION_CONSTANT_PATTERN.findall(source))
    if setting.constant in constants:
        return constants[setting.constant]
    alias = re.search(rf"^{re.escape(setting.constant)}\s*=\s*(\w+)\s*$", source, re.MULTILINE)
    assert alias and alias.group(1) in constants, f"{setting.constant} not resolvable in {setting.module}"
    return constants[alias.group(1)]


def _section_body(documentation: str, heading: str) -> str:
    """
    Extracts the text under one '#### <heading>' up to the next heading of any level.

    :param documentation: the full configuration page
    :param heading: the exact heading text
    :return: the section body, or the empty string if the section does not exist (the caller then
        reports every setting expected there as undocumented, naming the missing section)
    """
    match = re.search(rf"^#### {re.escape(heading)}\s*$(.*?)(?=^#{{1,4}} )", documentation, re.MULTILINE | re.DOTALL)
    return match.group(1) if match is not None else ""


def _documented_default(section: str, key: str) -> str | None:
    """
    Finds the default documented for a key within one section, as a markdown table row or a YAML line.

    :param section: the section body
    :param key: the setting key
    :return: the documented default, or None if the key is not documented there
    """
    row = re.search(rf"^\|\s*`{re.escape(key)}`\s*\|\s*`?([^`|]+?)`?\s*\|", section, re.MULTILINE)
    if row is not None:
        return row.group(1).strip()
    yaml_line = re.search(rf'^\s*{re.escape(key)}:\s*"?([^"\s#]+)"?', section, re.MULTILINE)
    return yaml_line.group(1).strip() if yaml_line is not None else None


def test_manifest_entries_exist_in_source():
    """The manifest may not drift from the code it claims to describe."""
    problems = []
    for setting in OVERRIDABLE_VERSIONS:
        source = _module_source(setting.module)
        if f'"{setting.key}"' not in source:
            problems.append(f"{setting.module}: key '{setting.key}' no longer appears in source")
        elif setting.constant not in source:
            problems.append(f"{setting.module}: constant {setting.constant} no longer appears in source")
    assert not problems, "manifest is stale:\n" + "\n".join(problems)


def test_every_pinned_version_constant_is_classified():
    """
    No pinned version may be silently absent from the contract.

    A new pin must be added to the manifest or given an exclusion reason; otherwise this fails, which
    is what stops the contract from quietly shrinking as backends are added or refactored.
    """
    claimed = {(s.module, s.constant) for s in OVERRIDABLE_VERSIONS}
    aliased = set()
    for setting in OVERRIDABLE_VERSIONS:
        alias = re.search(rf"^{re.escape(setting.constant)}\s*=\s*(\w+)\s*$", _module_source(setting.module), re.MULTILINE)
        if alias:
            aliased.add((setting.module, alias.group(1)))

    unclassified = []
    for path in sorted(LANGUAGE_SERVERS_DIR.rglob("*.py")):
        module = path.relative_to(LANGUAGE_SERVERS_DIR).with_suffix("").as_posix()
        for name, _ in VERSION_CONSTANT_PATTERN.findall(path.read_text(encoding="utf-8")):
            if (module, name) in claimed or (module, name) in aliased:
                continue
            if any(name.startswith(p) or name == p for p in NON_OVERRIDABLE_REASONS):
                continue
            unclassified.append(f"{module}.{name}")
    assert not unclassified, "pinned versions are neither in OVERRIDABLE_VERSIONS nor in NON_OVERRIDABLE_REASONS:\n  " + "\n  ".join(
        unclassified
    )


def test_overridable_versions_are_documented_with_their_default():
    """Each setting must be documented in its own backend's section, with the default the code uses."""
    documentation = CONFIGURATION_DOC.read_text(encoding="utf-8")
    problems = []
    for setting in OVERRIDABLE_VERSIONS:
        expected = _default_of(setting)
        documented = _documented_default(_section_body(documentation, setting.doc_section), setting.key)
        if documented is None:
            problems.append(f"{setting.doc_section}: '{setting.key}' is not documented (default {expected})")
        elif documented != expected:
            problems.append(f"{setting.doc_section}: '{setting.key}' documents '{documented}', source says '{expected}'")
    assert not problems, "configuration docs are out of sync with the pinned defaults:\n  " + "\n  ".join(problems)
