"""MFAS (Minimum Feedback Arc Set) approximation for refactor priority."""

from __future__ import annotations

import networkx as nx


def run_mfas(graph: nx.DiGraph) -> list[tuple[str, str]]:
    """Return approximate feedback arc set as list of edges to remove."""
    # Greedy approximation: repeatedly remove edge from node with highest (out - in) degree
    g = graph.copy()
    removed: list[tuple[str, str]] = []

    while not nx.is_directed_acyclic_graph(g):
        # Find node with max (out_degree - in_degree)
        scores = {n: g.out_degree(n) - g.in_degree(n) for n in g.nodes()}
        if not scores:
            break
        worst = max(scores, key=scores.get)
        # Remove an outgoing edge from worst
        out_edges = list(g.out_edges(worst))
        if not out_edges:
            g.remove_node(worst)
            continue
        edge = out_edges[0]
        g.remove_edge(*edge)
        removed.append(edge)

    return removed
