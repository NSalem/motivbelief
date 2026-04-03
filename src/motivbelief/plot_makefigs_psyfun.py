"""
Choice psychometric fits (by incentive): 3×4 panels + slope violins.
Port of scripts_figures/do_figs_psyfun.m (incentive figure).
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde, norm

from motivbelief.plot_makefigs_paths import fig_dir

RNG = np.random.default_rng(2026)

INC_CMAP = 0.7 * np.array([[1, 0, 0], [0.5, 0.5, 0.5], [0, 0.5, 0], [0, 1, 0]], dtype=float)

TOP_PAIRS = [("exp1a", "Free"), ("exp1b", "Free"), ("exp2", "Free"), ("exp3", "Replayed")]
BOTTOM_PAIRS = [("exp1a", "Observed"), ("exp1b", "Observed"), ("exp2", "Observed"), ("exp3", "Forced")]


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


def compute_summary_incentive(
    iexp: str,
    igroup: str,
    data_dir: Path,
    results_dir: Path,
    n_grid: int = 401,
) -> Dict[str, Any]:
    df = preprocess_df(pd.read_csv(data_dir / f"data_{iexp}.csv"))
    df["participant"] = df["participant"].astype(str)
    inc_col = _inc_col_name(df)
    in_group = df["choiceType"].astype(str) == igroup
    subjects = df.loc[in_group, "participant"].unique()
    fits = pd.read_csv(results_dir / f"pars_choice_{iexp}_{igroup}_byIncentive.csv")
    fits["participant"] = fits["participant"].astype(str)
    fits = fits[fits["participant"].isin(subjects)].copy()
    inc_levels = np.sort(fits["incentive"].unique())

    stim = df.loc[in_group, "stim"].astype(float)
    stim_grid = np.linspace(float(stim.min()), float(stim.max()), n_grid)

    sub = df.loc[in_group, ["participant", "stim", inc_col, "y_right"]].copy()
    sub = sub.rename(columns={inc_col: "incentive"})
    g1 = (
        sub.groupby(["participant", "stim", "incentive"], as_index=False)["y_right"]
        .mean()
        .rename(columns={"y_right": "y_right_mean"})
    )

    def _sem(x: pd.Series) -> float:
        x = x.dropna()
        return float(x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0

    g2 = g1.groupby(["stim", "incentive"], as_index=False).agg(
        mean=("y_right_mean", "mean"), sem=("y_right_mean", _sem)
    )
    group_emp_inc = g2

    curves_mean = np.full((len(inc_levels), n_grid), np.nan)
    for ii, inc in enumerate(inc_levels):
        fsub = fits[np.isclose(fits["incentive"].astype(float), float(inc))]
        if fsub.empty:
            continue
        tmp = []
        for _, r in fsub.iterrows():
            p = psychofun_local(
                float(r["choice_bias"]),
                float(r["sigma_act"]),
                float(r["p_lapse"]),
                stim_grid,
            )
            tmp.append(p)
        curves_mean[ii, :] = np.nanmean(np.asarray(tmp), axis=0)

    sigma_by_inc = fits[["participant", "incentive", "sigma_act"]].copy()

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


def _kde_violin_simple(
    ax: plt.Axes, data: np.ndarray, x_pos: float, color: np.ndarray, width: float = 0.4
) -> None:
    data = np.asarray(data, dtype=float)
    data = data[np.isfinite(data)]
    if data.size < 2:
        return
    kde = gaussian_kde(data)
    y = np.linspace(data.min(), data.max(), 80)
    d = kde(y)
    d = d / (d.max() + 1e-12) * width
    ax.fill_betweenx(y, x_pos - d, x_pos + d, facecolor=color, alpha=0.35, edgecolor=(0.3, 0.3, 0.3), linewidth=0.6)


def plot_psychometric_incentive_figure(
    repo_root: Path,
    *,
    out_path: Optional[Path] = None,
    dpi: int = 150,
) -> Path:
    repo_root = repo_root.resolve()
    data_dir = repo_root / "data"
    results_dir = repo_root / "results" / "fits_choice"
    out_dir = fig_dir(repo_root)

    top_summ = [compute_summary_incentive(e, g, data_dir, results_dir) for e, g in TOP_PAIRS]
    bot_summ = [compute_summary_incentive(e, g, data_dir, results_dir) for e, g in BOTTOM_PAIRS]

    all_slope = []
    for S in top_summ:
        sig = S["sigma_by_inc"]["sigma_act"].to_numpy(dtype=float)
        sl = 1.0 / sig
        sl = sl[np.isfinite(sl) & (sl > 0)]
        all_slope.extend(sl.tolist())
    if all_slope:
        slope_ylim = float(np.min(all_slope)), float(np.max(all_slope))
        slope_ylim = (max(0, slope_ylim[0]), slope_ylim[1] + 1e-6 if slope_ylim[1] <= slope_ylim[0] else slope_ylim[1])
    else:
        slope_ylim = (0.0, 1.0)

    fig, axes = plt.subplots(3, 4, figsize=(14, 10), constrained_layout=True)
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
                capsize=6,
                linewidth=1.2,
                markerfacecolor=col,
                markeredgecolor="white",
            )
        ax.axvline(0, color="k", linestyle="--", alpha=0.4)
        ax.axhline(0.5, color="k", linestyle="--", alpha=0.4)
        ax.set_title(f'{S["exp"]}\n{S["group"]}')
        ax.set_ylim(-0.02, 1.02)
        ax.set_xticks([])
        ax.set_yticks([])
        if j == 0:
            ax.set_yticks([0, 0.5, 1])
            ax.set_ylabel("p(right)")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

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
                capsize=6,
                linewidth=1.2,
                markerfacecolor="white",
                markeredgecolor=col,
            )
            ax.plot(Gi["stim"], Gi["mean"], "-", color=col, linewidth=2)
        ax.axvline(0, color="k", linestyle="--", alpha=0.4)
        ax.axhline(0.5, color="k", linestyle="--", alpha=0.4)
        ax.set_title(f'{S["exp"]}\n{S["group"]}')
        ax.set_xlabel("Rightward\ncoherence (%)")
        ax.set_ylim(-0.02, 1.02)
        ax.set_xticks([])
        ax.set_yticks([])
        if j == 0:
            ax.set_yticks([0, 0.5, 1])
            ax.set_ylabel("p(right)")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    # Row 3: slope violins (top_summ only)
    for e, S in enumerate(top_summ):
        ax = axes[2, e]
        T = S["sigma_by_inc"].copy()
        inc_vals = T["incentive"].to_numpy(dtype=float)
        pid = T["participant"].to_numpy()
        sigma_vals = T["sigma_act"].to_numpy(dtype=float)
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
                _kde_violin_simple(ax, yk, xT[k], col, width=0.4)

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
        if e == 0:
            ax.set_ylabel("slope (1/σ)")
        ax.set_title("")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    outp = (out_path or (out_dir / "plots_choice_fits_inc.png")).resolve()
    outp.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outp, dpi=dpi)
    fig.savefig(outp.with_suffix(".svg"))
    plt.close(fig)
    return outp


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--out", type=Path, default=None, help="Output image path (.png/.svg base)")
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()
    print(plot_psychometric_incentive_figure(args.repo_root, out_path=args.out, dpi=args.dpi))


if __name__ == "__main__":
    main()
