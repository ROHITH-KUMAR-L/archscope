"""Python parser using AST."""

from __future__ import annotations

import ast
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Edge:
    source: str
    target: str
    import_type: str
    line: int


def _resolve_import(root_path: Path, source_file: Path, module: str, level: int) -> str | None:
    """Resolve an import to a local file path if possible."""
    if level > 0:
        # Relative import
        base = source_file.parent
        for _ in range(level - 1):
            base = base.parent
        target_path = base / module.replace(".", os.sep)
    else:
        # Absolute import - try to find in project
        target_path = root_path / module.replace(".", os.sep)

    # Check for .py file
    if target_path.with_suffix(".py").exists():
        return str(target_path.with_suffix(".py").relative_to(root_path))
    # Check for package (directory with __init__.py)
    if (target_path / "__init__.py").exists():
        return str(target_path.relative_to(root_path))
    return None


_EXCLUDED_DIRS = {
    ".venv", "venv", "__pycache__", ".git", "node_modules",
    "build", "dist", ".eggs", ".pytest_cache", ".ruff_cache",
    ".idea", ".vscode", ".tox", ".mypy_cache", ".cache",
}


def _is_excluded(path: Path, root: Path) -> bool:
    for parent in path.parents:
        if parent == root:
            break
        if parent.name in _EXCLUDED_DIRS:
            return True
    return False


def parse_python_project(root: str | Path) -> list[Edge]:
    edges: list[Edge] = []
    root_path = Path(root)

    py_files = [f for f in root_path.rglob("*.py") if not _is_excluded(f, root_path)]
    module_to_file = {}
    for py_file in py_files:
        rel = py_file.relative_to(root_path)
        # Map module name to file (without .py)
        module_name = str(rel.with_suffix("")).replace(os.sep, ".")
        module_to_file[module_name] = str(rel)
        # Also map parent packages
        parts = module_name.split(".")
        for i in range(1, len(parts) + 1):
            pkg = ".".join(parts[:i])
            if pkg not in module_to_file:
                module_to_file[pkg] = str(rel).replace(str(rel.name), "").rstrip(os.sep)

    for py_file in py_files:
        try:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError, PermissionError, OSError):
            continue

        rel_path = str(py_file.relative_to(root_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    target = _resolve_import(root_path, py_file, alias.name, 0)
                    if target is None:
                        target = alias.name
                    edges.append(Edge(
                        source=rel_path,
                        target=target,
                        import_type="import",
                        line=node.lineno,
                    ))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                level = node.level
                for alias in node.names:
                    if level > 0 or module:
                        target = _resolve_import(root_path, py_file, module, level)
                        if target is None:
                            target = f"{module}.{alias.name}" if module else alias.name
                        else:
                            # For from X import Y, we want X resolved
                            pass
                    else:
                        target = alias.name
                    edges.append(Edge(
                        source=rel_path,
                        target=target,
                        import_type="from_import",
                        line=node.lineno,
                    ))

    return edges
