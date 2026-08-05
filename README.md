# archsight — Dependency Graph Analysis Engine

> Detect cycles, find critical files, compute safe build order, and measure blast-radius impact using classical graph algorithms — no API keys, no network, no dashboard required.

![Language](https://img.shields.io/badge/Language-Python%203.11%2B-blue) ![CLI](https://img.shields.io/badge/CLI-Typer-4B8BBE) ![Graph](https://img.shields.io/badge/Graph-NetworkX-orange) ![Optional](https://img.shields.io/badge/Optional-GitPython%20%2F%20tree--sitter-9cf) ![License](https://img.shields.io/badge/License-MIT-brightgreen)

---

## Executive Summary

`archsight` is a pip-installable Python library and CLI that statically analyzes Python, JavaScript/TypeScript, and C++ codebases, builds a directed dependency graph, and runs graph algorithms against it to surface architectural risk.

It is a pure, deterministic analysis engine — not a web app, not a visualization tool, not AI-powered. It runs fully offline (aside from the optional local git-mining feature) and is built to drop into CI pipelines, pre-commit hooks, and agent sessions without a running server or a browser.

| | |
|---|---|
| **Cycle detection** | Find circular dependencies with full cycle paths |
| **Build ordering** | Compute a safe topological build order |
| **Critical files** | Identify articulation points — single points of failure |
| **Parallel waves** | Group files into build layers that can run concurrently |
| **Blast radius** | See what breaks if you change a given file |
| **Refactor plan** | Rank the minimum edges to cut to make the graph acyclic (MFAS) |
| **Temporal coupling** | Mine git history for hidden co-change relationships *(optional)* |

---

## Installation

```bash
pip install archsight

# with temporal (git history) analysis:
pip install "archsight[temporal]"
```

Requires **Python 3.11+**.

---

## Quick start

```bash
archsight scan ./my-project --fail-on-cycle
```

Human-readable output in your terminal, non-zero exit code if a cycle is found. Wire it into CI and you're done.

---

## CLI

```bash
# Scan a project
archsight scan ./my-project

# Scan only specific languages
archsight scan ./my-project --lang python,javascript

# Run a subset of algorithms
archsight scan ./my-project --only cycles,articulation

# Output formats
archsight scan ./my-project --format json -o report.json
archsight scan ./my-project --format markdown -o report.md

# CI mode: exit code 1 if cycles found
archsight scan ./my-project --fail-on-cycle

# Blast-radius impact analysis for a single file
archsight impact ./my-project --file utils.py

# Temporal coupling (requires the [temporal] extra)
archsight temporal ./my-project --max-commits 30 --min-cochange 2
```

<details>
<summary><strong>All flags</strong></summary>

| Flag | Description |
|---|---|
| `--lang` | Comma-separated list of languages to include |
| `--only` | Comma-separated list of algorithms to run |
| `--format` | `text` (default), `json`, or `markdown` |
| `-o, --output` | Write report to a file instead of stdout |
| `--fail-on-cycle` | Exit with code `1` if any cycle is detected |
| `--max-commits` | *(temporal)* Number of commits to mine |
| `--min-cochange` | *(temporal)* Minimum co-change count to report a coupling |

</details>

---

## Python API

```python
from archsight import analyze

result = analyze("/path/to/project")

result.cycles                 # list of Cycle objects
result.build_order            # topological order, or None if cycles exist
result.articulation_points    # list of ArticulationPoint objects
result.build_waves            # parallel build layers, or None if cyclic
result.mfas                   # edges to remove for acyclic refactoring
result.impact                 # ImpactResult for a changed file, if requested
```

Format the result however you need:

```python
from archsight.report import format_json, format_markdown, format_table

print(format_json(result))
print(format_markdown(result))
print(format_table(result))
```

---

## Architecture

```
parsers/   →  produces edge lists only (source, target, import type, line)
               never touches networkx or graph algorithms

graph/     →  pure graph algorithms
               never knows what language produced its edges

temporal/  →  optional git history mining (requires archsight[temporal])
```

This boundary is deliberate: adding a 4th language is a **parser-only** change — the graph algorithms don't change at all.

---

## Testing

```bash
pip install -e ".[test]"
pytest tests/ -v
```

---

## License

MIT