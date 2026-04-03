"""
Run the full Python analysis pipeline in order: choice fit → sims → stats → figures.

Usage:
  python scripts/run_all.py
  python scripts/run_all.py --repo-root . --dpi 150
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser(description="fit_choice_model → simulate_confmodels → run_stats_pipeline → plot_makefigs")
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    py = sys.executable
    steps = [
        [py, "scripts/fit_choice_model.py"],
        [py, "scripts/simulate_confmodels.py"],
        [py, "scripts/run_stats_pipeline.py", "--repo-root", str(repo)],
        [py, "scripts/plot_makefigs.py", "--repo-root", str(repo), "--dpi", str(args.dpi)],
    ]
    for cmd in steps:
        print("+", " ".join(cmd), flush=True)
        subprocess.check_call(cmd, cwd=str(repo))
    print("Done.")


if __name__ == "__main__":
    main()
