# depsight — Implementation Plan (Core Engine)

Standalone Python library + CLI, extracted from CodeLens's analysis engine. This is Phase 1 —
build and ship this fully before starting the MCP server wrapper. The MCP server has nothing to
wrap until this exists as a real, installable, tested package.

---

## 1. Project Description

**What it is:** A pip-installable Python library and CLI tool that statically analyzes Python,
JavaScript/TypeScript, and C++ codebases, builds a dependency graph, and runs graph algorithms
against it to surface architectural risk: circular dependencies, critical single-points-of-failure
files, safe build ordering, blast-radius impact analysis, and git-history-based hidden coupling.

**What it is not:** Not a web app, not a visualization tool, not AI-powered. Pure deterministic
graph analysis, usable with zero API keys and zero network access (except the optional temporal
git-mining feature, which needs local git access only, not network).

**Why it's worth building as a separate package:** the analysis core in CodeLens is already good
— hand-rolled DFS 3-coloring, Tarjan's articulation points, Kahn's BFS layering, an MFAS
approximation. Right now it's trapped inside a FastAPI app that requires a browser and a running
server to use. Extracting it makes the same logic usable in CI pipelines, pre-commit hooks, and
(later) inside AI coding agent sessions via the MCP wrapper — none of which need or want a
dashboard.

---

## 2. Requirements

### Functional requirements
- Parse Python (`ast` module), JS/TS, and C++ projects and extract a directed dependency graph
- Detect cycles, return full cycle paths
- Compute topological build order; report cleanly when the graph isn't a DAG
- Find articulation points (critical files) with impact scoring
- Compute parallel build waves
- Run MFAS approximation and produce a ranked refactoring plan
- Compute reverse-BFS blast-radius impact analysis for a given file
- Optional: mine git history for co-change coupling (temporal analysis)
- CLI with human-readable, JSON, and markdown output modes
- CI-friendly exit codes (`--fail-on-cycle`)

### Technical requirements
- Python 3.11+ (matches your existing CodeLens backend)
- Core dependency: `networkx` (already used in CodeLens)
- Optional dependency: `tree-sitter` + language grammars for higher-accuracy JS/TS/C++ parsing,
  falling back to the existing regex parsers when not installed (same fallback behavior you
  already documented in CodeLens)
- `GitPython` — only required if temporal analysis is used; make it an optional extra
  (`depsight[temporal]`), don't force everyone to install it
- CLI framework: `typer` (built on `click`, gives you `--help` generation and type-hint-based
  argument parsing for free — less boilerplate than raw `argparse`)
