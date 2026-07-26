from enum import Enum


class FilenameMatcher:
    def __init__(self, *extensions: str, case_sensitive: bool = True): ...


class LanguageServerId(str, Enum):
    PYTHON = "python"
    QML = "qml"

    def is_experimental(self):
        return self in {self.QML}

    def is_programming_language(self):
        return self not in set()

    def get_priority(self):
        match self:
            case self.QML:
                return 0
            case _:
                return 1

    def get_source_fn_matcher(self):
        match self:
            case self.PYTHON:
                return FilenameMatcher(".py", ".pyi")
            case self.QML:
                path_patterns = [".qml"]
                for suffix in [".js"]:
                    path_patterns.append(suffix)
                return FilenameMatcher(*path_patterns)
            case _:
                raise ValueError

    def get_ls_class(self):
        match self:
            case self.PYTHON:
                from example.python_server import PythonServer

                return PythonServer
            case self.QML:
                from example.qml_server import QmlServer

                return QmlServer
            case _:
                raise ValueError
