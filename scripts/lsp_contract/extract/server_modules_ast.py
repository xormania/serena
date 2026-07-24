"""AST extraction of language-server provisioning facts.\n\nThe repository source remains authoritative; extraction supplies agreement checks and never a competing editable truth.\n"""

import ast
import json
from pathlib import Path
from typing import cast

from scripts.lsp_contract.diagnostics import ExtractionError

_FIELD_NAMES = {
    "platform_id": "platformId",
    "archive_type": "archiveType",
    "binary_name": "binaryName",
    "package_name": "packageName",
    "package_version": "packageVersion",
    "allowed_hosts": "allowedHosts",
}


def _call_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def _literal(node: ast.AST, constants: dict[str, object]) -> tuple[object, bool]:
    if isinstance(node, ast.Constant):
        return node.value, False
    if isinstance(node, ast.Name):
        if node.id in constants:
            return constants[node.id], False
        return node.id, True
    if isinstance(node, ast.Attribute):
        return _call_name(node), False
    if isinstance(node, ast.List | ast.Tuple | ast.Set):
        values: list[object] = []
        opaque = False
        for element in node.elts:
            value, element_opaque = _literal(element, constants)
            values.append(value)
            opaque = opaque or element_opaque
        return values, opaque
    if isinstance(node, ast.Dict):
        result: dict[str, object] = {}
        opaque = False
        for key_node, value_node in zip(node.keys, node.values, strict=True):
            if key_node is None:
                opaque = True
                continue
            key, key_opaque = _literal(key_node, constants)
            value, value_opaque = _literal(value_node, constants)
            result[str(key)] = value
            opaque = opaque or key_opaque or value_opaque
        return result, opaque
    try:
        return ast.unparse(node), True
    except Exception:
        return node.__class__.__name__, True


def _module_constants(tree: ast.Module) -> dict[str, object]:
    constants: dict[str, object] = {}
    for statement in tree.body:
        name: str | None = None
        value_node: ast.AST | None = None
        if isinstance(statement, ast.Assign) and len(statement.targets) == 1 and isinstance(statement.targets[0], ast.Name):
            name = statement.targets[0].id
            value_node = statement.value
        elif isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
            name = statement.target.id
            value_node = statement.value
        if name is None or value_node is None:
            continue
        value, opaque = _literal(value_node, constants)
        if not opaque:
            constants[name] = value
    return constants


def _runtime_dependency(node: ast.Call, constants: dict[str, object]) -> dict[str, object]:
    entry: dict[str, object] = {}
    opaque = bool(node.args)
    for keyword in node.keywords:
        if keyword.arg is None:
            opaque = True
            continue
        value, value_opaque = _literal(keyword.value, constants)
        entry[_FIELD_NAMES.get(keyword.arg, keyword.arg)] = value
        opaque = opaque or value_opaque
    entry["opaque"] = opaque
    return entry


def _uvx_pin(node: ast.Call, constants: dict[str, object]) -> dict[str, object]:
    values: dict[str, object] = {}
    opaque = bool(node.args)
    for keyword in node.keywords:
        if keyword.arg is None:
            opaque = True
            continue
        value, value_opaque = _literal(keyword.value, constants)
        values[keyword.arg] = value
        opaque = opaque or value_opaque
    package = values.get("package_name", values.get("package", ""))
    version = values.get("package_version", values.get("default_version", ""))
    result: dict[str, object] = {"package": str(package), "version": str(version)}
    if opaque:
        result["opaque"] = True
    return result


def _deduplicate(values: list[object]) -> list[object]:
    seen: set[str] = set()
    result: list[object] = []
    for value in values:
        key = json.dumps(value, sort_keys=True)
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result


def extract_server_modules(root: Path) -> dict[str, object]:
    """Extract dependency, pin, command, and executable-probe facts."""
    modules: dict[str, object] = {}
    for path in sorted(root.rglob("*.py")):
        if path.name == "__init__.py":
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as error:
            raise ExtractionError(path, error.lineno or 1, error.msg) from error

        constants = _module_constants(tree)
        runtime_dependencies: list[object] = []
        uvx_pins: list[object] = []
        cargo_commands: list[object] = []
        path_probes: list[object] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call_name = _call_name(node.func)
                if call_name.endswith("RuntimeDependency"):
                    runtime_dependencies.append(_runtime_dependency(node, constants))
                elif call_name.endswith("LanguageServerDependencyProviderUvx"):
                    uvx_pins.append(_uvx_pin(node, constants))
                elif call_name.endswith(".which") and node.args:
                    value, opaque = _literal(node.args[0], constants)
                    if isinstance(value, str) and not opaque:
                        path_probes.append(value)
            elif isinstance(node, ast.List | ast.Tuple):
                value, opaque = _literal(node, constants)
                if not opaque and isinstance(value, list) and len(value) >= 2 and value[0] == "cargo" and value[1] == "install":
                    cargo_commands.append(value)

        relative = path.relative_to(root).with_suffix("")
        module_name = ".".join(relative.parts)
        modules[module_name] = {
            "runtimeDeps": _deduplicate(runtime_dependencies),
            "uvxPins": _deduplicate(uvx_pins),
            "cargoCommands": _deduplicate(cargo_commands),
            "pathProbes": sorted(set(str(value) for value in path_probes)),
            "pins": {name: value for name, value in sorted(constants.items()) if "VERSION" in name or name.endswith("_SHA256")},
        }

    for json_path in sorted(root.rglob("runtime_dependencies.json")):
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ExtractionError(json_path, error.lineno, error.msg) from error
        module_name = ".".join(json_path.parent.relative_to(root).parts) or json_path.parent.name
        record = modules.setdefault(
            module_name,
            {"runtimeDeps": [], "uvxPins": [], "cargoCommands": [], "pathProbes": [], "pins": {}},
        )
        if not isinstance(record, dict):
            raise ExtractionError(json_path, 1, "module extraction record must be a mapping")
        cast(dict[str, object], record)["runtimeDependencyJson"] = payload

    return dict(sorted(modules.items()))
