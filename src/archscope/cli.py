"""CLI entry point using Typer."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from archscope import analyze
from archscope.report import format_json, format_markdown, format_table

app = typer.Typer(
    name="archscope",
    help="Static dependency-graph analysis for Python, JavaScript/TypeScript, and C++",
    add_completion=False,
)
console = Console()


@app.command()
def scan(
    path: Path = typer.Argument(..., help="Path to project root"),  # noqa: B008
    lang: str | None = typer.Option(
        None,
        "--lang",
        "-l",
        help="Comma-separated languages: python,javascript,typescript,cpp",
    ),
    only: str | None = typer.Option(
        None,
        "--only",
        help="Comma-separated algorithms: cycles,articulation,build_order,waves,mfas,impact",
    ),
    format: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, markdown"
    ),
output: Path | None = typer.Option(  # noqa: B008
        None, "--output", "-o", help="Write output to file instead of stdout"
    ),
    fail_on_cycle: bool = typer.Option(
        False, "--fail-on-cycle", help="Exit with code 1 if cycles found"
    ),
    impact_file: str | None = typer.Option(
        None, "--impact-file", help="File to analyze blast radius for"
    ),
):
    """Scan a project and report dependency analysis."""
    lang_val = lang
    languages = [v.strip() for v in lang_val.split(",")] if lang_val else None
    only_algos = [a.strip() for a in only.split(",")] if only else None

    result = analyze(
        project_path=path,
        languages=languages,
        impact_file=impact_file,
        include_temporal=False,
    )

    # Filter results if --only specified
    if only_algos:
        if "cycles" not in only_algos:
            result.cycles = []
        if "articulation" not in only_algos:
            result.articulation_points = []
        if "build_order" not in only_algos:
            result.build_order = None
        if "waves" not in only_algos:
            result.build_waves = None
        if "mfas" not in only_algos:
            result.mfas = []
        if "impact" not in only_algos:
            result.impact = None

    # Format output
    if format == "json":
        out = format_json(result)
    elif format == "markdown":
        out = format_markdown(result)
    else:
        out = format_table(result)

    if output:
        output.write_text(out)
        console.print(f"[green]Report written to {output}[/green]")
    else:
        console.print(out)

    # Exit code for CI
    if fail_on_cycle and result.cycles:
        raise typer.Exit(code=1)


@app.command()
def impact(
    path: Path = typer.Argument(..., help="Path to project root"),  # noqa: B008
    file: str = typer.Argument(..., help="File to analyze blast radius for"),  # noqa: B008
    lang: str | None = typer.Option(
        None, "--lang", "-l", help="Comma-separated languages"
    ),
    format: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, markdown"
    ),
output: Path | None = typer.Option(  # noqa: B008
        None, "--output", "-o", help="Write output to file"
    ),
):
    """Analyze blast radius impact of changing a specific file."""
    lang_val = lang
    languages = [v.strip() for v in lang_val.split(",")] if lang_val else None

    result = analyze(
        project_path=path,
        languages=languages,
        impact_file=file,
        include_temporal=False,
    )

    if result.impact is None:
        console.print(f"[red]File '{file}' not found in project[/red]")
        raise typer.Exit(code=1)

    # Format output
    if format == "json":
        out = format_json(result)
    elif format == "markdown":
        out = format_markdown(result)
    else:
        out = format_table(result)

    if output:
        output.write_text(out)
        console.print(f"[green]Report written to {output}[/green]")
    else:
        console.print(out)


@app.command()
def temporal(
    path: Path = typer.Argument(..., help="Path to git repository"),  # noqa: B008
    max_commits: int = typer.Option(
        100, "--max-commits", help="Maximum commits to analyze"
    ),
    min_cochange: int = typer.Option(
        2, "--min-cochange", help="Minimum co-change count to report"
    ),
    format: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, markdown"
    ),
output: Path | None = typer.Option(  # noqa: B008
        None, "--output", "-o", help="Write output to file"
    ),
):
    """Mine git history for temporal coupling patterns (requires archscope[temporal])."""
    try:
        from archscope.temporal import mine_temporal_patterns
    except ImportError:
        console.print("[red]Temporal analysis requires the [temporal] extra.[/red]")
        console.print(
            "Install with: [cyan]pip install archscope[temporal][/cyan]"
        )
        raise typer.Exit(code=1) from None

    if mine_temporal_patterns is None:
        console.print(
            "[red]GitPython not installed. "
            "Install with: pip install archscope[temporal][/red]"
        )
        raise typer.Exit(code=1) from None

    patterns = mine_temporal_patterns(path, max_commits, min_cochange)

    if format == "json":
        out = json.dumps(
            [
                {
                    "file_a": p.file_a,
                    "file_b": p.file_b,
                    "co_change_count": p.co_change_count,
                    "commits": p.commits,
                }
                for p in patterns
            ],
            indent=2,
        )
    elif format == "markdown":
        lines = ["# Temporal Coupling Patterns", ""]
        for p in patterns:
            lines.append(
                f"- **{p.file_a}** <-> **{p.file_b}** "
                f"({p.co_change_count} co-changes)"
            )
        out = "\n".join(lines)
    else:
        from rich.table import Table

        table = Table(title="Temporal Coupling Patterns")
        table.add_column("File A", style="cyan")
        table.add_column("File B", style="cyan")
        table.add_column("Co-changes", style="magenta")
        table.add_column("Commits", style="dim")
        for p in patterns:
            table.add_row(
                p.file_a,
                p.file_b,
                str(p.co_change_count),
                ", ".join(p.commits),
            )
        console.print(table)
        return

    if output:
        output.write_text(out)
        console.print(f"[green]Report written to {output}[/green]")
    else:
        console.print(out)


if __name__ == "__main__":
    app()
