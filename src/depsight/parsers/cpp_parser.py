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


def parse_cpp_project(root: str | Path) -> list[Edge]:
    edges: list[Edge] = []
    root_path = Path(root)

    for cpp_file in root_path.rglob("*.[ch]*"):
        try:
            content = cpp_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
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
