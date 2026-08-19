"""
2×4 figure: participant-average accuracy and belief (confidence) for merged
human data and three simulation stems.

Style matched to MATLAB ``do_figsModelAvg_2026_02_20.m``:
Position [400 400 350 150] → 3.5×1.5 in per 1×2; panel cell ≈ 1.75×1.5 in.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.ticker import MultipleLocator

from motivbelief.plotting.paths import fig_dir
from motivbelief.plotting.style import save_fig

CMAP = 0.7 * np.array([[1.0, 0.0, 0.0], [0.5, 0.5, 0.5], [0.0, 1.0, 0.0]])
INC_LEVELS = np.array([-1.0, 0.0, 1.0])
XTICKS = np.arange(1, 4)
XLABELS = ["Loss", "Neutral", "Gain"]

# MATLAB Position [400 400 350 150] → same panel cell as fig_xpatt.
_PANEL_W, _PANEL_H = 1.75, 1.5
FIGSIZE_2X4 = (4 * _PANEL_W, 2 * _PANEL_H)  # (7.0, 3.0)

# MATLAB errorbar / plot defaults (unset in the .m script).
MARKER_SIZE = 6.0
LINE_WIDTH = 0.5
MARKER_EDGE_WIDTH = 0.5
# Matplotlib capsize is half-width (center→end) in pt; MATLAB CapSize default = 6.
CAP_SIZE = 3.0
FONT_SIZE = 10.0
SPINE_LW = 0.5


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
            "axes.linewidth": SPINE_LW,
            "lines.linewidth": LINE_WIDTH,
            "lines.markersize": MARKER_SIZE,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


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


def _style_axes(ax: plt.Axes, *, ylim: Tuple[float, float], ylabel: str, title: Optional[str]) -> None:
    """Arial / thin spines; Box off (no top/right); bottom spine spans xticks only."""
    ax.set_xlim(0.5, 3.5)
    ax.set_xticks(XTICKS)
    ax.set_xticklabels(XLABELS)
    ax.set_ylim(ylim)
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.grid(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for side in ("bottom", "left"):
        ax.spines[side].set_visible(True)
        ax.spines[side].set_linewidth(SPINE_LW)
        ax.spines[side].set_color("k")
    ax.spines["bottom"].set_bounds(float(XTICKS[0]), float(XTICKS[-1]))
    ax.tick_params(axis="both", direction="in", labelsize=FONT_SIZE, width=SPINE_LW, length=3.5)
    ax.tick_params(axis="x", top=False)
    ax.tick_params(axis="y", right=False)
    ax.xaxis.label.set_fontsize(FONT_SIZE)
    ax.yaxis.label.set_fontsize(FONT_SIZE)
    if title:
        ax.title.set_fontsize(FONT_SIZE)


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

        ax.plot(
            x[good],
            yvals[good],
            "-k",
            linewidth=LINE_WIDTH,
            alpha=alpha,
            zorder=zorder_data - 1,
        )
        # Markers first, then errorbars on top (stems/caps visible through open markers).
        for i in range(3):
            if not good[i]:
                continue
            ax.plot(
                x[i],
                yvals[i],
                linestyle="none",
                marker=marker,
                color=c_edge[i],
                markerfacecolor=c_face[i],
                markeredgecolor=c_edge[i],
                markeredgewidth=MARKER_EDGE_WIDTH,
                markersize=MARKER_SIZE,
                alpha=alpha,
                zorder=zorder_data,
            )
            ax.errorbar(
                x[i],
                yvals[i],
                yerr=se[i],
                fmt="none",
                ecolor=c_edge[i],
                elinewidth=LINE_WIDTH,
                capsize=CAP_SIZE,
                alpha=alpha,
                zorder=zorder_data + 0.5,
            )

    _style_axes(ax, ylim=ylim, ylabel=ylabel, title=title)


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
    _setup_fonts()
    repo_root = repo_root.resolve()
    stems = [
        ("exp1a_exp2free_exp3", "behavior"),
        ("sim_act", "model Act"),
        ("sim_intent", "model Intent"),
        ("sim_confirm", "model Confirm"),
    ]
    dfs = {s: _load_avg(repo_root, s) for s, _ in stems}
    df_act = dfs["sim_act"]

    fig, axes = plt.subplots(2, 4, figsize=FIGSIZE_2X4, constrained_layout=True)
    fig.patch.set_facecolor("white")

    for col, (stem, ttl) in enumerate(stems):
        df = dfs[stem]
        title = ttl  # top row only; bottom mirrors MATLAB twin title via shared column
        # Accuracy
        ax0 = axes[0, col]
        if stem in ("sim_intent", "sim_confirm"):
            _plot_one_profile(
                ax0,
                df_act,
                "correct_mean",
                "correct_sem",
                (50, 90),
                "choice accuracy",
                title,
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
                "choice accuracy",
                title,
                marker="o",
                alpha=1.0,
                zorder_data=2,
            )
        # Belief (confidence) — MATLAB ylabel is "confidence"
        _plot_one_profile(
            axes[1, col],
            df,
            "conf_mean",
            "conf_sem",
            (50, 90),
            "confidence",
            None,
            marker="d",
            alpha=1.0,
        )

    out = out_path or (fig_dir(repo_root) / "plots_model_avg.png")
    return save_fig(fig, out, dpi=dpi, facecolor="white")


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
