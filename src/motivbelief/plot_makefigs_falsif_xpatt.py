"""
Incentive-effect falsification figure: 3×3 bars (participant average + xpatt sim overlays).
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from motivbelief.plot_makefigs_paths import fig_dir, stats_avg_root, stats_trial_root

EXP_STEM = "exp1a_exp2free_exp3"
GROUPS: List[str] = ["Free", "Non-Free"]
SIMS = [
    {"stem": "sim_act", "label": "Act"},
    {"stem": "sim_intent", "label": "Intent"},
    {"stem": "sim_confirm", "label": "Confirm"},
]

YLIM1 = (0.0, 4.0)
YLIM2 = (0.0, 6.0)
YLIM3 = (-3.0, 4.5)


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


def plot_corr_err_panel(
    ax: plt.Axes,
    exp_xp: pd.DataFrame,
    which_group: str,
    sim_stem: str,
    trial_root: Path,
) -> None:
    data_bar_face = (0.9, 0.9, 0.9)
    data_bar_edge = (1, 1, 1)
    data_err = (0, 0, 0)
    model_mec = 0.5 * np.ones(3)
    model_mfc = (1, 1, 1)

    if exp_xp.empty:
        ax.text(0.1, 0.5, "No xpattern loaded", transform=ax.transAxes)
        ax.set_axis_off()
        return

    y = [pick_value(exp_xp, which_group, "inc_corr"), pick_value(exp_xp, which_group, "inc_err")]
    e = [pick_ci_half(exp_xp, which_group, "inc_corr"), pick_ci_half(exp_xp, which_group, "inc_err")]
    x = np.arange(1, 3)
    ax.bar(x, y, width=0.7, facecolor=data_bar_face, edgecolor=data_bar_edge)
    ax.errorbar(x, y, yerr=e, fmt="none", ecolor=data_err, linewidth=1)

    sim_path = trial_root / sim_stem / "within_group_conf_xpatt.csv"
    if sim_path.is_file():
        sim_xp = read_xpattern_within_group(sim_path)
        ys = [pick_value(sim_xp, which_group, "inc_corr"), pick_value(sim_xp, which_group, "inc_err")]
        es = [pick_ci_half(sim_xp, which_group, "inc_corr"), pick_ci_half(sim_xp, which_group, "inc_err")]
        ax.errorbar(
            x,
            ys,
            yerr=es,
            fmt="o",
            linestyle="none",
            markerfacecolor=model_mfc,
            markeredgecolor=model_mec,
            ecolor=model_mec,
            linewidth=1.5,
            capsize=0,
        )
    else:
        ax.text(0.5, 0.5, f"No trial CSV", transform=ax.transAxes, ha="center")

    ax.set_ylabel(f"incentive ({which_group.lower()})")
    ax.set_xlim(0.5, 2.5)
    ax.set_xticks([1, 2])
    ax.set_xticklabels(["corr.", "incorr."])
    ax.tick_params(axis="x", length=0)


def plot_falsif_xpatt_figure(repo_root: Path, out: Optional[Path] = None, dpi: int = 150) -> Path:
    repo_root = repo_root.resolve()
    avg_root = stats_avg_root(repo_root)
    tr_root = stats_trial_root(repo_root)

    exp_avg_path = avg_root / EXP_STEM / f"within_summary__{EXP_STEM}__conf.csv"
    exp_xp_path = tr_root / EXP_STEM / "within_group_conf_xpatt.csv"

    exp_avg = read_avg_within_summary(exp_avg_path)
    exp_xp = read_xpattern_within_group(exp_xp_path) if exp_xp_path.is_file() else pd.DataFrame()

    fig, axes = plt.subplots(3, 3, figsize=(7.5, 9), constrained_layout=True)

    for s, S in enumerate(SIMS):
        row = s
        # Column 0: avg b_inc Free vs Non-Free
        ax1 = axes[row, 0]
        y = [pick_value(exp_avg, GROUPS[0], "inc"), pick_value(exp_avg, GROUPS[1], "inc")]
        e = [pick_ci_half(exp_avg, GROUPS[0], "inc"), pick_ci_half(exp_avg, GROUPS[1], "inc")]
        x = np.arange(1, 3)
        ax1.bar(x, y, width=0.7, facecolor=(0.9, 0.9, 0.9), edgecolor=(1, 1, 1))
        ax1.errorbar(x, y, yerr=e, fmt="none", color=(0, 0, 0), linewidth=1)
        sim_avg = avg_root / S["stem"] / f"within_summary__{S['stem']}__conf.csv"
        if sim_avg.is_file():
            sim_tab = read_avg_within_summary(sim_avg)
            ys = [pick_value(sim_tab, GROUPS[0], "inc"), pick_value(sim_tab, GROUPS[1], "inc")]
            es = [pick_ci_half(sim_tab, GROUPS[0], "inc"), pick_ci_half(sim_tab, GROUPS[1], "inc")]
            ax1.errorbar(
                x,
                ys,
                yerr=es,
                fmt="o",
                linestyle="none",
                markerfacecolor=(1, 1, 1),
                markeredgecolor=0.5 * np.ones(3),
                ecolor=0.5 * np.ones(3),
                linewidth=1.5,
            )
        ax1.set_ylabel("incentive effect")
        ax1.set_xlim(0.5, 2.5)
        ax1.set_xticks([1, 2])
        ax1.set_xticklabels([GROUPS[0].lower(), GROUPS[1].lower()])
        ax1.tick_params(axis="x", length=0)
        ax1.set_ylim(YLIM1)
        if s == 0:
            ax1.set_title("Avg Free vs Non-Free")

        ax2 = axes[row, 1]
        plot_corr_err_panel(ax2, exp_xp, GROUPS[0], S["stem"], tr_root)
        ax2.set_ylim(YLIM2)
        if s == 0:
            ax2.set_title(f"corr vs incorr ({GROUPS[0].lower()})")

        ax3 = axes[row, 2]
        plot_corr_err_panel(ax3, exp_xp, GROUPS[1], S["stem"], tr_root)
        ax3.set_ylim(YLIM3)
        if s == 0:
            ax3.set_title(f"corr vs incorr ({GROUPS[1].lower()})")

    out = out or (fig_dir(repo_root) / "plot_inc_eff_falsif.png")
    fig.savefig(out, dpi=dpi)
    fig.savefig(out.with_suffix(".svg"))
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