- `pytest` for testing
- `pyproject.toml`-based packaging (no `setup.py` — that's legacy)
- No hard dependency on FastAPI, Pydantic-for-web, GitHub API, or Groq/LLM anything — those stay
  in the web app or become explicitly optional extras

### Non-functional requirements
- Zero network calls required for core functionality (parsing + graph algorithms run fully
  offline)
- No required API keys — this must work out of the box with `pip install depsight` and nothing
  else, given the whole point is CI/agent-friendliness
- Must run standalone from the CodeLens web app — no shared runtime state, no import of
  `backend.app` or anything FastAPI-shaped

---

## 3. Architecture

```
depsight/
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── src/
│   └── depsight/
│       ├── __init__.py              # public API: analyze(), and re-exports
│       ├── parsers/
│       │   ├── __init__.py          # parse_project() orchestrator + language dispatch
│       │   ├── python_parser.py     # ported from backend/parsers/python_parser.py
│       │   ├── js_parser.py         # ported from backend/parsers/js_parser.py
│       │   └── cpp_parser.py        # ported from backend/parsers/cpp_parser.py
│       ├── graph/
│       │   ├── __init__.py          # re-exports
│       │   ├── builder.py           # DependencyGraph, ported from backend/graph_builder.py
│       │   ├── dfs.py               # detect_cycles(), topological_sort(), find_articulation_points()
│       │   ├── bfs.py               # build_wave_layers()
│       │   ├── mfas.py              # run_mfas()
│       │   └── impact.py            # analyze_impact()
│       ├── temporal/
│       │   ├── __init__.py
│       │   └── git_analysis.py      # mine_temporal_patterns(), optional extra
│       ├── report/
│       │   ├── __init__.py
│       │   ├── models.py            # plain dataclasses/Pydantic models, NOT FastAPI-coupled
│       │   └── formatter.py         # JSON / terminal-table / markdown renderers
│       └── cli.py                   # typer app, entry point for `depsight` command
└── tests/
    ├── conftest.py
    ├── test_parsers.py
    ├── test_graph.py
    ├── test_impact.py
    ├── test_temporal.py
    ├── test_cli.py
    └── fixtures/
        ├── python_complex/          # ported directly from CodeLens sample_projects/
        ├── python_complex_cyclic/
        ├── js_complex/
        ├── js_complex_cyclic/
        ├── cpp_complex/
        └── cpp_complex_cyclic/
```

**Key design rule, decided deliberately:** `parsers/` produces only a plain edge list
(source path, target path, import type, line number) — it never touches `networkx` or graph
algorithms. `graph/` never knows what language produced its edges. This is what lets you add a
4th language later as a parser-only change. Be ready to explain this boundary in an interview —
it's the actual architecture decision that matters here, not the algorithm implementations
themselves (which are already done).

---

## 4. Public API

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

```python
# Direct module access for anyone who wants just one piece
from depsight.parsers import parse_project
from depsight.graph import DependencyGraph, detect_cycles, find_articulation_points, analyze_impact

parse_result = parse_project("/path/to/project")
graph = DependencyGraph.build_from_files(parse_result)
cycles = detect_cycles(graph.nx_graph)
impact = analyze_impact(graph.nx_graph, changed_file="utils.py")
```

```python
# Temporal — explicit opt-in, separate import path, requires the [temporal] extra
from depsight.temporal import mine_temporal_patterns

temporal = mine_temporal_patterns(repo_path="/path/to/repo", max_commits=30, min_cochange=2)
```

---

## 5. CLI Design

```bash
pip install depsight
# or: pip install "depsight[temporal]" for git-mining support

depsight scan ./my-project
depsight scan ./my-project --lang python,typescript
depsight scan ./my-project --only cycles,articulation
depsight scan ./my-project --format json -o report.json
depsight scan ./my-project --format markdown -o report.md
depsight scan ./my-project --fail-on-cycle          # CI mode, non-zero exit on cycle found

depsight impact ./my-project --file utils.py         # standalone blast-radius command

depsight temporal ./my-project --max-commits 30 --min-cochange 2   # requires [temporal] extra
```

---

## 6. Workflow — how to actually build this, in order

### Step 1: Scaffold the package
- `pyproject.toml` with build backend (`hatchling` or `setuptools` — either is fine, `hatchling`
  is the more modern default), project metadata, dependency groups
- Empty package structure per section 3
- Get `pip install -e .` working from a clean venv before writing any real logic — confirms the
  packaging skeleton is correct before you build on top of it

### Step 2: Port parsers (no logic changes yet)
- Copy `python_parser.py`, `js_parser.py`, `cpp_parser.py` into the new structure
- Remove any FastAPI/request-shaped imports if present
- Port the corresponding sample projects into `tests/fixtures/`
- Get `test_parsers.py` passing standalone, disconnected from the old repo

### Step 3: Port the graph builder and algorithms
- `graph_builder.py` → `graph/builder.py`
- `algorithms/dfs.py`, `bfs.py`, `mfas.py`, `impact.py` → `graph/` equivalents
- These are the most self-contained pieces in the original codebase — should port with minimal
  changes, mostly import path fixes
- Port `test_algorithms.py` → `test_graph.py`, running against the new module paths

### Step 4: Define the report models and formatters
- Plain dataclasses or Pydantic models (Pydantic is fine here — it's just not the *web*
  Pydantic models from `models.py`, it's a clean new set)
- JSON formatter first (simplest), then markdown, then a readable terminal-table formatter
  (consider the `rich` library for terminal output — clean tables with minimal code)

### Step 5: Build `analyze()` — the orchestrator
- Single function: parse → build graph → run algorithms → assemble report
- This becomes the one function both the CLI and (later) the MCP server call — keep all real
  logic here, not duplicated in the CLI layer

### Step 6: Build the CLI
- `typer` app in `cli.py`, thin wrapper calling `analyze()` and the formatters
- No business logic in this file — if you find yourself writing analysis logic in `cli.py`,
  it belongs in `analyze()` instead

### Step 7: Temporal analysis as an optional extra
- Port `temporal.py` into `depsight/temporal/`
- Define it as an optional dependency group in `pyproject.toml`:
  `depsight[temporal]` pulls in `GitPython`; base install doesn't
- CLI command should give a clear error ("install depsight[temporal] to use this") rather than
  a raw `ImportError` if the extra isn't installed

### Step 8: Wire up CI
- GitHub Actions workflow: run `pytest` on every push, across at least two Python versions
  (3.11, 3.12) to catch version-specific issues early
- Add a `--fail-on-cycle` test case that specifically verifies the exit code, since that's the
  single most important feature for adoption (see prior conversation: this is the killer feature)

### Step 9: Package for PyPI
- Publish to **TestPyPI first**, verify `pip install depsight --index-url
  https://test.pypi.org/simple/` actually works from a clean environment
- Then publish to real PyPI
- Tag a `v0.1.0` release on GitHub matching the PyPI version

### Step 10: Point CodeLens's FastAPI backend at the new package
- Replace the in-repo copies of parsers/algorithms with `pip install -e ../depsight` (local dev)
  or `pip install depsight` (once published)
- This is the step that proves the extraction actually worked — the original app becomes a
  *consumer* of the new library instead of owning duplicate logic
- Delete the now-redundant code from the CodeLens backend once this is confirmed working

---

## 7. Testing Plan

- **Unit tests per algorithm**, using the six ported sample projects (three languages × cyclic/
  acyclic) — you already have known-correct expected outputs for these from the original 64-test
  suite, reuse that knowledge
- **Parser tests**: confirm each language's parser correctly resolves imports on its sample
  project and handles edge cases (missing files, empty projects, syntax errors) without crashing
- **CLI tests**: use `typer`'s `CliRunner` (or `click.testing.CliRunner`, which `typer` is built
  on) to test actual command invocations, including exit codes for `--fail-on-cycle`
- **Temporal tests**: need a real (small, fixture) git repo with a fabricated commit history —
  build this once as a fixture, don't rely on network access or the actual CodeLens repo
- Target: don't chase 100% coverage, but every public API function needs at least one test, and
  every CLI flag needs at least one invocation test

---

## 8. Todos

### Setup
- [ ] Create new repo, `pyproject.toml`, empty package skeleton
- [ ] `pip install -e .` works from a clean venv
- [ ] CI workflow scaffolded (even before real code exists — get the green checkmark pipeline
      working early)

### Core port
- [ ] Port Python parser + tests
- [ ] Port JS/TS parser + tests
- [ ] Port C++ parser + tests
- [ ] Port `DependencyGraph` builder
- [ ] Port DFS algorithms (cycles, topo sort, articulation points)
- [ ] Port BFS build waves
- [ ] Port MFAS
- [ ] Port impact/blast-radius analysis
- [ ] Port six sample-project fixtures from CodeLens

### New work (didn't exist before, needs building fresh)
- [ ] Design and implement report models (dataclasses/Pydantic, non-web)
- [ ] JSON formatter
- [ ] Markdown formatter
- [ ] Terminal table formatter (`rich`, optional but recommended)
- [ ] `analyze()` orchestrator function
- [ ] CLI (`typer`) with `scan`, `impact`, `temporal` subcommands
- [ ] `--fail-on-cycle` exit code behavior + test
- [ ] `--only` flag to run a subset of algorithms

### Temporal (optional extra)
- [ ] Port `mine_temporal_patterns`
- [ ] Define `depsight[temporal]` extra in `pyproject.toml`
- [ ] Graceful error when extra isn't installed but temporal command is invoked
- [ ] Build a small fixture git repo for testing (fabricated commit history)

### Packaging & release
- [ ] README with real install + usage examples (not placeholder text)
- [ ] LICENSE (MIT)
- [ ] CHANGELOG.md
- [ ] Publish to TestPyPI, verify clean-env install
- [ ] Publish v0.1.0 to real PyPI
- [ ] Tag GitHub release matching PyPI version

### Integration back into CodeLens
- [ ] Point CodeLens's FastAPI backend at the new `depsight` package
- [ ] Delete redundant duplicated logic from the CodeLens repo
- [ ] Confirm CodeLens's existing 64-test suite (whatever remains after this migration) still
      passes end to end

**Do not start the MCP server plan (next file) until every box above is checked and `v0.1.0` is
live on PyPI.** The MCP server has nothing real to wrap until then.
