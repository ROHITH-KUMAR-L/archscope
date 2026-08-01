"""Report formatters: JSON, Markdown, terminal table."""

from __future__ import annotations

import json

from archscope.report.models import AnalysisResult


def format_json(result: AnalysisResult) -> str:
    return json.dumps(result.to_dict(), indent=2)


def format_markdown(result: AnalysisResult) -> str:
    lines = [
        "# archscope Analysis Report",
        "",
        f"**Project:** {result.project_path}",
        f"**Languages:** {', '.join(result.languages) if result.languages else 'none detected'}",
        f"**Files:** {result.total_files}",
        f"**Dependencies:** {result.total_edges}",
        "",
    ]

    if result.cycles:
        lines.append(f"## Cycles ({len(result.cycles)})")
        for i, cycle in enumerate(result.cycles, 1):
            lines.append(f"### Cycle {i}")
            lines.append(" -> ".join(cycle.path))
            lines.append("")
    else:
        lines.append("## Cycles: None found")
        lines.append("")

    if result.build_order:
        lines.append("## Build Order")
        for i, file in enumerate(result.build_order, 1):
            lines.append(f"{i}. {file}")
        lines.append("")
    else:
        lines.append("## Build Order: Not available (cycles present)")
        lines.append("")

    if result.articulation_points:
        lines.append(
            f"## Articulation Points ({len(result.articulation_points)})"
        )
        for ap in result.articulation_points:
            lines.append(
                f"- **{ap.file}** "
                f"(impact: {ap.impact_score:.2f}, "
                f"components: {ap.components})"
            )
        lines.append("")

    if result.build_waves:
        lines.append("## Build Waves (Parallel Layers)")
        for i, wave in enumerate(result.build_waves, 1):
            lines.append(f"### Wave {i}")
            for file in wave:
                lines.append(f"- {file}")
            lines.append("")

    if result.mfas:
        lines.append(f"## MFAS Refactor Priority ({len(result.mfas)} edges to remove)")
        for source, target in result.mfas:
            lines.append(f"- {source} → {target}")
        lines.append("")

    if result.impact:
        lines.append("## Impact Analysis")
        lines.append(f"**Changed file:** {result.impact.changed_file}")
        lines.append(f"**Directly affected:** {len(result.impact.directly_affected)}")
        lines.append(f"**Transitively affected:** {len(result.impact.transitively_affected)}")
        lines.append(f"**Total blast radius:** {result.impact.total_affected}")
        lines.append("")

    return "\n".join(lines)


def format_table(result: AnalysisResult) -> str:
    lines = []

    # Summary
    lines.append("archscope Summary")
    lines.append("=" * 50)
    lines.append(f"Project:          {result.project_path}")
    lines.append(f"Languages:        {', '.join(result.languages) if result.languages else 'none'}")
    lines.append(f"Files:            {result.total_files}")
    lines.append(f"Dependencies:     {result.total_edges}")
    lines.append(f"Cycles:           {len(result.cycles)}")
    lines.append(f"Articulation Pts: {len(result.articulation_points)}")
    lines.append(f"Build Waves:      {len(result.build_waves) if result.build_waves else 'N/A'}")
    lines.append(f"MFAS Edges:       {len(result.mfas)}")
    lines.append("")

    # Cycles
    if result.cycles:
        lines.append("Cycles")
        lines.append("-" * 50)
        for i, cycle in enumerate(result.cycles, 1):
            lines.append(f"  {i}. {' -> '.join(cycle.path)}")
        lines.append("")

    # Articulation points
    if result.articulation_points:
        lines.append("Articulation Points")
        lines.append("-" * 50)
        for ap in result.articulation_points:
            lines.append(
                f"  {ap.file} "
                f"(impact: {ap.impact_score:.2f}, "
                f"components: {ap.components})"
            )
        lines.append("")

    # Build waves
    if result.build_waves:
        lines.append("Build Waves")
        lines.append("-" * 50)
        for i, wave in enumerate(result.build_waves, 1):
            lines.append(f"  Wave {i}: {', '.join(wave)}")
        lines.append("")

    # Impact
    if result.impact:
        lines.append("Impact Analysis")
        lines.append("-" * 50)
        lines.append(f"  Changed file:    {result.impact.changed_file}")
        lines.append(f"  Directly affected: {len(result.impact.directly_affected)}")
        lines.append(f"  Transitively affected: {len(result.impact.transitively_affected)}")
        lines.append(f"  Total blast radius: {result.impact.total_affected}")
        lines.append("")

    return "\n".join(lines)
