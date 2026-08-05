"""C++ parser (regex-based fallback)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Edge:
    source: str
    target: str
    import_type: str
    line: int


_INCLUDE_RE = re.compile(
    r"""^\s*#\s*include\s+[<"]([^>"]+)[>"]""",
    re.MULTILINE,
)


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


def parse_cpp_project(root: str | Path) -> list[Edge]:
    edges: list[Edge] = []
    root_path = Path(root)

    for cpp_file in root_path.rglob("*.[ch]*"):
        if _is_excluded(cpp_file, root_path):
            continue
        try:
            content = cpp_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError, OSError):
            continue

        rel_path = str(cpp_file.relative_to(root_path))

        for match in _INCLUDE_RE.finditer(content):
            line_no = content[:match.start()].count("\n") + 1
            edges.append(Edge(
                source=rel_path,
                target=match.group(1),
                import_type="include",
                line=line_no,
            ))

    return edges
