"""DFS-based graph algorithms: cycles, topological sort, articulation points."""

from __future__ import annotations

import networkx as nx


def detect_cycles(graph: nx.DiGraph) -> list[list[str]]:
    """Return all cycles in the graph as lists of node names."""
    try:
        cycles = list(nx.simple_cycles(graph))
        return cycles
    except nx.NetworkXNoCycle:
        return []


def topological_sort(graph: nx.DiGraph) -> list[str] | None:
    """Return topological order if graph is a DAG, else None."""
    try:
        return list(nx.topological_sort(graph))
    except nx.NetworkXUnfeasible:
        return None


def find_articulation_points(graph: nx.DiGraph) -> list[str]:
    """Find articulation points in the underlying undirected graph."""
    undirected = graph.to_undirected()
    return list(nx.articulation_points(undirected))
