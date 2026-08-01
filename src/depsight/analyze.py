"""Orchestrator: parse → build graph → run algorithms → assemble report."""

from __future__ import annotations

from pathlib import Path

import networkx as nx

from depsight.graph import (
    DependencyGraph,
    analyze_impact,
    build_wave_layers,
    detect_cycles,
    find_articulation_points,
    run_mfas,
    topological_sort,
)
from depsight.parsers import parse_cpp_project, parse_js_project, parse_python_project
from depsight.report.models import AnalysisResult, ArticulationPoint, Cycle, ImpactResult


def analyze(
    project_path: str | Path,
    languages: list[str] | None = None,
    impact_file: str | None = None,
    include_temporal: bool = False,
    max_commits: int = 100,
    min_cochange: int = 2,
) -> AnalysisResult:
    root = Path(project_path).resolve()

    # Parse each language
    parse_results: dict[str, list] = {}
    all_edges = []

    if languages is None or "python" in languages:
        edges = parse_python_project(root)
        if edges:
            parse_results["python"] = edges
            all_edges.extend(edges)

    if languages is None or "javascript" in languages or "typescript" in languages:
        edges = parse_js_project(root)
        if edges:
            parse_results["javascript"] = edges
            all_edges.extend(edges)

    if languages is None or "cpp" in languages:
        edges = parse_cpp_project(root)
        if edges:
            parse_results["cpp"] = edges
            all_edges.extend(edges)

    # Build graph
    graph = DependencyGraph.build_from_edges(all_edges)

    # Run algorithms
    cycles = [Cycle(path=c) for c in detect_cycles(graph.nx_graph)]
    build_order = topological_sort(graph.nx_graph)

    # Articulation points with impact scoring
    aps = find_articulation_points(graph.nx_graph)
    articulation_points = []
    for ap in aps:
        # Impact score: number of nodes that would be disconnected
        undirected = graph.nx_graph.to_undirected()
        undirected.remove_node(ap)
        components = len(list(nx.connected_components(undirected)))
        articulation_points.append(ArticulationPoint(
            file=ap,
            impact_score=float(components),
            components=components,
        ))

    build_waves = build_wave_layers(graph.nx_graph)
    mfas = run_mfas(graph.nx_graph)

    impact = None
    if impact_file:
        impact_res = analyze_impact(graph.nx_graph, impact_file)
        if impact_res:
            impact = ImpactResult(
                changed_file=impact_res.changed_file,
                directly_affected=impact_res.directly_affected,
                transitively_affected=impact_res.transitively_affected,
                total_affected=impact_res.total_affected,
            )

    temporal_patterns = []
    if include_temporal:
        from depsight.temporal import mine_temporal_patterns
        if mine_temporal_patterns:
            temporal_patterns = mine_temporal_patterns(root, max_commits, min_cochange)

    return AnalysisResult(
        project_path=str(root),
        languages=list(parse_results.keys()),
        total_files=len(graph.nodes()),
        total_edges=len(all_edges),
        cycles=cycles,
        build_order=build_order,
        articulation_points=articulation_points,
        build_waves=build_waves,
        mfas=mfas,
        impact=impact,
        temporal_patterns=temporal_patterns,
    )
