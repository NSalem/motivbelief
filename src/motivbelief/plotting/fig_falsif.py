"""
Incentive-effect falsification figure: 3×3 bars (participant average + xpatt sim overlays).
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager

from motivbelief.plotting.paths import fig_dir, stats_avg_root, stats_trial_root

EXP_STEM = "exp1a_exp2free_exp3"
GROUPS: List[str] = ["Free", "Non-Free"]
SIMS = [
    {"stem": "sim_act", "label": "Act"},
    {"stem": "sim_intent", "label": "Intent"},
    {"stem": "sim_confirm", "label": "Confirm"},
]

# Match MATLAB Position width×height = 300×600 px (~3×6 in); SVG export is 450×900 at 150 dpi.
FIGSIZE = (3.0, 6.0)

YLIM1 = (0.0, 4.0)
YLIM2 = (0.0, 6.0)
YLIM3 = (-3.0, 4.5)

DATA_BAR_FACE = (0.9, 0.9, 0.9)
DATA_BAR_EDGE = (1.0, 1.0, 1.0)
DATA_ERR_COLOR = (0.0, 0.0, 0.0)
DATA_ERR_LW = 1.0
MODEL_MFC = (1.0, 1.0, 1.0)
MODEL_MEC = (0.5, 0.5, 0.5)
MODEL_ERR_LW = 1.5
MODEL_MS = 6.0
BAR_WIDTH = 0.7
# Matplotlib capsize is the half-width of the cap (center→end) in points.
# Want full cap width = half bar width → half-cap = quarter bar width.
# Panel is 88 px wide over xlim span 2.0 @ 150 dpi.
ERR_CAPSIZE = (BAR_WIDTH / 4.0) / 2.0 * (88.0 / 150.0) * 72.0  # ≈ 3.70 pt
# MATLAB SVG: 16 px ticks / 17.6 px labels on 450-px fig @ 150 dpi → 7.7 / 8.4 pt.
TICK_FS = 7.5
LABEL_FS = 8.0
TITLE_FS = 8.0
# SVG rotate(-30) is clockwise; matplotlib positive angles are CCW → +30.
XTICK_ROT = 30
# Panel boxes from panels/inc_eff_falsif.svg on a 450×900 canvas.
_SUBPLOT = dict(
    left=60 / 450,
    right=429 / 450,
    bottom=(900 - 850) / 900,
    top=(900 - 34) / 900,
    wspace=52 / 88,
    hspace=39 / 246,
)


def read_avg_within_summary(csv_path: Path) -> pd.DataFrame:
    raw = pd.read_csv(csv_path)
    keep = raw[raw["coef"].astype(str) == "b_inc"].copy()
    if keep.empty:
        raise ValueError(f"No b_inc rows in {csv_path}")
    out = pd.DataFrame(
        {
            "Group": keep["choiceType"].astype(str).values,
            "inc_est": keep["mean"].astype(float).values,
            "inc_lcl": (keep["mean"] - 1.96 * keep["se"]).astype(float).values,
            "inc_ucl": (keep["mean"] + 1.96 * keep["se"]).astype(float).values,
        }
    )
    return out


def read_xpattern_within_group(csv_path: Path) -> pd.DataFrame:
    raw = pd.read_csv(csv_path)
    groups = raw["Group"].astype(str).unique().tolist()
    rows = []
    for g in groups:
        r_c = raw[(raw["Group"] == g) & (raw["Effect"].astype(str) == "Incentive|Correct")]
        r_e = raw[(raw["Group"] == g) & (raw["Effect"].astype(str) == "Incentive|Error")]
        row: Dict[str, object] = {"Group": g}
        if not r_c.empty:
            row["inc_corr_est"] = float(r_c.iloc[0]["estimate"])
            row["inc_corr_lcl"] = float(r_c.iloc[0]["lcl"])
            row["inc_corr_ucl"] = float(r_c.iloc[0]["ucl"])
        else:
            row["inc_corr_est"] = np.nan
            row["inc_corr_lcl"] = np.nan
            row["inc_corr_ucl"] = np.nan
        if not r_e.empty:
            row["inc_err_est"] = float(r_e.iloc[0]["estimate"])
            row["inc_err_lcl"] = float(r_e.iloc[0]["lcl"])
            row["inc_err_ucl"] = float(r_e.iloc[0]["ucl"])
        else:
            row["inc_err_est"] = np.nan
            row["inc_err_lcl"] = np.nan
            row["inc_err_ucl"] = np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def _pick_idx(T: pd.DataFrame, group_name: str) -> Optional[int]:
    g = T["Group"].astype(str)
    want = str(group_name)
    for i in range(len(T)):
        if g.iloc[i] == want:
            return i
    for i in range(len(T)):
        if g.iloc[i].lower() == want.lower():
            return i
    return None


def _setup_fonts() -> None:
    """Use Arial when available; else bundled Liberation Sans (same metrics as Arial)."""
    font_dir = Path(__file__).resolve().parent / "fonts"
    for ttf in ("LiberationSans-Regular.ttf", "LiberationSans-Bold.ttf"):
        path = font_dir / ttf
        if path.is_file():
            font_manager.fontManager.addfont(str(path))
    has_arial = any(getattr(f, "name", None) == "Arial" for f in font_manager.fontManager.ttflist)
    # Put the face we actually have first — matplotlib won't reliably fall through
    # from a missing Arial to the next entry (it jumps to DejaVu).
    primary = "Arial" if has_arial else "Liberation Sans"
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [primary, "Helvetica", "DejaVu Sans"],
            "axes.linewidth": 0.5,
            "axes.edgecolor": (0.15, 0.15, 0.15),
            "xtick.color": (0.15, 0.15, 0.15),
            "ytick.color": (0.15, 0.15, 0.15),
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def pick_value(T: pd.DataFrame, group_name: str, what: str) -> float:
    if T.empty:
        return float("nan")
    idx = _pick_idx(T, group_name)
    if idx is None:
        return float("nan")
    row = T.iloc[idx]
    if what == "inc":
        return float(row["inc_est"])
    if what == "inc_corr":
        return float(row["inc_corr_est"])
    if what == "inc_err":
        return float(row["inc_err_est"])
    raise ValueError(what)


def pick_ci_half(T: pd.DataFrame, group_name: str, what: str) -> float:
    if T.empty:
        return float("nan")
    idx = _pick_idx(T, group_name)
    if idx is None:
        return float("nan")
    row = T.iloc[idx]
    if what == "inc":
        l, u = float(row["inc_lcl"]), float(row["inc_ucl"])
    elif what == "inc_corr":
        l, u = float(row["inc_corr_lcl"]), float(row["inc_corr_ucl"])
    elif what == "inc_err":
        l, u = float(row["inc_err_lcl"]), float(row["inc_err_ucl"])
    else:
        raise ValueError(what)
    return (u - l) / 2


def _style_axes(ax: plt.Axes) -> None:
    """Match MATLAB: TickDir out, Box off, thin spines, no x-ticks, +30° labels."""
    ax.set_xlim(0.5, 2.5)
    ax.tick_params(axis="both", direction="out", labelsize=TICK_FS)
    ax.tick_params(axis="x", length=0, pad=2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for side in ("bottom", "left"):
        ax.spines[side].set_linewidth(0.5)
        ax.spines[side].set_color((0.15, 0.15, 0.15))
    ax.yaxis.set_tick_params(width=0.5, length=3.5, colors=(0.15, 0.15, 0.15))
    ax.tick_params(axis="x", labelrotation=XTICK_ROT)
    for label in ax.get_xticklabels():
        # Match MATLAB SVG rotate(-30) [= mpl +30]; hang labels under ticks.
        label.set_horizontalalignment("right")
        label.set_rotation_mode("anchor")


def _draw_column_titles(fig: plt.Figure) -> None:
    """Place top-row titles in figure coords (MATLAB SVG anchors at y≈32 on a 900-px canvas)."""
    # Centers of the three top-row panels; y matches MATLAB title baseline.
    anchors = [
        (104 / 450, 1.0 - 28 / 900, "Avg Free vs Non-Free"),
        (244 / 450, 1.0 - 28 / 900, f"corr vs incorr ({GROUPS[0].lower()})"),
        (385 / 450, 1.0 - 28 / 900, f"corr vs incorr ({GROUPS[1].lower()})"),
    ]
    for x, y, text in anchors:
        fig.text(
            x,
            y,
            text,
            ha="center",
            va="bottom",
            fontsize=TITLE_FS,
            fontweight="bold",
            clip_on=False,
        )


def _overlay_model(ax: plt.Axes, x: np.ndarray, ys: List[float], es: List[float]) -> None:
    ax.errorbar(
        x,
        ys,
        yerr=es,
        fmt="o",
        linestyle="none",
        markerfacecolor=MODEL_MFC,
        markeredgecolor=MODEL_MEC,
        ecolor=MODEL_MEC,
        linewidth=MODEL_ERR_LW,
        markeredgewidth=MODEL_ERR_LW,
        markersize=MODEL_MS,
        capsize=ERR_CAPSIZE,
        capthick=MODEL_ERR_LW,
        zorder=3,
    )


def plot_corr_err_panel(
    ax: plt.Axes,
    exp_xp: pd.DataFrame,
    which_group: str,
    sim_stem: str,
    trial_root: Path,
) -> None:
    if exp_xp.empty:
        ax.text(0.1, 0.5, "No xpattern loaded", transform=ax.transAxes)
        ax.set_axis_off()
        return

    y = [pick_value(exp_xp, which_group, "inc_corr"), pick_value(exp_xp, which_group, "inc_err")]
    e = [pick_ci_half(exp_xp, which_group, "inc_corr"), pick_ci_half(exp_xp, which_group, "inc_err")]
    x = np.arange(1, 3)
    ax.bar(x, y, width=BAR_WIDTH, facecolor=DATA_BAR_FACE, edgecolor=DATA_BAR_EDGE, linewidth=0.5)
    ax.errorbar(
        x,
        y,
        yerr=e,
        fmt="none",
        ecolor=DATA_ERR_COLOR,
        linewidth=DATA_ERR_LW,
        capsize=ERR_CAPSIZE,
        capthick=DATA_ERR_LW,
        zorder=2,
    )

    sim_path = trial_root / sim_stem / "within_group_conf_xpatt.csv"
    if sim_path.is_file():
        sim_xp = read_xpattern_within_group(sim_path)
        ys = [pick_value(sim_xp, which_group, "inc_corr"), pick_value(sim_xp, which_group, "inc_err")]
        es = [pick_ci_half(sim_xp, which_group, "inc_corr"), pick_ci_half(sim_xp, which_group, "inc_err")]
        _overlay_model(ax, x, ys, es)
    else:
        ax.text(0.5, 0.5, "No trial CSV", transform=ax.transAxes, ha="center")

    ax.set_ylabel(f"incentive ({which_group.lower()})", fontsize=LABEL_FS)
    ax.set_xticks([1, 2])
    ax.set_xticklabels(["corr.", "incorr."])
    _style_axes(ax)


def plot_falsif_xpatt_figure(
    repo_root: Path,
    out: Optional[Path] = None,
    dpi: int = 150,
    *,
    trial_root: Optional[Path] = None,
    sim_stems: Optional[List[str]] = None,
) -> Path:
    repo_root = repo_root.resolve()
    avg_root = stats_avg_root(repo_root)
    tr_root = trial_root if trial_root is not None else stats_trial_root(repo_root)
    data_tr_root = stats_trial_root(repo_root)
    sim_stem_list = sim_stems if sim_stems is not None else [S["stem"] for S in SIMS]

    exp_avg_path = avg_root / EXP_STEM / f"within_summary__{EXP_STEM}__conf.csv"
    exp_xp_path = data_tr_root / EXP_STEM / "within_group_conf_xpatt.csv"

    exp_avg = read_avg_within_summary(exp_avg_path)
    exp_xp = read_xpattern_within_group(exp_xp_path) if exp_xp_path.is_file() else pd.DataFrame()

    _setup_fonts()

    # Geometry mirrors MATLAB tiledlayout compact panels (see _SUBPLOT / inc_eff_falsif.svg).
    fig, axes = plt.subplots(
        3,
        3,
        figsize=FIGSIZE,
        facecolor="white",
        constrained_layout=False,
    )
    fig.subplots_adjust(**_SUBPLOT)

    for s, S in enumerate(SIMS):
        row = s
        sim_stem = sim_stem_list[s] if s < len(sim_stem_list) else S["stem"]
        # Column 0: avg b_inc Free vs Non-Free
        ax1 = axes[row, 0]
        y = [pick_value(exp_avg, GROUPS[0], "inc"), pick_value(exp_avg, GROUPS[1], "inc")]
        e = [pick_ci_half(exp_avg, GROUPS[0], "inc"), pick_ci_half(exp_avg, GROUPS[1], "inc")]
        x = np.arange(1, 3)
        ax1.bar(x, y, width=BAR_WIDTH, facecolor=DATA_BAR_FACE, edgecolor=DATA_BAR_EDGE, linewidth=0.5)
        ax1.errorbar(
            x,
            y,
            yerr=e,
            fmt="none",
            ecolor=DATA_ERR_COLOR,
            linewidth=DATA_ERR_LW,
            capsize=ERR_CAPSIZE,
            capthick=DATA_ERR_LW,
            zorder=2,
        )
        sim_avg = avg_root / S["stem"] / f"within_summary__{S['stem']}__conf.csv"
        if sim_avg.is_file():
            sim_tab = read_avg_within_summary(sim_avg)
            ys = [pick_value(sim_tab, GROUPS[0], "inc"), pick_value(sim_tab, GROUPS[1], "inc")]
            es = [pick_ci_half(sim_tab, GROUPS[0], "inc"), pick_ci_half(sim_tab, GROUPS[1], "inc")]
            _overlay_model(ax1, x, ys, es)
        else:
            ax1.text(
                0.5,
                0.5,
                f"No {S['label']} avg",
                transform=ax1.transAxes,
                ha="center",
            )
        ax1.set_ylabel("incentive effect", fontsize=LABEL_FS)
        ax1.set_xticks([1, 2])
        ax1.set_xticklabels([GROUPS[0].lower(), GROUPS[1].lower()])
        ax1.set_ylim(YLIM1)
        ax1.set_yticks([0, 1, 2, 3, 4])
        _style_axes(ax1)

        ax2 = axes[row, 1]
        plot_corr_err_panel(ax2, exp_xp, GROUPS[0], sim_stem, tr_root)
        ax2.set_ylim(YLIM2)
        ax2.set_yticks([0, 1, 2, 3, 4, 5, 6])

        ax3 = axes[row, 2]
        plot_corr_err_panel(ax3, exp_xp, GROUPS[1], sim_stem, tr_root)
        ax3.set_ylim(YLIM3)
        ax3.set_yticks([-3, -2, -1, 0, 1, 2, 3, 4])

    _draw_column_titles(fig)

    out = out or (fig_dir(repo_root) / "plot_inc_eff_falsif.png")
    fig.savefig(out, dpi=dpi, facecolor="white")
    fig.savefig(out.with_suffix(".svg"), facecolor="white")
    plt.close(fig)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()
    print(plot_falsif_xpatt_figure(args.repo_root, out=args.out, dpi=args.dpi))


if __name__ == "__main__":
    main()
