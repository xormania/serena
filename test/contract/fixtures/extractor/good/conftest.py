from solidlsp.ls_config import LanguageServerId

_LANGUAGE_REPO_ALIASES = {
    LanguageServerId.PYTHON_TY: LanguageServerId.PYTHON,
    LanguageServerId.PYTHON_TY: LanguageServerId.PYTHON,
}
_LANGUAGE_PYTEST_MARKERS = {LanguageServerId.PYTHON_TY: ["python"]}
_LANGUAGE_SERVER_BACKENDS = [LanguageServerId.PYTHON, LanguageServerId.PYTHON_TY]
_VERIFIED_IMPLEMENTATION_LANGUAGES = {LanguageServerId.PYTHON}
