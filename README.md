# depsight

Static dependency-graph analysis for Python, JavaScript/TypeScript, and C++.

## Installation

```bash
pip install depsight
# or with temporal (git history) analysis:
pip install "depsight[temporal]"
```

## Usage

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

# CI mode: fail on cycles
depsight scan ./my-project --fail-on-cycle

# Blast radius impact analysis
depsight impact ./my-project --file utils.py

# Temporal coupling (requires [temporal] extra)
depsight temporal ./my-project --max-commits 30 --min-cochange 2
```

## Python API

```python
from depsight import analyze

result = analyze("/path/to/project")

result.graph                  # underlying DependencyGraph
result.cycles                 # from detect_cycles()
result.build_order            # from topological_sort() — None if cycles exist
result.articulation_points    # from find_articulation_points()
result.build_waves            # from build_wave_layers()
result.mfas                   # from run_mfas()
result.to_json()
result.to_markdown()
```

## Architecture

- `parsers/` — produces edge lists only, no graph logic
- `graph/` — pure graph algorithms, no language awareness
- `temporal/` — optional git history mining (requires `depsight[temporal]`)

## License

MIT