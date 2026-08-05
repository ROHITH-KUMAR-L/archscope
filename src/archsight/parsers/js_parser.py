"""JavaScript/TypeScript parser (regex-based fallback)."""

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


_IMPORT_RE = re.compile(
    r"""^\s*(?:import\s+(?:[\w*\s{},]+\s+from\s+)?|export\s+(?:[\w*\s{},]+\s+from\s+)?)(['"])([^'"]+)\1""",
    re.MULTILINE,
)
_REQUIRE_RE = re.compile(
    r"""require\(['"]([^'"]+)['"]\)""",
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


def parse_js_project(root: str | Path) -> list[Edge]:
    edges: list[Edge] = []
    root_path = Path(root)

    for js_file in root_path.rglob("*.[jt]s*"):
        if _is_excluded(js_file, root_path):
            continue
        try:
            content = js_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError, OSError):
            continue

        rel_path = str(js_file.relative_to(root_path))

        for match in _IMPORT_RE.finditer(content):
            line_no = content[:match.start()].count("\n") + 1
            edges.append(Edge(
                source=rel_path,
                target=match.group(2),
                import_type="import",
                line=line_no,
            ))

        for match in _REQUIRE_RE.finditer(content):
            line_no = content[:match.start()].count("\n") + 1
            edges.append(Edge(
                source=rel_path,
                target=match.group(1),
                import_type="require",
                line=line_no,
            ))

    return edges
