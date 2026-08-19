"""
Run the full Python analysis pipeline in order:
  choice fit → Free conf fit → [Free recovery if --with-recovery] → BMC → sims → stats → figures.

Usage:
  python scripts/run_all.py
  python scripts/run_all.py --repo-root . --dpi 150
  python scripts/run_all.py --with-recovery   # Free recovery + identifiability (expensive)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "fit_choice_model → fit_conf_free → [recover_free → analyze_recovery] → "
            "compare_conf_free → simulate_belief → run_stats_pipeline → plot_figures"
        )
    )
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument(
        "--with-recovery",
        action="store_true",
        help=(
            "Also run Free recovery (recover_free.py) and "
            "analyze_recovery_identifiability.py. Off by default — full recovery "
            "is expensive (hundreds of synthetic participants × cross-fits)."
        ),
    )
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    py = sys.executable
    steps = [
        [py, "scripts/fit_choice_model.py"],
        [py, "scripts/fit_conf_free.py"],
    ]
    if args.with_recovery:
        steps.extend(
            [
                [py, "scripts/recover_free.py"],
                [py, "scripts/analyze_recovery_identifiability.py"],
            ]
        )
    steps.extend(
        [
            [py, "scripts/compare_conf_free.py", "--repo-root", str(repo)],
            [py, "scripts/simulate_belief.py"],
            [py, "scripts/run_stats_pipeline.py", "--repo-root", str(repo)],
            [py, "scripts/plot_figures.py", "--repo-root", str(repo), "--dpi", str(args.dpi)],
        ]
    )
    for cmd in steps:
        print("+", " ".join(cmd), flush=True)
        subprocess.check_call(cmd, cwd=str(repo))
    print("Done.")


if __name__ == "__main__":
    main()
