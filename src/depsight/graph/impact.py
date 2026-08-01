"""Blast-radius impact analysis via reverse BFS."""

from __future__ import annotations

from dataclasses import dataclass

import networkx as nx


@dataclass
class ImpactResult:
    changed_file: str
    directly_affected: list[str]
    transitively_affected: list[str]
    total_affected: int


def analyze_impact(graph: nx.DiGraph, changed_file: str) -> ImpactResult | None:
    """Compute blast radius: all nodes that depend (transitively) on changed_file."""
    if changed_file not in graph:
        return None

    # Reverse graph: edges point from dependee to dependent
    reverse = graph.reverse()

    # BFS from changed_file in reverse graph
    visited = set()
    queue = [changed_file]
    directly = []
    transitively = []

    while queue:
        node = queue.pop(0)
        if node in visited:
            continue
        visited.add(node)

        if node != changed_file:
            # Check if direct dependency
            if graph.has_edge(node, changed_file):
                directly.append(node)
            else:
                transitively.append(node)

        for succ in reverse.successors(node):
            if succ not in visited:
                queue.append(succ)

    return ImpactResult(
        changed_file=changed_file,
        directly_affected=directly,
        transitively_affected=transitively,
        total_affected=len(directly) + len(transitively),
    )
