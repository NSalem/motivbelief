"""
Choice psychometric fits (by incentive): 3×4 panels + slope violins.

Top row: Free/Replayed — fitted curves + empirical points.
Bottom row: Observed/Forced — empirical points only (no choice fits).
Row 3: slope (1/σ) violins from Free/Replayed by-incentive fits.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from scipy.stats import norm

from motivbelief.plotting.artists import kde_violin
from motivbelief.plotting.paths import fig_dir
from motivbelief.plotting.style import save_fig

RNG = np.random.default_rng(2026)

INC_CMAP = 0.7 * np.array([[1, 0, 0], [0.5, 0.5, 0.5], [0, 0.5, 0], [0, 1, 0]], dtype=float)

TOP_PAIRS = [("exp1a", "Free"), ("exp1b", "Free"), ("exp2", "Free"), ("exp3", "Replayed")]
BOTTOM_PAIRS = [("exp1a", "Observed"), ("exp1b", "Observed"), ("exp2", "Observed"), ("exp3", "Forced")]

# ~30% above matplotlib's default 10pt
FONT_SIZE = 13.0
MARKER_EDGE_WIDTH = 1.5  # default 1.0 + 1

# MATLAB: figure('Position',[200 200 1200 900]); tiledlayout(3,4,'TileSpacing','compact','Padding','compact')
# Same px→inches convention as fig_xpatt / fig_falsif (Position/100).
FIGSIZE = (12.0, 9.0)
# Approximate tiledlayout compact: nearly-square panels, small gaps, room for 2-line titles.
_SUBPLOT = dict(left=0.06, right=0.995, bottom=0.05, top=0.94, wspace=0.13, hspace=0.17)


def _setup_fonts() -> None:
    """Use Arial when available; else bundled Liberation Sans (same metrics as Arial)."""
    font_dir = Path(__file__).resolve().parent / "fonts"
    for ttf in ("LiberationSans-Regular.ttf", "LiberationSans-Bold.ttf"):
        path = font_dir / ttf
        if path.is_file():
            font_manager.fontManager.addfont(str(path))
    has_arial = any(getattr(f, "name", None) == "Arial" for f in font_manager.fontManager.ttflist)
    primary = "Arial" if has_arial else "Liberation Sans"
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [primary, "Helvetica", "DejaVu Sans"],
            "font.size": FONT_SIZE,
            "axes.titlesize": FONT_SIZE,
            "axes.labelsize": FONT_SIZE,
            "xtick.labelsize": FONT_SIZE,
            "ytick.labelsize": FONT_SIZE,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def preprocess_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.loc[df["conf"].notna()].copy()
    df["respRight"] = df["resp"].astype(str).str.lower() == "right"
    side = df["dir"].astype(str).str.lower()
    side_num = np.where(side == "right", 1.0, np.where(side == "left", -1.0, np.nan))
    df["stim"] = df["coh"].astype(float) * side_num
    df["y_right"] = df["respRight"].astype(float)
    return df


def psychofun_local(bias: float, sigma: float, lapse: float, x: np.ndarray) -> np.ndarray:
    z = (x + bias) / max(sigma, 1e-12)
    p0 = norm.cdf(z)
    return lapse * 0.5 + (1 - lapse) * p0


def inc_color(inc: float, inc_cmap: np.ndarray = INC_CMAP) -> np.ndarray:
    tol = 1e-9
    if abs(inc - (-1)) < tol:
        return inc_cmap[0]
    if abs(inc - 0) < tol:
        return inc_cmap[1]
    if abs(inc - 0.1) < 1e-6:
        return inc_cmap[2]
    if abs(inc - 1) < tol:
        return inc_cmap[3]
    return inc_cmap[3] if inc > 0 else inc_cmap[0]


def _inc_col_name(df: pd.DataFrame) -> str:
    for c in ("incentive", "incentive_abs", "inc", "stake", "reward"):
        if c in df.columns:
            return c
    raise ValueError("No incentive column in data")


def _load_by_incentive_fits(results_dir: Path, iexp: str, igroup: str) -> pd.DataFrame:
    """Load per-incentive choice fits (Free/Replayed only)."""
    canonical = results_dir / iexp / f"results_{igroup}_by_incentive.csv"
    if canonical.is_file():
        return pd.read_csv(canonical)

    raise FileNotFoundError(
        f"Missing by-incentive choice fits for {iexp}/{igroup}. "
        f"Expected {canonical}. Re-run scripts/fit_choice_model.py (Free/Replayed)."
    )


def _empirical_by_incentive(
    df: pd.DataFrame, igroup: str, inc_col: str
) -> Tuple[np.ndarray, pd.DataFrame]:
    """Incentive levels + group mean±SEM p(right) by stim×incentive (empirical only)."""
    in_group = df["choiceType"].astype(str) == igroup
    sub = df.loc[in_group, ["participant", "stim", inc_col, "y_right"]].copy()
    sub = sub.rename(columns={inc_col: "incentive"})
    if sub.empty:
        raise ValueError(f"No trials for choiceType={igroup}")

    g1 = (
        sub.groupby(["participant", "stim", "incentive"], as_index=False)["y_right"]
        .mean()
        .rename(columns={"y_right": "y_right_mean"})
    )

    def _sem(x: pd.Series) -> float:
        x = x.dropna()
        return float(x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0

    group_emp_inc = g1.groupby(["stim", "incentive"], as_index=False).agg(
        mean=("y_right_mean", "mean"), sem=("y_right_mean", _sem)
    )
    inc_levels = np.sort(sub["incentive"].astype(float).unique())
    return inc_levels, group_emp_inc


def compute_empirical_incentive(
    iexp: str,
    igroup: str,
    data_dir: Path,
) -> Dict[str, Any]:
    """Empirical psychometric summary (no choice fits). Used for Observed/Forced."""
    df = preprocess_df(pd.read_csv(data_dir / f"data_{iexp}.csv"))
    df["participant"] = df["participant"].astype(str)
    inc_col = _inc_col_name(df)
    inc_levels, group_emp_inc = _empirical_by_incentive(df, igroup, inc_col)
    return {
        "exp": iexp,
        "group": igroup,
        "inc_levels": inc_levels,
        "group_emp_inc": group_emp_inc,
    }


def compute_summary_incentive(
    iexp: str,
    igroup: str,
    data_dir: Path,
    results_dir: Path,
    n_grid: int = 401,
) -> Dict[str, Any]:
    """Empirical + mean fitted curves + per-incentive σ (Free/Replayed)."""
    df = preprocess_df(pd.read_csv(data_dir / f"data_{iexp}.csv"))
    df["participant"] = df["participant"].astype(str)
    inc_col = _inc_col_name(df)
    in_group = df["choiceType"].astype(str) == igroup
    subjects = df.loc[in_group, "participant"].unique()
    fits = _load_by_incentive_fits(results_dir, iexp, igroup)
    fits["participant"] = fits["participant"].astype(str)
    fits = fits[fits["participant"].isin(subjects)].copy()
    if fits.empty:
        raise ValueError(f"No by-incentive fits for subjects in {iexp}/{igroup}")

    stim = df.loc[in_group, "stim"].astype(float)
    stim_grid = np.linspace(float(stim.min()), float(stim.max()), n_grid)
    _, group_emp_inc = _empirical_by_incentive(df, igroup, inc_col)
    # Prefer fit incentive levels so curve indexing matches fitted params.
    inc_levels = np.sort(fits["incentive"].unique())

    curves_mean = np.full((len(inc_levels), n_grid), np.nan)
    for ii, inc in enumerate(inc_levels):
        fsub = fits[np.isclose(fits["incentive"].astype(float), float(inc))]
        if fsub.empty:
            continue
        tmp = []
        for _, r in fsub.iterrows():
            p = psychofun_local(
                float(r["sens_bias"]),
                float(r["sens_noise"]),
                float(r["p_lapse"]),
                stim_grid,
            )
            tmp.append(p)
        curves_mean[ii, :] = np.nanmean(np.asarray(tmp), axis=0)

    sigma_by_inc = fits[["participant", "incentive", "sens_noise"]].copy()

    return {
        "exp": iexp,
        "group": igroup,
        "df": df,
        "inc_levels": inc_levels,
        "stim_grid": stim_grid,
        "curves_mean": curves_mean,
        "group_emp_inc": group_emp_inc,
        "sigma_by_inc": sigma_by_inc,
    }


def plot_psychometric_incentive_figure(
    repo_root: Path,
    *,
    out_path: Optional[Path] = None,
    dpi: int = 150,
) -> Path:
    repo_root = repo_root.resolve()
    data_dir = repo_root / "data"
    results_dir = repo_root / "results" / "modeling" / "fits_choice"
    out_dir = fig_dir(repo_root)

    _setup_fonts()

    top_summ = [compute_summary_incentive(e, g, data_dir, results_dir) for e, g in TOP_PAIRS]
    bot_summ = [compute_empirical_incentive(e, g, data_dir) for e, g in BOTTOM_PAIRS]

    slope_ylim = (0.0, 2.0)
    slope_yticks = np.arange(0.0, 2.0 + 1e-9, 0.5)

    fig, axes = plt.subplots(3, 4, figsize=FIGSIZE, facecolor="white", constrained_layout=False)
    fig.subplots_adjust(**_SUBPLOT)
    # Row 1
    for j, S in enumerate(top_summ):
        ax = axes[0, j]
        stim_grid = S["stim_grid"]
        G = S["group_emp_inc"]
        for ii, inc in enumerate(S["inc_levels"]):
            col = inc_color(float(inc), INC_CMAP)
            y = S["curves_mean"][ii]
            if np.all(~np.isfinite(y)):
                continue
            ax.plot(stim_grid, y, color=col, linewidth=3)
            Gi = G[np.isclose(G["incentive"].astype(float), float(inc))]
            if Gi.empty:
                continue
            Gi = Gi.sort_values("stim")
            ax.errorbar(
                Gi["stim"],
                Gi["mean"],
                yerr=1.96 * Gi["sem"],
                fmt="o",
                color=col,
                markersize=6,
                capsize=3,
                linewidth=1.2,
                markerfacecolor=col,
                markeredgecolor="white",
                markeredgewidth=MARKER_EDGE_WIDTH,
            )
        ax.axvline(0, color="k", linestyle="--", alpha=0.4)
        ax.axhline(0.5, color="k", linestyle="--", alpha=0.4)
        ax.set_title(f'{S["exp"]}\n{S["group"]}', pad=4)
        ax.set_ylim(-0.02, 1.02)
        ax.set_xticks([])
        ax.set_yticks([])
        if j == 0:
            ax.set_yticks([0, 0.5, 1])
            ax.set_ylabel("p(right)")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_bounds(0.0, 1.0)

    # Row 2
    for j, S in enumerate(bot_summ):
        ax = axes[1, j]
        G = S["group_emp_inc"]
        for ii, inc in enumerate(S["inc_levels"]):
            col = inc_color(float(inc), INC_CMAP)
            Gi = G[np.isclose(G["incentive"].astype(float), float(inc))]
            if Gi.empty:
                continue
            Gi = Gi.sort_values("stim")
            ax.errorbar(
                Gi["stim"],
                Gi["mean"],
                yerr=1.96 * Gi["sem"],
                fmt="o",
                color=col,
                markersize=6,
                capsize=3,
                linewidth=1.2,
                markerfacecolor="white",
                markeredgecolor=col,
                markeredgewidth=MARKER_EDGE_WIDTH,
            )
            ax.plot(Gi["stim"], Gi["mean"], "-", color=col, linewidth=2)
        ax.axvline(0, color="k", linestyle="--", alpha=0.4)
        ax.axhline(0.5, color="k", linestyle="--", alpha=0.4)
        ax.set_title(f'{S["exp"]}\n{S["group"]}', pad=4)
        ax.set_xlabel("Rightward coherence (%)")
        ax.set_ylim(-0.02, 1.02)
        ax.set_xticks([])
        ax.set_yticks([])
        if j == 0:
            ax.set_yticks([0, 0.5, 1])
            ax.set_ylabel("p(right)")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_bounds(0.0, 1.0)

    # Row 3: slope violins (top_summ only); share y across the row
    for e in range(1, 4):
        axes[2, e].sharey(axes[2, 0])

    for e, S in enumerate(top_summ):
        ax = axes[2, e]
        T = S["sigma_by_inc"].copy()
        inc_vals = T["incentive"].to_numpy(dtype=float)
        pid = T["participant"].to_numpy()
        sigma_vals = T["sens_noise"].to_numpy(dtype=float)
        slope_vals = 1.0 / sigma_vals
        inc_levels = np.sort(np.unique(inc_vals[~np.isnan(inc_vals)]))
        K = len(inc_levels)
        xT = np.arange(1, K + 1, dtype=float)
        sub_list = np.unique(pid)
        x_jitt = 0.30 * (RNG.random(len(sub_list)) - 0.5)

        for k in range(K):
            inc = inc_levels[k]
            col = inc_color(float(inc), INC_CMAP)
            yk = slope_vals[np.isclose(inc_vals, float(inc))]
            yk = yk[np.isfinite(yk)]
            if yk.size:
                kde_violin(ax, yk, xT[k], tuple(col), width=0.4, alpha=0.35)

        for sidx, sid in enumerate(sub_list):
            ys = np.full(K, np.nan)
            for k in range(K):
                m = (pid == sid) & np.isclose(inc_vals, float(inc_levels[k]))
                if np.any(m):
                    ys[k] = slope_vals[np.where(m)[0][0]]
            ok = np.isfinite(ys)
            if np.sum(ok) >= 2:
                ax.plot(xT[ok] + x_jitt[sidx], ys[ok], "-", color=(0.7, 0.7, 0.7, 0.25), linewidth=1)

        for sidx, sid in enumerate(sub_list):
            for k in range(K):
                inc_v = float(inc_levels[k])
                col = inc_color(inc_v, INC_CMAP)
                m = (pid == sid) & np.isclose(inc_vals, inc_v)
                if not np.any(m):
                    continue
                y = float(slope_vals[np.where(m)[0][0]])
                if not np.isfinite(y):
                    continue
                ax.plot(
                    xT[k] + x_jitt[sidx],
                    y,
                    "o",
                    markerfacecolor=col,
                    markeredgecolor="white",
                    markeredgewidth=MARKER_EDGE_WIDTH,
                    markersize=6,
                )

        inc_mu = np.full(K, np.nan)
        inc_se = np.full(K, np.nan)
        for k in range(K):
            inc_v = float(inc_levels[k])
            col = inc_color(inc_v, INC_CMAP)
            yk = slope_vals[np.isclose(inc_vals, inc_v)]
            yk = yk[np.isfinite(yk)]
            if yk.size:
                inc_mu[k] = float(np.mean(yk))
                inc_se[k] = float(np.std(yk, ddof=1) / np.sqrt(yk.size)) if yk.size > 1 else 0.0
                ax.errorbar(xT[k], inc_mu[k], yerr=inc_se[k], fmt="none", ecolor=col, linewidth=2, capsize=8)
        good = np.isfinite(inc_mu)
        if np.any(good):
            ax.plot(xT[good], inc_mu[good], "-k", linewidth=2)

        ax.set_xlim(0.5, K + 0.5)
        ax.set_xticks(xT)
        ax.set_xticklabels([str(float(v)) for v in inc_levels])
        ax.set_ylim(slope_ylim)
        ax.set_yticks(slope_yticks)
        if e == 0:
            ax.set_ylabel("slope (1/σ)")
        else:
            ax.tick_params(labelleft=False)
        ax.set_title("")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_bounds(float(xT[0]), float(xT[-1]))
        ax.spines["left"].set_bounds(float(slope_yticks[0]), float(slope_yticks[-1]))

    outp = (out_path or (out_dir / "plots_choice_fits_inc.png")).resolve()
    return save_fig(fig, outp, dpi=dpi)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--out", type=Path, default=None, help="Output image path (.png/.svg base)")
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()
    print(plot_psychometric_incentive_figure(args.repo_root, out_path=args.out, dpi=args.dpi))


if __name__ == "__main__":
    main()
