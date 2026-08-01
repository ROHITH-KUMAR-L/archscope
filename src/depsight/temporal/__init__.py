"""Temporal (git history) analysis — optional extra."""

try:
    from depsight.temporal.git_analysis import mine_temporal_patterns
except ImportError:
    mine_temporal_patterns = None

__all__ = ["mine_temporal_patterns"]
