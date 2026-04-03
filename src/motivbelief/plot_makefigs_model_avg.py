"""
2×4 figure: participant-average accuracy and belief (confidence) for merged human data
and three simulation stems. Matches scripts_figures/do_figsModelAvg_2026_02_20.m layout.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from motivbelief.plot_makefigs_paths import fig_dir

CMAP = 0.7 * np.array([[1.0, 0.0, 0.0], [0.5, 0.5, 0.5], [0.0, 1.0, 0.0]])
INC_LEVELS = np.array([-1.0, 0.0, 1.0])
XTICKS = np.arange(1, 4)
XLABELS = ["Loss", "Neutral", "Gain"]


def _norm_inc(x: float) -> float:
    return float(np.round(float(x), 6))


def _aligned_series(sub: pd.DataFrame, ymean: str, ysem: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Values at INC_LEVELS (-1,0,1); NaN if missing."""
    sub = sub.copy()
    sub["incentive"] = sub["incentive"].map(_norm_inc)
    m = {row.incentive: row for _, row in sub.iterrows()}
    y, se = [], []
    for inc in INC_LEVELS:
        if inc in m:
            y.append(float(m[inc][ymean]))
            se.append(float(m[inc][ysem]))
        else:
            y.append(np.nan)
            se.append(np.nan)
    x = XTICKS.astype(float)
    return x, np.array(y, dtype=float), np.array(se, dtype=float)


def _plot_one_profile(
    ax: plt.Axes,
    df: pd.DataFrame,
    ymean: str,
    ysem: str,
    ylim: Tuple[float, float],
    ylabel: str,
    title: Optional[str],
    *,
    marker: str = "o",
    alpha: float = 1.0,
    zorder_data: int = 2,
) -> None:
    """Two trajectories: agency 0 (Non-Free) open markers; agency 1 (Free) filled."""
    for agency in (0, 1):
        sub = df[df["agency"] == agency]
        if sub.empty:
            continue
        x, yvals, se = _aligned_series(sub, ymean, ysem)
        good = np.isfinite(yvals) & np.isfinite(se)
        if not np.any(good):
            continue

        if agency == 0:
            c_edge = np.array([CMAP[i] for i in range(3)])
            c_face = np.ones((3, 3))
        else:
            c_face = np.array([CMAP[i] for i in range(3)])
            c_edge = np.zeros((3, 3))

        ax.plot(x[good], yvals[good], "-k", alpha=alpha, zorder=zorder_data - 1)
        for i in range(3):
            if not good[i]:
                continue
            ax.errorbar(
                x[i],
                yvals[i],
                yerr=se[i],
                fmt=marker,
                color=c_edge[i],
                markerfacecolor=c_face[i],
                markeredgecolor=c_edge[i],
                ecolor=c_edge[i],
                capsize=0,
                linestyle="none",
                alpha=alpha,
                zorder=zorder_data,
            )

    ax.set_xlim(0.5, 3.5)
    ax.set_xticks(XTICKS)
    ax.set_xticklabels(XLABELS)
    ax.set_ylim(ylim)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.grid(True, alpha=0.25, linestyle=":")


def _load_avg(repo: Path, stem: str) -> pd.DataFrame:
    p = repo / "results" / "stats" / "average" / stem / f"sample_avg_{stem}.csv"
    if not p.is_file():
        alt = repo / "results" / "stats_py" / "average" / stem / f"sample_avg_{stem}.csv"
        p = alt if alt.is_file() else p
    return pd.read_csv(p)


def plot_model_avg_figure(
    repo_root: Path,
    out_path: Optional[Path] = None,
    *,
    dpi: int = 150,
) -> Path:
    """
    Single 2×4 figure: row 0 = accuracy, row 1 = belief (confidence).
    Columns: merged data, sim_act, sim_intent, sim_confirm.
    On intent/confirm accuracy panels, plot only sim_act accuracy at reduced alpha (no intent/confirm accuracy).
    """
    repo_root = repo_root.resolve()
    stems = [
        ("exp1a_exp2free_exp3", "Data"),
        ("sim_act", "Sim act"),
        ("sim_intent", "Sim intent"),
        ("sim_confirm", "Sim confirm"),
    ]
    dfs = {s: _load_avg(repo_root, s) for s, _ in stems}
    df_act = dfs["sim_act"]

    fig, axes = plt.subplots(2, 4, figsize=(14, 6), constrained_layout=True)

    for col, (stem, ttl) in enumerate(stems):
        df = dfs[stem]
        # Accuracy
        ax0 = axes[0, col]
        if stem in ("sim_intent", "sim_confirm"):
            _plot_one_profile(
                ax0,
                df_act,
                "correct_mean",
                "correct_sem",
                (50, 90),
                "Choice accuracy",
                ttl,
                marker="o",
                alpha=0.5,
                zorder_data=2,
            )
        else:
            _plot_one_profile(
                ax0,
                df,
                "correct_mean",
                "correct_sem",
                (50, 90),
                "Choice accuracy",
                ttl,
                marker="o",
                alpha=1.0,
                zorder_data=2,
            )
        # Belief (confidence)
        _plot_one_profile(
            axes[1, col],
            df,
            "conf_mean",
            "conf_sem",
            (50, 90),
            "Belief",
            ttl,
            marker="d",
            alpha=1.0,
        )

    out = out_path or (fig_dir(repo_root) / "plots_model_avg.png")
    fig.savefig(out, dpi=dpi)
    svg = out.with_suffix(".svg")
    fig.savefig(svg)
    plt.close(fig)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="2×4 model-average accuracy + belief figure.")
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()
    p = plot_model_avg_figure(args.repo_root, out_path=args.out, dpi=args.dpi)
    print(p)


if __name__ == "__main__":
    main()
