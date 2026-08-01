"""Report data models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Cycle:
    path: list[str]


@dataclass
class ArticulationPoint:
    file: str
    impact_score: float
    components: int


@dataclass
class ImpactResult:
    changed_file: str
    directly_affected: list[str]
    transitively_affected: list[str]
    total_affected: int


@dataclass
class AnalysisResult:
    project_path: str
    languages: list[str]
    total_files: int
    total_edges: int
    cycles: list[Cycle] = field(default_factory=list)
    build_order: list[str] | None = None
    articulation_points: list[ArticulationPoint] = field(default_factory=list)
    build_waves: list[list[str]] | None = None
    mfas: list[tuple[str, str]] = field(default_factory=list)
    impact: ImpactResult | None = None
    temporal_patterns: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "project_path": self.project_path,
            "languages": self.languages,
            "total_files": self.total_files,
            "total_edges": self.total_edges,
            "cycles": [{"path": c.path} for c in self.cycles],
            "build_order": self.build_order,
            "articulation_points": [
                {"file": a.file, "impact_score": a.impact_score, "components": a.components}
                for a in self.articulation_points
            ],
            "build_waves": self.build_waves,
            "mfas": [{"source": s, "target": t} for s, t in self.mfas],
            "impact": {
                "changed_file": self.impact.changed_file,
                "directly_affected": self.impact.directly_affected,
                "transitively_affected": self.impact.transitively_affected,
                "total_affected": self.impact.total_affected,
            } if self.impact else None,
            "temporal_patterns": [
                {
                    "file_a": p.file_a,
                    "file_b": p.file_b,
                    "co_change_count": p.co_change_count,
                    "commits": p.commits,
                }
                for p in self.temporal_patterns
            ],
        }
