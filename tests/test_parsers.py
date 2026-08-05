"""Tests for dependency parsers."""

from pathlib import Path

from archsight.parsers.cpp_parser import parse_cpp_project
from archsight.parsers.js_parser import parse_js_project
from archsight.parsers.python_parser import parse_python_project


class TestPythonParser:
    def test_parse_python_complex(self, python_complex_dir: Path) -> None:
        edges = parse_python_project(python_complex_dir)
        assert len(edges) > 0
        sources = {e.source for e in edges}
        assert "main.py" in sources

    def test_parse_python_complex_cyclic(self, python_complex_cyclic_dir: Path) -> None:
        edges = parse_python_project(python_complex_cyclic_dir)
        assert len(edges) == 2
        targets = {e.target for e in edges}
        assert "a" in targets or "a.py" in targets
        assert "b" in targets or "b.py" in targets

    def test_parse_empty_project(self, tmp_path: Path) -> None:
        edges = parse_python_project(tmp_path)
        assert edges == []

    def test_parse_python_syntax_error(self, tmp_path: Path) -> None:
        (tmp_path / "bad.py").write_text("def unclosed(", encoding="utf-8")
        edges = parse_python_project(tmp_path)
        assert edges == []


class TestJSParser:
    def test_parse_js_complex(self, js_complex_dir: Path) -> None:
        edges = parse_js_project(js_complex_dir)
        assert len(edges) > 0
        sources = {e.source for e in edges}
        assert "main.js" in sources

    def test_parse_js_complex_cyclic(self, js_complex_cyclic_dir: Path) -> None:
        edges = parse_js_project(js_complex_cyclic_dir)
        assert len(edges) == 2

    def test_parse_empty_project(self, tmp_path: Path) -> None:
        edges = parse_js_project(tmp_path)
        assert edges == []


class TestCppParser:
    def test_parse_cpp_complex(self, cpp_complex_dir: Path) -> None:
        edges = parse_cpp_project(cpp_complex_dir)
        assert len(edges) > 0
        sources = {e.source for e in edges}
        assert "main.cpp" in sources

    def test_parse_cpp_complex_cyclic(self, cpp_complex_cyclic_dir: Path) -> None:
        edges = parse_cpp_project(cpp_complex_cyclic_dir)
        assert len(edges) == 2

    def test_parse_empty_project(self, tmp_path: Path) -> None:
        edges = parse_cpp_project(tmp_path)
        assert edges == []
