"""
Behavior violins + subject trajectories (accuracy and confidence by incentive).

"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

from motivbelief.plot_makefigs_paths import fig_dir, stats_avg_root

RNG = np.random.default_rng(42)


def kde_violin(
    ax: plt.Axes,
    data: np.ndarray,
    x_pos: float,
    color: Tuple[float, float, float],
    *,
    width: float = 0.4,
    alpha: float = 0.25,
) -> None:
    data = np.asarray(data, dtype=float)
    data = data[np.isfinite(data)]
    if data.size == 0:
        return
    if data.size == 1:
        ax.scatter([x_pos], [float(data[0])], c=[color], edgecolors="k", zorder=3)
        return
    lo, hi = float(np.min(data)), float(np.max(data))
    if lo == hi:
        y = np.linspace(lo - 0.5, hi + 0.5, 50)
        d = np.ones_like(y) * width
    else:
        kde = gaussian_kde(data)
        y = np.linspace(lo, hi, 80)
        d = kde(y)
        d_max = float(np.max(d)) if np.max(d) > 0 else 1.0
        d = d / d_max * width
    ax.fill_betweenx(
        y, x_pos - d, x_pos + d, facecolor=color, alpha=alpha, edgecolor=(0.4, 0.4, 0.4), linewidth=0.6
    )


def _behav_cfg(stem: str, title: str, groups: List[str], inc, cmap, xlim: Tuple[float, float]) -> Dict[str, Any]:
    return {
        "stem": stem,
        "title": title,
        "groups": groups,
        "inc": np.array(inc, dtype=float),
        "cmap": np.asarray(cmap, dtype=float),
        "xlim": xlim,
    }


def _plot_group_on_axis(
    ax: plt.Axes,
    tmp: pd.DataFrame,
    subj_codes: np.ndarray,
    group_mask: np.ndarray,
    inc_levels: np.ndarray,
    cmap: np.ndarray,
    group_is_first: bool,
    yvals: np.ndarray,
    xT: np.ndarray,
) -> None:
    n_inc = len(inc_levels)
    inc_col = tmp["incentive"].to_numpy(dtype=float)
    if group_is_first:
        c_face = np.ones((n_inc, 3))
        c_edg = cmap[:n_inc]
    else:
        c_face = cmap[:n_inc]
        c_edg = np.ones((n_inc, 3))

    ag = group_mask
    sub_list = np.unique(subj_codes[ag])
    x_jitt = 0.3 * (RNG.random(len(sub_list)) - 0.5)

    for k_inc in range(n_inc):
        iv = inc_levels[k_inc]
        vals = yvals[ag & np.isclose(inc_col, iv)]
        kde_violin(ax, vals, float(xT[k_inc]), tuple(cmap[k_inc]), width=0.4)

    for si, sid in enumerate(sub_list):
        sm = ag & (subj_codes == sid)
        xs, ys = [], []
        for k_inc in range(n_inc):
            iv = inc_levels[k_inc]
            m2 = sm & np.isclose(inc_col, iv)
            if np.any(m2):
                xs.append(float(xT[k_inc] + x_jitt[si]))
                ys.append(float(np.mean(yvals[m2])))
        if len(xs) > 1:
            ax.plot(xs, ys, "-", color=(0.7, 0.7, 0.7), linewidth=1)
        for k_inc in range(n_inc):
            iv = inc_levels[k_inc]
            m2 = sm & np.isclose(inc_col, iv)
            if np.any(m2):
                ax.plot(
                    xT[k_inc] + x_jitt[si],
                    float(np.mean(yvals[m2])),
                    "o",
                    markerfacecolor=tuple(c_face[k_inc]),
                    markeredgecolor=tuple(c_edg[k_inc]),
                )

    inc_mu = np.zeros(n_inc)
    inc_se = np.zeros(n_inc)
    for kk in range(n_inc):
        iv = inc_levels[kk]
        vals = yvals[ag & np.isclose(inc_col, iv)]
        vals = vals[np.isfinite(vals)]
        inc_mu[kk] = float(np.mean(vals)) if vals.size else np.nan
        inc_se[kk] = float(np.std(vals, ddof=1) / np.sqrt(len(vals))) if len(vals) > 1 else np.nan
    for kk in range(n_inc):
        if not np.isfinite(inc_mu[kk]):
            continue
        ax.errorbar(
            xT[kk],
            inc_mu[kk],
            yerr=inc_se[kk] if np.isfinite(inc_se[kk]) else 0,
            fmt="none",
            ecolor=tuple(cmap[kk]),
            linewidth=2,
            capsize=0,
        )
    good = np.isfinite(inc_mu)
    if np.any(good):
        ax.plot(xT[good], inc_mu[good], "-k", linewidth=2)


def plot_behav_figure(repo_root: Path, dpi: int = 150) -> List[Path]:
    repo_root = repo_root.resolve()
    avg_root = stats_avg_root(repo_root)
    out_dir = fig_dir(repo_root)

    specs = [
        _behav_cfg(
            "exp1a",
            "Exp.1a",
            ["Observed", "Free"],
            [-1, 0, 1],
            0.7 * np.array([[1, 0, 0], [0.5, 0.5, 0.5], [0, 1, 0]], dtype=float),
            (0.5, 6.5),
        ),
        _behav_cfg(
            "exp2",
            "Exp.2",
            ["Observed", "Free"],
            [-1, 0, 1],
            0.7 * np.array([[1, 0, 0], [0.5, 0.5, 0.5], [0, 1, 0]], dtype=float),
            (0.5, 6.5),
        ),
        _behav_cfg(
            "exp3",
            "Exp.3",
            ["Forced", "Replayed"],
            [-1, 0, 1],
            0.7 * np.array([[1, 0, 0], [0.5, 0.5, 0.5], [0, 1, 0]], dtype=float),
            (0.5, 6.5),
        ),
        _behav_cfg(
            "exp1b",
            "Exp.1b",
            ["Observed", "Free"],
            [0.1, 1.0],
            0.7 * np.array([[0, 0.5, 0], [0, 1, 0]], dtype=float),
            (0.5, 4.5),
        ),
    ]

    paths: List[Path] = []
    for cfg in specs:
        csv_path = avg_root / cfg["stem"] / f"sub_avg_{cfg['stem']}.csv"
        tmp = pd.read_csv(csv_path)
        g = tmp["group"].astype(str)
        keep = g.isin(cfg["groups"])
        tmp = tmp.loc[keep].copy()
        g = tmp["group"].astype(str)
        p = tmp["participant"].astype(str)
        # np.unique(..., return_inverse=True) returns (unique_vals, inverse_index) only
        _, subj_codes = np.unique(p, return_inverse=True)

        group_id = np.full(len(tmp), np.nan)
        group_id[g == cfg["groups"][0]] = 0
        group_id[g == cfg["groups"][1]] = 1

        inc_levels = cfg["inc"]
        n_inc = len(inc_levels)
        cmap = cfg["cmap"]
        x0 = np.arange(1, n_inc + 1, dtype=float)
        x1 = np.arange(n_inc + 1, 2 * n_inc + 1, dtype=float)

        fig, axes = plt.subplots(1, 2, figsize=(9, 4), constrained_layout=True)
        fig.patch.set_facecolor("white")

        for ax, ycol, ylbl in zip(axes, ["correct", "conf"], ["choice accuracy", "confidence"]):
            yvals = tmp[ycol].to_numpy(dtype=float)
            _plot_group_on_axis(
                ax, tmp, subj_codes, group_id == 0, inc_levels, cmap, True, yvals, x0
            )
            _plot_group_on_axis(
                ax, tmp, subj_codes, group_id == 1, inc_levels, cmap, False, yvals, x1
            )
            ax.set_xlim(cfg["xlim"])
            ax.set_ylim(20, 100)
            ax.set_ylabel(ylbl)
            ax.set_title(cfg["title"])

        fbase = "".join(ch for ch in cfg["title"].lower() if ch.isalnum())
        outp = out_dir / f"plots_behav_avg_{fbase}.png"
        fig.savefig(outp, dpi=dpi, facecolor="white")
        fig.savefig(outp.with_suffix(".svg"), facecolor="white")
        plt.close(fig)
        paths.append(outp)
    return paths


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()
    for p in plot_behav_figure(args.repo_root, dpi=args.dpi):
        print(p)


if __name__ == "__main__":
    main()
