"""Test-only retirement enforcement for the disposable synthetic thesis."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

from .harness import ValidationError


_EXCLUDED_TOP_LEVEL = frozenset({"about", "docs", "openspec", "tests", "thesis"})
_PACKAGE_FILENAMES = frozenset(
    {
        "Dockerfile",
        "Pipfile",
        "package.json",
        "pyproject.toml",
        "requirements.txt",
        "setup.cfg",
        "setup.py",
    }
)
_THESIS_PACKAGE_TOKEN = re.compile(
    r"(?<![A-Za-z0-9_])thesis(?:[._-][A-Za-z0-9_]+)?(?![A-Za-z0-9_])"
)


@dataclass(frozen=True)
class ProductionSurfaceReport:
    production_sources: tuple[str, ...]
    production_package_files: tuple[str, ...]


def scan_production_surfaces(project_root: Path) -> ProductionSurfaceReport:
    """List non-thesis source and packaging inputs subject to retirement checks."""
    source_paths: list[str] = []
    package_paths: list[str] = []
    for path in sorted(project_root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(project_root)
        if not relative.parts or relative.parts[0] in _EXCLUDED_TOP_LEVEL:
            continue
        if any(part in {".git", "__pycache__"} for part in relative.parts):
            continue
        if path.suffix == ".py":
            source_paths.append(relative.as_posix())
        if path.name in _PACKAGE_FILENAMES:
            package_paths.append(relative.as_posix())
    return ProductionSurfaceReport(tuple(source_paths), tuple(package_paths))


def assert_import_negative(project_root: Path) -> ProductionSurfaceReport:
    """Fail if a production source or package can depend on ``thesis``."""
    report = scan_production_surfaces(project_root)
    for relative in report.production_sources:
        try:
            tree = ast.parse((project_root / relative).read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            raise ValidationError("production_source_unreadable") from None
        for node in ast.walk(tree):
            if _imports_thesis(node):
                raise ValidationError("production_thesis_import")
    for relative in report.production_package_files:
        try:
            package_text = (project_root / relative).read_text(encoding="utf-8")
        except OSError:
            raise ValidationError("production_package_unreadable") from None
        if _THESIS_PACKAGE_TOKEN.search(package_text):
            raise ValidationError("production_thesis_package")
    return report


def _imports_thesis(node: ast.AST) -> bool:
    if isinstance(node, ast.Import):
        return any(_is_thesis_module(alias.name) for alias in node.names)
    if isinstance(node, ast.ImportFrom):
        return _is_thesis_module(node.module)
    if (
        isinstance(node, ast.Call)
        and node.args
        and isinstance(node.args[0], ast.Constant)
    ):
        imported = node.args[0].value
        if isinstance(imported, str) and _is_import_module_call(node.func):
            return _is_thesis_module(imported)
    return False


def _is_import_module_call(function: ast.expr) -> bool:
    return (
        isinstance(function, ast.Name)
        and function.id == "import_module"
        or (isinstance(function, ast.Attribute) and function.attr == "import_module")
    )


def _is_thesis_module(module: str | None) -> bool:
    return module == "thesis" or bool(module and module.startswith("thesis."))
