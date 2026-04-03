"""Resolve results paths for figure scripts."""

from __future__ import annotations

from pathlib import Path


def _stats_branch(repo: Path, name: str) -> Path:
    """Prefer `results/stats/{name}` (canonical Python outputs); fall back to `stats_py` if needed."""
    repo = repo.resolve()
    st = repo / "results" / "stats" / name
    py = repo / "results" / "stats_py" / name
    if st.is_dir():
        return st
    return py if py.is_dir() else st


def stats_avg_root(repo: Path) -> Path:
    return _stats_branch(repo, "average")


def stats_trial_root(repo: Path) -> Path:
    return _stats_branch(repo, "trial")


def fig_dir(repo: Path) -> Path:
    """Output directory for all `plot_makefigs_*` figures (`<repo>/plots`)."""
    d = repo.resolve() / "plots"
    d.mkdir(parents=True, exist_ok=True)
    return d
