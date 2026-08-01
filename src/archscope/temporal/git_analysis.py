"""Temporal analysis via git history mining — requires archscope[temporal] extra."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    from git import Repo
except ImportError:
    Repo = None  # type: ignore


@dataclass
class TemporalPattern:
    file_a: str
    file_b: str
    co_change_count: int
    commits: list[str]


def mine_temporal_patterns(
    repo_path: str | Path,
    max_commits: int = 100,
    min_cochange: int = 2,
) -> list[TemporalPattern]:
    if Repo is None:
        raise ImportError("GitPython not installed. Install with: pip install archscope[temporal]")

    repo = Repo(repo_path)
    if repo.bare:
        raise ValueError("Not a valid git repository")

    co_changes: dict[tuple[str, str], list[str]] = {}

    for commit in list(repo.iter_commits(max_count=max_commits)):
        files = list(commit.stats.files.keys())
        if len(files) < 2:
            continue
        for i, f1 in enumerate(files):
            for f2 in files[i + 1:]:
                key = tuple(sorted((f1, f2)))
                co_changes.setdefault(key, []).append(commit.hexsha[:8])

    patterns = []
    for (f1, f2), commits in co_changes.items():
        if len(commits) >= min_cochange:
            patterns.append(TemporalPattern(
                file_a=f1,
                file_b=f2,
                co_change_count=len(commits),
                commits=commits,
            ))

    return sorted(patterns, key=lambda p: p.co_change_count, reverse=True)
