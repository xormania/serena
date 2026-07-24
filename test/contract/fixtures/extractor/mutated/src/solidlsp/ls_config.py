# ruff: noqa: F821

from enum import Enum


class LanguageServerId(str, Enum):
    PYTHON = "python"

    def get_source_fn_matcher(self):
        match self:
            case self.PYTHON:
                return build_matcher()  # type: ignore[unresolved-reference]
            case _:
                raise ValueError

    def get_ls_class(self):
        match self:
            case self.PYTHON:
                from example.python_server import PythonServer

                return PythonServer
            case _:
                raise ValueError
