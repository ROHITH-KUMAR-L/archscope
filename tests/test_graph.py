"""Tests for graph algorithms."""

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
from depsight.graph.builder import Edge


class TestDependencyGraph:
    def test_build_from_edges(self) -> None:
        edges = [
            Edge(source="a.py", target="b.py", import_type="import", line=1),
            Edge(source="b.py", target="c.py", import_type="import", line=1),
        ]
        graph = DependencyGraph.build_from_edges(edges)
        assert "a.py" in graph.nodes()
        assert "b.py" in graph.nodes()
        assert "c.py" in graph.nodes()
        assert graph.nx_graph.has_edge("a.py", "b.py")
        assert graph.nx_graph.has_edge("b.py", "c.py")

    def test_empty_graph(self) -> None:
        graph = DependencyGraph.build_from_edges([])
        assert len(graph.nodes()) == 0


class TestDetectCycles:
    def test_acyclic_graph(self) -> None:
        g = nx.DiGraph()
        g.add_edge("a", "b")
        g.add_edge("b", "c")
        cycles = detect_cycles(g)
        assert cycles == []

    def test_cyclic_graph(self) -> None:
        g = nx.DiGraph()
        g.add_edge("a", "b")
        g.add_edge("b", "a")
        cycles = detect_cycles(g)
        assert len(cycles) > 0
        assert set(cycles[0]) == {"a", "b"}

    def test_self_loop(self) -> None:
        g = nx.DiGraph()
        g.add_edge("a", "a")
        cycles = detect_cycles(g)
        assert len(cycles) > 0


class TestTopologicalSort:
    def test_dag(self) -> None:
        g = nx.DiGraph()
        g.add_edge("a", "b")
        g.add_edge("b", "c")
        order = topological_sort(g)
        assert order is not None
        assert order.index("a") < order.index("b")
        assert order.index("b") < order.index("c")

    def test_cyclic_graph_returns_none(self) -> None:
        g = nx.DiGraph()
        g.add_edge("a", "b")
        g.add_edge("b", "a")
        order = topological_sort(g)
        assert order is None


class TestFindArticulationPoints:
    def test_no_articulation_points(self) -> None:
        g = nx.DiGraph()
        g.add_edge("a", "b")
        g.add_edge("b", "c")
        g.add_edge("a", "c")
        aps = find_articulation_points(g)
        assert "b" not in aps or len(aps) == 0

    def test_single_articulation_point(self) -> None:
        g = nx.DiGraph()
        g.add_edge("a", "b")
        g.add_edge("c", "b")
        aps = find_articulation_points(g)
        assert "b" in aps


class TestBuildWaveLayers:
    def test_dag_waves(self) -> None:
        g = nx.DiGraph()
        g.add_edge("a", "b")
        g.add_edge("a", "c")
        g.add_edge("b", "d")
        g.add_edge("c", "d")
        waves = build_wave_layers(g)
        assert waves is not None
        assert len(waves) >= 2

    def test_cyclic_graph_returns_none(self) -> None:
        g = nx.DiGraph()
        g.add_edge("a", "b")
        g.add_edge("b", "a")
        waves = build_wave_layers(g)
        assert waves is None


class TestMFAS:
    def test_acyclic_graph_returns_empty(self) -> None:
        g = nx.DiGraph()
        g.add_edge("a", "b")
        g.add_edge("b", "c")
        mfas = run_mfas(g)
        assert mfas == []

    def test_cyclic_graph_returns_edges(self) -> None:
        g = nx.DiGraph()
        g.add_edge("a", "b")
        g.add_edge("b", "a")
        mfas = run_mfas(g)
        assert len(mfas) > 0


class TestAnalyzeImpact:
    def test_impact_on_leaf(self) -> None:
        g = nx.DiGraph()
        g.add_edge("a", "b")
        g.add_edge("b", "c")
        result = analyze_impact(g, "c")
        assert result is not None
        assert result.changed_file == "c"
        assert "b" in result.directly_affected
        assert "a" in result.transitively_affected

    def test_impact_on_node_with_no_dependents(self) -> None:
        g = nx.DiGraph()
        g.add_edge("a", "b")
        result = analyze_impact(g, "b")
        assert result is not None
        assert result.total_affected == 1
        assert "a" in result.directly_affected

    def test_impact_on_missing_file(self) -> None:
        g = nx.DiGraph()
        g.add_edge("a", "b")
        result = analyze_impact(g, "nonexistent")
        assert result is None
