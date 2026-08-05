"""Dependency graph builder."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import networkx as nx


@dataclass
class Edge:
    source: str
    target: str
    import_type: str
    line: int


class DependencyGraph:
    def __init__(self) -> None:
        self.nx_graph = nx.DiGraph()

    @classmethod
    def build_from_edges(cls, edges: Iterable[Edge]) -> DependencyGraph:
        graph = cls()
        for edge in edges:
            graph.nx_graph.add_edge(
                edge.source,
                edge.target,
                import_type=edge.import_type,
                line=edge.line,
            )
        return graph

    @classmethod
    def build_from_files(cls, parse_results: dict[str, list[Edge]]) -> DependencyGraph:
        graph = cls()
        for _language, edges in parse_results.items():
            for edge in edges:
                graph.nx_graph.add_edge(
                    edge.source,
                    edge.target,
                    import_type=edge.import_type,
                    line=edge.line,
                )
        return graph

    def nodes(self) -> list[str]:
        return list(self.nx_graph.nodes())

    def edges(self) -> list[tuple[str, str]]:
        return list(self.nx_graph.edges())

    def predecessors(self, node: str) -> list[str]:
        return list(self.nx_graph.predecessors(node))

    def successors(self, node: str) -> list[str]:
        return list(self.nx_graph.successors(node))
