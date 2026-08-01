"""Parser orchestration and language dispatch."""

from archscope.parsers.cpp_parser import parse_cpp_project
from archscope.parsers.js_parser import parse_js_project
from archscope.parsers.python_parser import parse_python_project

__all__ = [
    "parse_python_project",
    "parse_js_project",
    "parse_cpp_project",
]
