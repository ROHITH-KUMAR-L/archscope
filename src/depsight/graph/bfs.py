"""BFS-based build wave layering (Kahn's algorithm)."""

from __future__ import annotations

import networkx as nx


def build_wave_layers(graph: nx.DiGraph) -> list[list[str]] | None:
    """Return list of build waves (parallel layers) if DAG, else None."""
    if not nx.is_directed_acyclic_graph(graph):
        return None

    # Kahn's algorithm with level tracking
    in_degree = {n: graph.in_degree(n) for n in graph.nodes()}
    queue = [n for n, d in in_degree.items() if d == 0]
    layers: list[list[str]] = []

    while queue:
        layers.append(queue[:])
        next_queue = []
        for node in queue:
            for succ in graph.successors(node):
                in_degree[succ] -= 1
                if in_degree[succ] == 0:
                    next_queue.append(succ)
        queue = next_queue

    return layers
