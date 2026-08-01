# depsight

Static dependency-graph analysis for Python, JavaScript/TypeScript, and C++.

Detects cycles, finds critical files (articulation points), computes safe build
ordering, measures blast-radius impact, and ranks refactoring priority using a
Minimum Feedback Arc Set approximation.

## Installation

```bash
pip install depsight
# or with temporal (git history) analysis:
pip install "depsight[temporal]"
```

## Usage

### CLI

```bash
# Scan a project
depsight scan ./my-project

# Scan with specific languages
depsight scan ./my-project --lang python,javascript

# Only run specific algorithms
depsight scan ./my-project --only cycles,articulation

# Output formats
depsight scan ./my-project --format json -o report.json
depsight scan ./my-project --format markdown -o report.md

# CI mode: exit code 1 if cycles found
depsight scan ./my-project --fail-on-cycle

# Blast radius impact analysis
depsight impact ./my-project --file utils.py

# Temporal coupling (requires [temporal] extra)
depsight temporal ./my-project --max-commits 30 --min-cochange 2
```

### Python API

```python
from depsight import analyze

result = analyze("/path/to/project")

# Access results
result.cycles                 # list of Cycle objects
result.build_order            # topological order, or None if cycles exist
result.articulation_points    # list of ArticulationPoint objects
result.build_waves            # parallel build layers, or None if cyclic
result.mfas                   # edges to remove for acyclic refactoring
result.impact                 # ImpactResult for a changed file (if requested)
```

For formatted output, use the formatter functions directly:

```python
from depsight.report import format_json, format_markdown, format_table

print(format_json(result))
print(format_markdown(result))
print(format_table(result))
```

## Architecture

- `parsers/` — produces edge lists only (source, target, import type, line).
  Never touches `networkx` or graph algorithms.
- `graph/` — pure graph algorithms. Never knows what language produced its edges.
- `temporal/` — optional git history mining (requires `depsight[temporal]`).

This boundary means adding a 4th language is a parser-only change.

## Testing

```bash
pip install -e ".[test]"
pytest tests/ -v
```

## License

MIT