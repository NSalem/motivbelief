"""
Single entry point for all figure generators.
Outputs go to `<repo>/plots/` (PNG + SVG).

Examples:
  python scripts/plot_figures.py
  python scripts/plot_figures.py --repo-root . --dpi 200
  python scripts/plot_figures.py --only behav glm
  python scripts/plot_figures.py --only xpatt psyfun
  python scripts/plot_figures.py --only xpatt_coh   # optional figures
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import List, Sequence

# Headless-friendly default before any matplotlib import via plotting modules.
os.environ.setdefault("MPLBACKEND", "Agg")

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO / "src") not in sys.path:
    sys.path.insert(0, str(_REPO / "src"))

from motivbelief.plotting.fig_behav import plot_behav_figure
from motivbelief.plotting.fig_bmc import plot_free_bmc_figure
from motivbelief.plotting.fig_calib import plot_calib_by_experiment, plot_calib_data_vs_models
from motivbelief.plotting.fig_chosen_contribution import plot_chosen_contribution_figure
from motivbelief.plotting.fig_falsif import plot_falsif_xpatt_figure
from motivbelief.plotting.fig_glm import plot_glm_figure
from motivbelief.plotting.fig_hmeta import plot_hmeta_figures
from motivbelief.plotting.fig_model_avg import plot_model_avg_figure
from motivbelief.plotting.fig_params import plot_params_figure
from motivbelief.plotting.fig_psyfun import plot_psychometric_incentive_figure
from motivbelief.plotting.fig_recov import plot_recov_figures
from motivbelief.plotting.fig_xpatt import (
    plot_xpatt_by_experiment,
    plot_xpatt_data_vs_models,
    plot_xpatt_empirical_overlay_models,
)

# Default = paper core (includes Free recovery figures).
FIG_GROUPS = (
    "model_avg",
    "xpatt",
    "falsif_xpatt",
    "calib",
    "behav",
    "glm",
    "psyfun",
    "params",
    "recov",
)

OPTIONAL_FIG_GROUPS = (
    "xpatt_coh",
    "hmeta",
    "chosen_contrib",
)

ALL_FIG_GROUPS = FIG_GROUPS + OPTIONAL_FIG_GROUPS


def run_figures(repo: Path, dpi: int, only: Sequence[str] | None) -> List[Path]:
    """Run selected figure generators; `only` None or [] means all core groups."""
    if only is None or len(only) == 0:
        want = set(FIG_GROUPS)
    else:
        want = set(x.lower() for x in only)
    if "all" in want:
        want = set(ALL_FIG_GROUPS)
    if "core" in want:
        want = (want - {"core"}) | set(FIG_GROUPS)

    unknown = want - set(ALL_FIG_GROUPS)
    if unknown:
        raise SystemExit(
            f"Unknown --only names: {sorted(unknown)}. "
            f"Valid: all, core, {', '.join(ALL_FIG_GROUPS)}"
        )

    outs: List[Path] = []
    if "model_avg" in want:
        outs.append(plot_model_avg_figure(repo, dpi=dpi))
    if "xpatt" in want:
        outs.append(plot_xpatt_by_experiment(repo, dpi=dpi))
        outs.append(plot_xpatt_data_vs_models(repo, dpi=dpi))
        outs.append(plot_xpatt_empirical_overlay_models(repo, dpi=dpi))
    if "xpatt_coh" in want:
        # Imported lazily: requires plotting/optional/, unlike every other group.
        from motivbelief.plotting.optional.fig_xpatt_coh import (
            plot_xpatt_coh_by_experiment,
            plot_xpatt_coh_data_vs_models,
            plot_xpatt_coh_empirical_overlay_models,
        )

        outs.append(plot_xpatt_coh_by_experiment(repo, dpi=dpi))
        outs.append(plot_xpatt_coh_data_vs_models(repo, dpi=dpi))
        outs.append(plot_xpatt_coh_empirical_overlay_models(repo, dpi=dpi))
    if "calib" in want:
        outs.append(plot_calib_by_experiment(repo, dpi=dpi))
        outs.append(plot_calib_data_vs_models(repo, dpi=dpi))
    if "falsif_xpatt" in want:
        outs.append(plot_falsif_xpatt_figure(repo, dpi=dpi))
    if "hmeta" in want:
        outs.extend(plot_hmeta_figures(repo, dpi=dpi))
    if "behav" in want:
        outs.extend(plot_behav_figure(repo, dpi=dpi))
    if "glm" in want:
        outs.extend(plot_glm_figure(repo, dpi=dpi))
    if "psyfun" in want:
        outs.append(plot_psychometric_incentive_figure(repo, dpi=dpi))
    if "params" in want:
        outs.append(plot_params_figure(repo, dpi=dpi))
        outs.append(plot_free_bmc_figure(repo, dpi=dpi))
    if "recov" in want:
        outs.extend(plot_recov_figures(repo, dpi=dpi))
    if "chosen_contrib" in want:
        outs.append(plot_chosen_contribution_figure(repo, dpi=dpi))
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
            "Which figure groups to build (default: core paper set). "
            f"Core: {', '.join(FIG_GROUPS)}. "
            f"Optional: {', '.join(OPTIONAL_FIG_GROUPS)}. "
            "Also: all, core. Example: --only behav glm"
        ),
    )
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    outs = run_figures(repo, args.dpi, args.only)
    for p in outs:
        print(p)


if __name__ == "__main__":
    main()
