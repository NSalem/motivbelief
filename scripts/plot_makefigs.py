"""
Single entry point for all figure generators.
Outputs go to `<repo>/plots/` (PNG + SVG).

Examples:
  python scripts/plot_makefigs.py
  python scripts/plot_makefigs.py --repo-root . --dpi 200
  python scripts/plot_makefigs.py --only behav glm
  python scripts/plot_makefigs.py --only xpatt psyfun
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Sequence

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO / "src") not in sys.path:
    sys.path.insert(0, str(_REPO / "src"))

from motivbelief.plot_makefigs_behav import plot_behav_figure
from motivbelief.plot_makefigs_falsif_xpatt import plot_falsif_xpatt_figure
from motivbelief.plot_makefigs_glm import plot_glm_figure
from motivbelief.plot_makefigs_model_avg import plot_model_avg_figure
from motivbelief.plot_makefigs_psyfun import plot_psychometric_incentive_figure
from motivbelief.plot_makefigs_xpatt import plot_xpatt_by_experiment, plot_xpatt_data_vs_models

FIG_GROUPS = ("model_avg", "xpatt", "falsif_xpatt", "behav", "glm", "psyfun")


def run_figures(repo: Path, dpi: int, only: Sequence[str] | None) -> List[Path]:
    """Run selected figure generators; `only` None or [] means all."""
    if only is None or len(only) == 0:
        want = set(FIG_GROUPS)
    else:
        want = set(x.lower() for x in only)
    if "all" in want:
        want = set(FIG_GROUPS)

    unknown = want - set(FIG_GROUPS)
    if unknown:
        raise SystemExit(f"Unknown --only names: {sorted(unknown)}. Valid: all, {', '.join(FIG_GROUPS)}")

    outs: List[Path] = []
    if "model_avg" in want:
        outs.append(plot_model_avg_figure(repo, dpi=dpi))
    if "xpatt" in want:
        outs.append(plot_xpatt_by_experiment(repo, dpi=dpi))
        outs.append(plot_xpatt_data_vs_models(repo, dpi=dpi))
    if "falsif_xpatt" in want:
        outs.append(plot_falsif_xpatt_figure(repo, dpi=dpi))
    if "behav" in want:
        outs.extend(plot_behav_figure(repo, dpi=dpi))
    if "glm" in want:
        outs.extend(plot_glm_figure(repo, dpi=dpi))
    if "psyfun" in want:
        outs.append(plot_psychometric_incentive_figure(repo, dpi=dpi))
    return outs


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generate figures into plots/ (PNG + SVG).",
    )
    ap.add_argument("--repo-root", type=Path, default=Path("."), help="Project root (default: cwd)")
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument(
        "--only",
        nargs="*",
        default=None,
        metavar="NAME",
        help=(
            "Which figure groups to build (default: all). "
            f"Names: {', '.join(FIG_GROUPS)}, or all. Example: --only behav glm"
        ),
    )
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    outs = run_figures(repo, args.dpi, args.only)
    for p in outs:
        print(p)


if __name__ == "__main__":
    main()
