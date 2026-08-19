"""
Xpatt (trial-level) figures: experiment comparison and data vs models.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager

from motivbelief.plotting.paths import fig_dir, stats_trial_root
from motivbelief.plotting.series_panel import Series, draw_lines, draw_points, style_belief_axis
from motivbelief.plotting.style import (
    CMAP_EXP1B,
    CMAP_INC_3,
    lookup_inc_idx,
    make_inc_map_flexible,
    open_filled_faces,
    save_fig,
)

DIFF_LEVELS = np.array([-0.5, 0.0, 0.5])
CMAP_DEFAULT = CMAP_INC_3

# MATLAB Position [400 400 350 150] → 3.5×1.5 in for 1×2; one panel cell ≈ 1.75×1.5.
_PANEL_W, _PANEL_H = 1.75, 1.5
FIGSIZE_2X4 = (4 * _PANEL_W, 2 * _PANEL_H)  # (7.0, 3.0)
FIGSIZE_2X3 = (3 * _PANEL_W, 2 * _PANEL_H)  # (5.25, 3.0)

# MATLAB errorbar / plot defaults (unset in the .m script).
MARKER_SIZE = 6.0
LINE_WIDTH = 0.5
MARKER_EDGE_WIDTH = 0.5
# Matplotlib capsize is half-width (center→end) in pt; full cap = marker diameter.
CAP_SIZE = MARKER_SIZE / 2.0
MARKER_ALPHA = 0.85
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


def _trial_dir(repo: Path, stem: str) -> Path:
    """Prefer `results/stats/trial`; fall back to `results/stats_py/trial` if CSV exists only there."""
    root = stats_trial_root(repo)
    p = root / stem
    f = p / f"sample_xpatt_{stem}.csv"
    if f.is_file():
        return p
    alt = repo / "results" / "stats_py" / "trial" / stem
    if (alt / f"sample_xpatt_{stem}.csv").is_file():
        return alt
    return p


def _read_xpatt_pair(repo: Path, stem: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    ddir = _trial_dir(repo, stem)
    f_data = ddir / f"sample_xpatt_{stem}.csv"
    f_pred = ddir / f"sub_pred_xpatt_{stem}.csv"
    if not f_data.is_file():
        raise FileNotFoundError(f_data)
    if not f_pred.is_file():
        raise FileNotFoundError(f_pred)
    tx = pd.read_csv(f_data)
    tsub = pd.read_csv(f_pred)
    tx["group"] = tx["group"].astype(str)
    tsub["group"] = tsub["group"].astype(str)
    return tx, tsub


def _sem(x: pd.Series) -> float:
    x = x.dropna()
    if len(x) < 2:
        return float("nan")
    return float(x.std(ddof=1) / np.sqrt(len(x)))


def aggregate_pred(tsub: pd.DataFrame) -> pd.DataFrame:
    g = tsub.groupby(["group", "difficulty", "incentive", "correct"], as_index=False)
    out = g.agg(pred_mean=("conf", "mean"), pred_sem=("conf", _sem))
    return out


def _point_series_kw() -> Dict[str, float]:
    return {
        "markersize": MARKER_SIZE,
        "markeredgewidth": MARKER_EDGE_WIDTH,
        "linewidth": LINE_WIDTH,
        "capsize": CAP_SIZE,
        "elinewidth": LINE_WIDTH,
        "alpha": MARKER_ALPHA,
    }


def _line_series_kw() -> Dict[str, float]:
    return {
        "markersize": MARKER_SIZE,
        "markeredgewidth": MARKER_EDGE_WIDTH,
        "linewidth": LINE_WIDTH,
        "capsize": CAP_SIZE,
        "elinewidth": LINE_WIDTH,
    }


def _xpatt_point_series(
    tx: pd.DataFrame,
    group: str,
    panel_k: int,
    cmap: np.ndarray,
    inc_to_idx: Dict[float, int],
    inc_levels: np.ndarray,
    corr_levels: np.ndarray,
    x_levels: np.ndarray = DIFF_LEVELS,
) -> List[Series]:
    c_fac, c_edg = open_filled_faces(panel_k, cmap)
    d0 = tx[tx["group"] == group]
    x_pos = np.arange(1, len(x_levels) + 1, dtype=float)
    out: List[Series] = []
    skw = _point_series_kw()

    for cval in corr_levels:
        dc = d0[np.isclose(d0["correct"].astype(float), float(cval))]
        for inc in inc_levels:
            cidx = lookup_inc_idx(inc_to_idx, float(inc))
            if cidx >= cmap.shape[0]:
                continue
            col = cmap[cidx]
            d_inc = dc[np.isclose(dc["incentive"].astype(float), float(inc))]
            if d_inc.empty:
                continue
            y = np.full(len(x_levels), np.nan)
            ys = np.full(len(x_levels), np.nan)
            for di, dlv in enumerate(x_levels):
                row = d_inc[np.isclose(d_inc["difficulty"].astype(float), float(dlv))]
                if not row.empty:
                    y[di] = float(row["conf_mean"].iloc[0])
                    ys[di] = float(row["conf_sem"].iloc[0])
            good = np.isfinite(y) & np.isfinite(ys)
            if np.any(good):
                out.append(
                    Series(
                        x_pos[good],
                        y[good],
                        yerr=ys[good],
                        color=col,
                        markerfacecolor=c_fac[cidx],
                        markeredgecolor=c_edg[cidx],
                        marker="o",
                        zorder=3,
                        **skw,
                    )
                )
    return out


def _xpatt_line_series(
    tp: pd.DataFrame,
    group: str,
    cmap: np.ndarray,
    inc_to_idx: Dict[float, int],
    inc_levels: np.ndarray,
    corr_levels: np.ndarray,
    x_levels: np.ndarray = DIFF_LEVELS,
) -> List[Series]:
    p0 = tp[tp["group"] == group]
    x_pos = np.arange(1, len(x_levels) + 1, dtype=float)
    out: List[Series] = []
    skw = _line_series_kw()

    for cval in corr_levels:
        linestyle = "--" if float(cval) < 0 else "-"
        pc = p0[np.isclose(p0["correct"].astype(float), float(cval))]
        for inc in inc_levels:
            cidx = lookup_inc_idx(inc_to_idx, float(inc))
            if cidx >= cmap.shape[0]:
                continue
            col = cmap[cidx]
            p_inc = pc[np.isclose(pc["incentive"].astype(float), float(inc))]
            if p_inc.empty:
                continue
            yline = np.full(len(x_levels), np.nan)
            ysem = np.full(len(x_levels), np.nan)
            for di, dlv in enumerate(x_levels):
                row = p_inc[np.isclose(p_inc["difficulty"].astype(float), float(dlv))]
                if not row.empty:
                    yline[di] = float(row["pred_mean"].iloc[0])
                    ysem[di] = float(row["pred_sem"].iloc[0])
            good = np.isfinite(yline) & np.isfinite(ysem)
            if np.sum(good) >= 2:
                out.append(
                    Series(
                        x_pos[good],
                        yline[good],
                        yerr=ysem[good],
                        color=col,
                        linestyle=linestyle,
                        zorder=2,
                        **skw,
                    )
                )
    return out


def _style_xpatt_axes(ax: plt.Axes, *, n_x: int, title: Optional[str]) -> None:
    """Arial / thin spines; Box off (no top/right); bottom spine spans xticks only."""
    style_belief_axis(
        ax,
        ylim=(10, 90),
        ylabel="belief",
        title=title,
        xlim=(0.75, n_x + 0.25),
        grid=False,
    )
    xticks = np.arange(1, n_x + 1)
    ax.set_xticks(xticks)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for side in ("bottom", "left"):
        ax.spines[side].set_visible(True)
        ax.spines[side].set_linewidth(SPINE_LW)
        ax.spines[side].set_color("k")
    ax.spines["bottom"].set_bounds(float(xticks[0]), float(xticks[-1]))
    ax.tick_params(axis="both", direction="in", labelsize=FONT_SIZE, width=SPINE_LW, length=3.5)
    ax.tick_params(axis="x", top=False)
    ax.tick_params(axis="y", right=False)
    ax.xaxis.label.set_fontsize(FONT_SIZE)
    ax.yaxis.label.set_fontsize(FONT_SIZE)
    if title:
        ax.title.set_fontsize(FONT_SIZE)


def plot_xpatt_panel(
    ax: plt.Axes,
    tx: pd.DataFrame,
    tp: pd.DataFrame,
    group: str,
    panel_k: int,
    cmap: np.ndarray,
    inc_to_idx: Dict[float, int],
    inc_levels: np.ndarray,
    corr_levels: np.ndarray,
    title: Optional[str],
    *,
    x_levels: np.ndarray = DIFF_LEVELS,
) -> None:
    """One group panel: data errorbars + predicted mean ± SEM band."""
    points = _xpatt_point_series(
        tx, group, panel_k, cmap, inc_to_idx, inc_levels, corr_levels, x_levels=x_levels
    )
    lines = _xpatt_line_series(
        tp, group, cmap, inc_to_idx, inc_levels, corr_levels, x_levels=x_levels
    )
    draw_points(ax, points)
    draw_lines(ax, lines, band=True)
    _style_xpatt_axes(ax, n_x=len(x_levels), title=title)


def _groups_for_stem(stem: str) -> List[str]:
    if stem == "exp3":
        return ["Forced", "Replayed"]
    if stem in ("exp1a_exp2free_exp3", "sim_act", "sim_intent", "sim_confirm"):
        return ["Non-Free", "Free"]
    return ["Observed", "Free"]


def plot_xpatt_by_experiment(repo_root: Path, out: Optional[Path] = None, dpi: int = 150) -> Path:
    """
    2×4: columns = Exp 1a, 1b, 2, 3.
    Rows: Exp 1a/1b/2 → Observed (row 0), Free (row 1); Exp 3 → Forced, Replayed.
    """
    _setup_fonts()
    repo_root = repo_root.resolve()
    stems = ["exp1a", "exp1b", "exp2", "exp3"]
    row_groups = [
        [("Observed", 1), ("Free", 2)],
        [("Observed", 1), ("Free", 2)],
        [("Observed", 1), ("Free", 2)],
        [("Forced", 1), ("Replayed", 2)],
    ]
    cmap_for_stem = {"exp1b": CMAP_EXP1B}

    fig, axes = plt.subplots(2, 4, figsize=FIGSIZE_2X4, constrained_layout=True)
    fig.patch.set_facecolor("white")
    titles = ["Exp 1a", "Exp 1b", "Exp 2", "Exp 3"]
    for col, stem in enumerate(stems):
        tx, tsub = _read_xpatt_pair(repo_root, stem)
        panel_groups = _groups_for_stem(stem)
        tx = tx[tx["group"].isin(panel_groups)]
        tsub = tsub[tsub["group"].isin(panel_groups)]

        cmap = cmap_for_stem.get(stem, CMAP_DEFAULT)
        inc_levels = np.sort(tx["incentive"].unique())
        corr_levels = np.sort(tx["correct"].unique())
        inc_to_idx = make_inc_map_flexible(inc_levels, cmap.shape[0])
        tp = aggregate_pred(tsub)

        for row in range(2):
            grp, pk = row_groups[col][row]
            plot_xpatt_panel(
                axes[row, col],
                tx,
                tp,
                grp,
                pk,
                cmap,
                inc_to_idx,
                inc_levels,
                corr_levels,
                title=titles[col] if row == 0 else None,
            )

    out = out or (fig_dir(repo_root) / "plots_xpatt_by_experiment.png")
    return save_fig(fig, out, dpi=dpi, facecolor="white")


def plot_xpatt_data_vs_models(repo_root: Path, out: Optional[Path] = None, dpi: int = 150) -> Path:
    """
    2×4: columns = merged data (1a+2free+3), sim act, sim intent, sim confirm.
    Rows: Free (row 0), Non-Free (row 1).
    """
    _setup_fonts()
    repo_root = repo_root.resolve()
    stems = ["exp1a_exp2free_exp3", "sim_act", "sim_intent", "sim_confirm"]
    col_titles = ["Data (1a+2free+3)", "Sim act", "Sim intent", "Sim confirm"]
    row_groups = [("Free", 2), ("Non-Free", 1)]

    fig, axes = plt.subplots(2, 4, figsize=FIGSIZE_2X4, constrained_layout=True)
    fig.patch.set_facecolor("white")
    for col, stem in enumerate(stems):
        tx, tsub = _read_xpatt_pair(repo_root, stem)
        panel_groups = _groups_for_stem(stem)
        tx = tx[tx["group"].isin(panel_groups)]
        tsub = tsub[tsub["group"].isin(panel_groups)]

        inc_levels = np.sort(tx["incentive"].unique())
        corr_levels = np.sort(tx["correct"].unique())
        inc_to_idx = make_inc_map_flexible(inc_levels, CMAP_DEFAULT.shape[0])
        tp = aggregate_pred(tsub)

        for row in range(2):
            grp, pk = row_groups[row]
            plot_xpatt_panel(
                axes[row, col],
                tx,
                tp,
                grp,
                pk,
                CMAP_DEFAULT,
                inc_to_idx,
                inc_levels,
                corr_levels,
                title=col_titles[col] if row == 0 else None,
            )

    out = out or (fig_dir(repo_root) / "plots_xpatt_data_vs_models.png")
    return save_fig(fig, out, dpi=dpi, facecolor="white")


DATA_STEM = "exp1a_exp2free_exp3"
SIM_STEMS: List[Tuple[str, str]] = [
    ("sim_act", "Sim act"),
    ("sim_intent", "Sim intent"),
    ("sim_confirm", "Sim confirm"),
]


def plot_xpatt_empirical_overlay_models(
    repo_root: Path, out: Optional[Path] = None, dpi: int = 150
) -> Path:
    """
    2×3: empirical data (dots) overlaid with each simulation model (lines).
    Rows: Free (row 0), Non-Free (row 1).
    """
    _setup_fonts()
    repo_root = repo_root.resolve()
    row_groups = [("Free", 2), ("Non-Free", 1)]
    panel_groups = _groups_for_stem(DATA_STEM)

    tx, _ = _read_xpatt_pair(repo_root, DATA_STEM)
    tx = tx[tx["group"].isin(panel_groups)]
    inc_levels = np.sort(tx["incentive"].unique())
    corr_levels = np.sort(tx["correct"].unique())
    inc_to_idx = make_inc_map_flexible(inc_levels, CMAP_DEFAULT.shape[0])

    fig, axes = plt.subplots(2, 3, figsize=FIGSIZE_2X3, constrained_layout=True)
    fig.patch.set_facecolor("white")
    for col, (sim_stem, col_title) in enumerate(SIM_STEMS):
        _, tsub = _read_xpatt_pair(repo_root, sim_stem)
        tsub = tsub[tsub["group"].isin(panel_groups)]
        tp = aggregate_pred(tsub)

        for row in range(2):
            grp, pk = row_groups[row]
            plot_xpatt_panel(
                axes[row, col],
                tx,
                tp,
                grp,
                pk,
                CMAP_DEFAULT,
                inc_to_idx,
                inc_levels,
                corr_levels,
                title=col_title if row == 0 else None,
            )

    out = out or (fig_dir(repo_root) / "plots_xpatt_empirical_vs_models.png")
    return save_fig(fig, out, dpi=dpi, facecolor="white")


def main() -> None:
    ap = argparse.ArgumentParser(description="Xpatt 2×4 figures.")
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--out-exp", type=Path, default=None, help="Output for experiment figure")
    ap.add_argument("--out-merged", type=Path, default=None, help="Output for data vs models figure")
    ap.add_argument("--out-overlay", type=Path, default=None, help="Output for empirical overlay figure")
    args = ap.parse_args()
    p1 = plot_xpatt_by_experiment(args.repo_root, out=args.out_exp, dpi=args.dpi)
    p2 = plot_xpatt_data_vs_models(args.repo_root, out=args.out_merged, dpi=args.dpi)
    p3 = plot_xpatt_empirical_overlay_models(args.repo_root, out=args.out_overlay, dpi=args.dpi)
    print(p1)
    print(p2)
    print(p3)


if __name__ == "__main__":
    main()
