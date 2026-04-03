"""
Xpatt (trial-level) figures: experiment comparison and data vs models.
Port of scripts_figures/do_figsModelAvg_Xpatt_2026_02_20.m with 2×4 layouts.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from motivbelief.plot_makefigs_paths import fig_dir

DIFF_LEVELS = np.array([-0.5, 0.0, 0.5])

CMAP_DEFAULT = 0.7 * np.array([[1.0, 0.0, 0.0], [0.5, 0.5, 0.5], [0.0, 1.0, 0.0]])
CMAP_EXP1B = 0.7 * np.array([[0.0, 0.5, 0.0], [0.0, 1.0, 0.0]])


def _trial_dir(repo: Path, stem: str) -> Path:
    """Prefer `results/stats/trial`; fall back to `results/stats_py/trial` if CSV exists only there."""
    p = repo / "results" / "stats" / "trial" / stem
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


def make_inc_map_flexible(inc_levels: np.ndarray, n_colors: int) -> Dict[float, int]:
    inc_levels = np.sort(np.unique(inc_levels))
    if n_colors == 3 and len(inc_levels) == 3 and np.allclose(inc_levels, [-1, 0, 1]):
        return {-1.0: 0, 0.0: 1, 1.0: 2}
    out: Dict[float, int] = {}
    for i, v in enumerate(inc_levels):
        out[float(v)] = min(i, n_colors - 1)
    return out


def _lookup_inc_idx(inc_to_idx: Dict[float, int], inc: float) -> int:
    for k, v in inc_to_idx.items():
        if np.isclose(float(inc), float(k), rtol=0.0, atol=1e-9):
            return v
    raise KeyError(f"incentive {inc!r} not in {list(inc_to_idx.keys())}")


def _panel_style(panel_k: int, cmap: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """panel_k 1 = open markers (edge color); 2 = filled markers."""
    n = cmap.shape[0]
    if panel_k == 1:
        return np.ones((n, 3)), cmap.copy()
    return cmap.copy(), np.zeros((n, 3))


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
) -> None:
    """One group panel: data errorbars + predicted mean ± SEM band (MATLAB logic)."""
    c_fac, c_edg = _panel_style(panel_k, cmap)
    d0 = tx[tx["group"] == group]
    p0 = tp[tp["group"] == group]

    for cval in corr_levels:
        linestyle = "--" if float(cval) < 0 else "-"
        dc = d0[np.isclose(d0["correct"].astype(float), float(cval))]
        pc = p0[np.isclose(p0["correct"].astype(float), float(cval))]

        for inc in inc_levels:
            cidx = _lookup_inc_idx(inc_to_idx, float(inc))
            col = cmap[cidx]
            if cidx >= cmap.shape[0]:
                continue

            # Data
            d_inc = dc[np.isclose(dc["incentive"].astype(float), float(inc))]
            if not d_inc.empty:
                y = np.full(3, np.nan)
                ys = np.full(3, np.nan)
                for di, dlv in enumerate(DIFF_LEVELS):
                    row = d_inc[np.isclose(d_inc["difficulty"].astype(float), float(dlv))]
                    if not row.empty:
                        y[di] = float(row["conf_mean"].iloc[0])
                        ys[di] = float(row["conf_sem"].iloc[0])
                good = np.isfinite(y) & np.isfinite(ys)
                xg = np.arange(1, 4)[good]
                if len(xg):
                    ax.errorbar(
                        xg,
                        y[good],
                        yerr=ys[good],
                        fmt="o",
                        linestyle="none",
                        color=col,
                        markerfacecolor=c_fac[cidx],
                        markeredgecolor=c_edg[cidx],
                        ecolor=c_edg[cidx],
                    )

            # Prediction line + band
            p_inc = pc[np.isclose(pc["incentive"].astype(float), float(inc))]
            if p_inc.empty:
                continue
            yline = np.full(3, np.nan)
            ysem = np.full(3, np.nan)
            for di, dlv in enumerate(DIFF_LEVELS):
                row = p_inc[np.isclose(p_inc["difficulty"].astype(float), float(dlv))]
                if not row.empty:
                    yline[di] = float(row["pred_mean"].iloc[0])
                    ysem[di] = float(row["pred_sem"].iloc[0])
            good = np.isfinite(yline) & np.isfinite(ysem)
            xg = np.arange(1, 4)[good]
            if len(xg) >= 2:
                yg = yline[good]
                ysg = ysem[good]
                ax.fill_between(
                    xg,
                    yg - ysg,
                    yg + ysg,
                    color=col,
                    alpha=0.18,
                    linewidth=0,
                )
                ax.plot(xg, yg, linestyle=linestyle, color=col)

    ax.set_xlim(0.75, 3.25)
    ax.set_ylim(10, 90)
    ax.set_ylabel("Belief")
    if title:
        ax.set_title(title)
    ax.grid(True, alpha=0.25, linestyle=":")


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
    repo_root = repo_root.resolve()
    stems = ["exp1a", "exp1b", "exp2", "exp3"]
    row_groups = [
        [("Observed", 1), ("Free", 2)],
        [("Observed", 1), ("Free", 2)],
        [("Observed", 1), ("Free", 2)],
        [("Forced", 1), ("Replayed", 2)],
    ]
    cmap_for_stem = {"exp1b": CMAP_EXP1B}

    fig, axes = plt.subplots(2, 4, figsize=(16, 7), constrained_layout=True)
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
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=dpi)
    fig.savefig(out.with_suffix(".svg"))
    plt.close(fig)
    return out


def plot_xpatt_data_vs_models(repo_root: Path, out: Optional[Path] = None, dpi: int = 150) -> Path:
    """
    2×4: columns = merged data (1a+2free+3), sim act, sim intent, sim confirm.
    Rows: Free (row 0), Non-Free (row 1).
    """
    repo_root = repo_root.resolve()
    stems = ["exp1a_exp2free_exp3", "sim_act", "sim_intent", "sim_confirm"]
    col_titles = ["Data (1a+2free+3)", "Sim act", "Sim intent", "Sim confirm"]
    row_groups = [("Free", 2), ("Non-Free", 1)]

    fig, axes = plt.subplots(2, 4, figsize=(16, 7), constrained_layout=True)
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
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=dpi)
    fig.savefig(out.with_suffix(".svg"))
    plt.close(fig)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Xpatt 2×4 figures.")
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--out-exp", type=Path, default=None, help="Output for experiment figure")
    ap.add_argument("--out-merged", type=Path, default=None, help="Output for data vs models figure")
    args = ap.parse_args()
    p1 = plot_xpatt_by_experiment(args.repo_root, out=args.out_exp, dpi=args.dpi)
    p2 = plot_xpatt_data_vs_models(args.repo_root, out=args.out_merged, dpi=args.dpi)
    print(p1)
    print(p2)


if __name__ == "__main__":
    main()
