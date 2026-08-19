"""
Figure 4A: chosen-option evidence contribution vs incentive, on match vs
mismatch trials, under the three congruence models (Action/Intention/
Confirmation). Holds the Free-fitted (pe_wt, pe_wt_v) at the
across-participant average and sweeps mismatch_coef analytically (a point
prediction from the average parameters, using conf_core's own weighting
formula: w = tanh(factor*(pe_wt + pe_wt_v*incentive)), chosen contribution
= 100*(1+w)/2, factor=1 on match trials, factor=mismatch_coef on mismatch
trials):

* Action (mismatch_coef=+1): factor is the same as match's, so the mismatch
  curve is identical to the match curve -- omitted from this panel.
* Intention (mismatch_coef=-1): factor flips sign relative to match's, so
  mismatch = 100 - match exactly.
* Confirmation (mismatch_coef=0): factor is 0, so the mismatch curve is flat
  at 50% regardless of incentive -- drawn in grey.

mismatch_coef only has an effect for Non-Free choices (see
:func:`motivbelief.modeling.conf_core.confidence_core`); on Free trials the
action is always the model's own covert choice.

Layout: 1 row x 3 square panels, one per congruence model.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from motivbelief.modeling.analysis_free import FREE_EXPERIMENTS_VIOLIN, load_conf_fits
from motivbelief.plotting.paths import fig_dir
from motivbelief.plotting.series_panel import Series, draw_lines
from motivbelief.plotting.style import save_fig

FIT_TAG = "pe_wt_v"

MATCH_COLOR = (0.0, 1, 0.0)
MISMATCH_COLOR = (1, 0.0, 0.0)
MISMATCH_COLOR_GREY = (0.6, 0.6, 0.6)

MISMATCH_COEFS: Tuple[float, ...] = (1.0, -1.0, 0.0)
PANEL_TITLES = {
    1.0: "act",
    -1.0: "int",
    0.0: "con",
}
# Panel 1 (mcm=1) omits the mismatch line (it's identical to match, see module
# docstring); panel 3 (mcm=0) draws it in grey instead of the default color.
PANEL_MISMATCH_COLOR = {-1.0: MISMATCH_COLOR, 0.0: MISMATCH_COLOR_GREY}

INC_GRID = np.linspace(-1.0, 1.0, 101)


def _pe_pairs(data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """Per-participant (pe_wt, pe_wt_v) from the Free pe_wt_v model, pooled
    across FREE_EXPERIMENTS_VIOLIN (same selection as fig_params.py)."""
    sub = data.loc[
        data["experiment"].isin(FREE_EXPERIMENTS_VIOLIN) & (data["fit_tag"] == FIT_TAG),
        ["pe_wt", "pe_wt_v"],
    ].dropna()
    return sub["pe_wt"].to_numpy(dtype=float), sub["pe_wt_v"].to_numpy(dtype=float)


def _avg_params(data: pd.DataFrame) -> Tuple[float, float]:
    """Across-participant average (pe_wt, pe_wt_v) from the Free pe_wt_v model."""
    pe_wt, pe_wt_v = _pe_pairs(data)
    return float(np.mean(pe_wt)), float(np.mean(pe_wt_v))


def _chosen_pct_curve(
    pe_wt: float, pe_wt_v: float, factor: float, inc_grid: np.ndarray
) -> np.ndarray:
    """100 * (1 + tanh(factor*(pe_wt + pe_wt_v*inc))) / 2, shape (n_grid,)."""
    arg = factor * (pe_wt + pe_wt_v * inc_grid)
    return 100.0 * (1.0 + np.tanh(arg)) / 2.0


def _style_panel(ax: plt.Axes, *, title: str, ylabel: Optional[str] = None) -> None:
    ax.axhline(50.0, color="k", linestyle=":", linewidth=0.8, alpha=0.5, zorder=1)
    ax.set_xlim(-1.0, 1.0)
    ax.set_ylim(25, 75)
    ax.set_xticks([-1.0, 0.0, 1.0])
    ax.set_yticks([25,50,75])
    ax.set_xlabel("Incentive",fontsize = 24)
    if ylabel:
        ax.set_ylabel(ylabel,fontsize=24)
    ax.set_title(title, fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=20)
    ax.set_box_aspect(1)


def plot_chosen_contribution_figure(
    repo_root: Path,
    out_path: Optional[Path] = None,
    *,
    dpi: int = 150,
) -> Path:
    repo_root = repo_root.resolve()
    data = load_conf_fits(repo_root / "results" / "modeling" / "fits_conf")
    pe_wt_avg, pe_wt_v_avg = _avg_params(data)

    match_curve = _chosen_pct_curve(pe_wt_avg, pe_wt_v_avg, 1.0, INC_GRID)

    fig, axes = plt.subplots(1, 3, figsize=(7.5, 3.0), constrained_layout=True)
    fig.patch.set_facecolor("white")

    for i, (ax, mcm) in enumerate(zip(axes, MISMATCH_COEFS)):
        series = [
            Series(
                INC_GRID,
                match_curve,
                color=MATCH_COLOR,
                linestyle="-",
                label=r"$c = a$",
                linewidth=3,
                zorder=2,
            ),
        ]
        if mcm in PANEL_MISMATCH_COLOR:
            mismatch_curve = _chosen_pct_curve(pe_wt_avg, pe_wt_v_avg, mcm, INC_GRID)
            series.append(
                Series(
                    INC_GRID,
                    mismatch_curve,
                    color=PANEL_MISMATCH_COLOR[mcm],
                    linestyle="-",
                    label=r"$c \neq a$",
                    linewidth=3,
                    zorder=3,
                )
            )
        draw_lines(ax, series, band=True)
        _style_panel(
            ax,
            title='',
            ylabel=r"$x_a$ contrib. (%)",
        )

    out = out_path or (fig_dir(repo_root) / "plots_chosen_contribution.png")
    return save_fig(fig, out, dpi=dpi, facecolor="white")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Chosen-option contribution (match vs mismatch) across 3 "
            "mismatch_coef hypotheses (+1 / -1 / 0)."
        )
    )
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()
    print(plot_chosen_contribution_figure(args.repo_root, out_path=args.out, dpi=args.dpi))


if __name__ == "__main__":
    main()
