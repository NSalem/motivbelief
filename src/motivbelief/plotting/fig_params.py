"""
Free-condition confidence-parameter violin plots from the pe_wt_v model
(bel_noise; pe_wt + pe_wt_v), split by experiment, with one-sample t-tests
vs zero on pe_wt / pe_wt_v.

Layout: 1 row × 3 columns, one column per parameter (bel_noise | pe_wt |
pe_wt_v). Each column shows three violins on the x-axis: exp1a, exp2, and
merged (pooled across experiments). The pe_wt and pe_wt_v columns share a
common y-axis scale; bel_noise has its own. Optional BMC via ``--bmc-out``
(``fig_bmc.plot_free_bmc_figure``).
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

from motivbelief.modeling.analysis_free import (
    FREE_EXPERIMENTS_VIOLIN,
    load_conf_fits,
    one_sample_ttests,
)
from motivbelief.plotting.artists import kde_violin
from motivbelief.plotting.fig_bmc import plot_free_bmc_figure
from motivbelief.plotting.paths import fig_dir
from motivbelief.plotting.style import save_fig

RNG = np.random.default_rng(42)

FIT_TAG = "pe_wt_v"

BEL_NOISE_SPEC = ("bel_noise", r"$\sigma_{\mathrm{bel}}$", (0.45, 0.45, 0.45))
PE_SPECS: Tuple[Tuple[str, str, Tuple[float, float, float]], ...] = (
    ("pe_wt", r"$\alpha_0$", (0.2, 0.45, 0.75)),
    ("pe_wt_v", r"$\alpha_v$", (0.85, 0.45, 0.15)),
)
TTEST_PARAMS = ("pe_wt", "pe_wt_v")

# One entry per x-position within each parameter column: (ttest scope key,
# x-tick label, experiments pooled for that violin).
EXPERIMENT_GROUPS: Tuple[Tuple[str, str, Tuple[str, ...]], ...] = (
    ("exp1a", "Exp1a", ("exp1a",)),
    ("exp2", "Exp2", ("exp2",)),
    ("pooled", "Merged", FREE_EXPERIMENTS_VIOLIN),
)


def _param_values(
    data: pd.DataFrame, param: str, experiments: Tuple[str, ...] = FREE_EXPERIMENTS_VIOLIN
) -> np.ndarray:
    sub = data.loc[
        data["experiment"].isin(experiments) & (data["fit_tag"] == FIT_TAG),
        param,
    ]
    vals = sub.dropna().to_numpy(dtype=float)
    return vals[np.isfinite(vals)]


def _p_to_stars(p: float) -> str:
    if not np.isfinite(p):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return ""


def save_conf_param_ttests(data: pd.DataFrame, out_path: Path) -> pd.DataFrame:
    """One-sample t-tests (+ Wilcoxon) vs 0 for pe_wt / pe_wt_v (pe_wt_v Free model)."""
    free_wv = data.loc[
        (data["fit_tag"] == FIT_TAG) & data["experiment"].isin(FREE_EXPERIMENTS_VIOLIN)
    ]
    tt = one_sample_ttests(free_wv, parameters=TTEST_PARAMS, model_labels=["Free"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tt.to_csv(out_path, index=False)
    return tt


def _local_violin_halfwidth(vals: np.ndarray, width: float) -> np.ndarray:
    """Half-width of the KDE violin at each point in ``vals`` (mirrors ``kde_violin``)."""
    n = vals.size
    if n == 0:
        return np.zeros(0)
    if n == 1:
        return np.full(1, width)
    lo, hi = float(np.min(vals)), float(np.max(vals))
    if lo == hi:
        return np.full(n, width)
    kde = gaussian_kde(vals)
    d_max = float(np.max(kde(np.linspace(lo, hi, 80))))
    d_max = d_max if d_max > 0 else 1.0
    return kde(vals) / d_max * width


def _draw_single_violin(
    ax: plt.Axes,
    vals: np.ndarray,
    x: float,
    color: Tuple[float, float, float],
    *,
    width: float = 0.3,
    jitter_frac: float = 0.5,
) -> None:
    if vals.size == 0:
        return
    kde_violin(ax, vals, x, color, width=width, alpha=0.35)
    halfwidths = _local_violin_halfwidth(vals, width)
    jitter = jitter_frac * halfwidths * (RNG.random(vals.size) * 2.0 - 1.0)
    ax.plot(
        x + jitter,
        vals,
        "o",
        markerfacecolor=color,
        markeredgecolor="white",
        markersize=3,
        linestyle="None",
        zorder=3,
        alpha=0.85,
    )
    mu = float(np.mean(vals))
    se = float(np.std(vals, ddof=1) / np.sqrt(vals.size)) if vals.size > 1 else 0.0
    ax.errorbar(x, mu, yerr=se, fmt="none", ecolor="k", linewidth=2.5, capsize=5, zorder=4)


def _ylim_from_vals(all_vals: Iterable[float], *, pad_frac: float = 0.08) -> Tuple[float, float]:
    vals = [float(v) for v in all_vals if np.isfinite(v)]
    if not vals:
        return (-1.0, 1.0)
    lo, hi = min(vals), max(vals)
    pad = pad_frac * (hi - lo) if hi > lo else 0.5
    return lo - pad, hi + pad


def _style_compact_ax(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=10)

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    xticks = ax.get_xticks()
    yticks = ax.get_yticks()
    xticks = xticks[(xticks >= xlim[0] - 1e-9) & (xticks <= xlim[1] + 1e-9)]
    yticks = yticks[(yticks >= ylim[0] - 1e-9) & (yticks <= ylim[1] + 1e-9)]
    if xticks.size:
        ax.spines["bottom"].set_bounds(float(xticks[0]), float(xticks[-1]))
    if yticks.size:
        ax.spines["left"].set_bounds(float(yticks[0]), float(yticks[-1]))


def _plot_param_column(
    ax: plt.Axes,
    data: pd.DataFrame,
    ttests: pd.DataFrame,
    spec: Tuple[str, str, Tuple[float, float, float]],
    *,
    ylim: Tuple[float, float],
    show_ttest: bool,
) -> None:
    """One parameter per column; violins at exp1a / exp2 / merged along x."""
    param, label, color = spec
    x_pos = np.arange(1, len(EXPERIMENT_GROUPS) + 1, dtype=float)
    annotations: List[Tuple[float, float, str]] = []

    for i, (scope_key, _xlabel, experiments) in enumerate(EXPERIMENT_GROUPS):
        vals = _param_values(data, param, experiments)
        x = float(x_pos[i])
        _draw_single_violin(ax, vals, x, color)
        if show_ttest and vals.size:
            row = ttests.loc[
                (ttests["scope"] == f"{scope_key} | Free") & (ttests["parameter"] == param)
            ]
            if not row.empty:
                stars = _p_to_stars(float(row.iloc[0]["t_p"]))
                if stars:
                    annotations.append((x, float(np.max(vals)), stars))

    if show_ttest:
        ax.axhline(0.0, color="k", linestyle="--", linewidth=1, alpha=0.6, zorder=1)
    ax.set_xlim(0.5, len(EXPERIMENT_GROUPS) + 0.5)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([g[1] for g in EXPERIMENT_GROUPS], fontsize=11,rotation=45)
    ax.set_ylabel(label, fontsize=16)
    ax.set_ylim(*ylim)
    _style_compact_ax(ax)

    lo, hi = ylim
    span = hi - lo if hi > lo else 1.0
    for x, local_max, stars in annotations:
        y = min(hi - 0.02 * span, local_max + 0.04 * span)
        ax.text(x, y, stars, ha="center", va="bottom", fontsize=10, fontweight="bold")


def plot_params_figure(
    repo_root: Path,
    out_path: Optional[Path] = None,
    *,
    dpi: int = 150,
) -> Path:
    repo_root = repo_root.resolve()
    data = load_conf_fits(repo_root / "results" / "modeling" / "fits_conf")
    ttests = save_conf_param_ttests(
        data, repo_root / "results" / "modeling" / "fits_conf" / "ttests_vs_zero.csv"
    )

    bel_vals = _param_values(data, "bel_noise").tolist()
    bel_ylim = _ylim_from_vals(bel_vals)
    if bel_vals and min(bel_vals) >= 0:
        bel_ylim = (-0.05 * (max(bel_vals) + 1e-6), bel_ylim[1])

    pe_vals: List[float] = []
    for param, _label, _color in PE_SPECS:
        pe_vals.extend(_param_values(data, param).tolist())
    pe_ylim = _ylim_from_vals(pe_vals)
    pe_span = pe_ylim[1] - pe_ylim[0]
    pe_ylim = (pe_ylim[0], pe_ylim[1] + 0.08 * pe_span)

    fig, axes = plt.subplots(
        1,
        3,
        figsize=(6, 3),
        constrained_layout=True,
    )
    fig.patch.set_facecolor("white")

    _plot_param_column(axes[0], data, ttests, BEL_NOISE_SPEC, ylim=bel_ylim, show_ttest=False)
    _plot_param_column(axes[1], data, ttests, PE_SPECS[0], ylim=pe_ylim, show_ttest=True)
    _plot_param_column(axes[2], data, ttests, PE_SPECS[1], ylim=pe_ylim, show_ttest=True)

    out = out_path or (fig_dir(repo_root) / "plots_params_free.png")
    return save_fig(fig, out, dpi=dpi, facecolor="white")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Free confidence-parameter violin figure + Free BMC bar chart."
    )
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--out", type=Path, default=None, help="Violin figure path")
    ap.add_argument("--bmc-out", type=Path, default=None, help="BMC bar chart path")
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument(
        "--skip-bmc",
        action="store_true",
        help="Only make the parameter violin figure (skip BMC bar chart).",
    )
    args = ap.parse_args()
    print(plot_params_figure(args.repo_root, out_path=args.out, dpi=args.dpi))
    if not args.skip_bmc:
        print(plot_free_bmc_figure(args.repo_root, out_path=args.bmc_out, dpi=args.dpi))


if __name__ == "__main__":
    main()
