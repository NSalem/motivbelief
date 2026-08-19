"""
Coefficient bar figures (accuracy + confidence GLM) per experiment.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from motivbelief.plotting.paths import fig_dir, stats_avg_root


def read_within_table(exp_dir: Path, fname: str) -> pd.DataFrame:
    f = exp_dir / fname
    if not f.is_file():
        raise FileNotFoundError(f)
    return pd.read_csv(f)


def get_means_se(T: pd.DataFrame, choice_type: str, coef_list: List[str]) -> Tuple[np.ndarray, np.ndarray]:
    m = np.full(len(coef_list), np.nan)
    se = np.full(len(coef_list), np.nan)
    ct = T["choiceType"].astype(str).str.strip()
    coef = T["coef"].astype(str).str.strip()
    for i, cn in enumerate(coef_list):
        rows = (ct.str.lower() == choice_type.lower()) & (coef.str.lower() == cn.lower())
        if rows.any():
            idx = np.where(rows)[0][0]
            m[i] = float(T.iloc[idx]["mean"])
            se[i] = float(T.iloc[idx]["se"])
    return m, se


def plot_group_bars(
    ax: plt.Axes,
    T: pd.DataFrame,
    choice_types: List[str],
    coefs: List[str],
    offsets: List[float],
) -> None:
    n_c = len(coefs)
    n_g = len(choice_types)
    if n_g == 2 and n_c == 2:
        bw = 0.4
    else:
        bw = 0.2

    for gi, ct in enumerate(choice_types):
        mu, err = get_means_se(T, ct, coefs)
        x = np.arange(1, n_c + 1, dtype=float) + offsets[gi]
        face = 0.5 * np.ones(3) if ct.lower() == "free" else np.ones(3)
        ax.bar(x, mu, width=bw, facecolor=face, edgecolor=(0, 0, 0))
        ax.errorbar(x, mu, yerr=err, fmt="none", ecolor="k", linestyle="none")


def plot_glm_figure(repo_root: Path, dpi: int = 150) -> List[Path]:
    repo_root = repo_root.resolve()
    in_dir = stats_avg_root(repo_root)
    out_dir = fig_dir(repo_root)

    specs: List[Dict[str, Any]] = [
        {
            "name": "exp1a",
            "title": "Exp.1a",
            "resp_acc": "correct",
            "resp_conf": "conf",
            "choice_types": ["Observed", "Free"],
            "coefs": ["b_inc", "b_abs"],
            "xlabels": ["V", "abs(V)"],
            "offsets": [-0.2, 0.2],
        },
        {
            "name": "exp2",
            "title": "Exp.2",
            "resp_acc": "correct",
            "resp_conf": "confSym",
            "choice_types": ["Observed", "Free"],
            "coefs": ["b_inc", "b_abs"],
            "xlabels": ["V", "abs(V)"],
            "offsets": [-0.2, 0.2],
        },
        {
            "name": "exp1b",
            "title": "Exp.1b",
            "resp_acc": "correct",
            "resp_conf": "conf",
            "choice_types": ["Observed", "Free"],
            "coefs": ["b_inc"],
            "xlabels": ["V"],
            "offsets": [-0.1, 0.1],
        },
        {
            "name": "exp1a_exp3",
            "title": "Exp. 1a + Exp.3",
            "resp_acc": "correct",
            "resp_conf": "conf",
            "choice_types": ["Observed", "Forced", "Replayed", "Free"],
            "coefs": ["b_inc", "b_abs"],
            "xlabels": ["V", "abs(V)"],
            "offsets": [-0.3, -0.1, 0.1, 0.3],
        },
    ]

    paths: List[Path] = []
    for S in specs:
        expdir = in_dir / S["name"]
        Tacc = read_within_table(expdir, f"within_summary__{S['name']}__{S['resp_acc']}.csv")
        Tconf = read_within_table(expdir, f"within_summary__{S['name']}__{S['resp_conf']}.csv")

        fig, axes = plt.subplots(2, 1, figsize=(4, 6), constrained_layout=True)
        fig.suptitle(S["title"])
        n_c = len(S["coefs"])

        for ax, T, ylab, ylim in [
            (axes[0], Tacc, "Accuracy", (-2.5, 2.5)),
            (axes[1], Tconf, "Confidence", (-2, 5)),
        ]:
            plot_group_bars(ax, T, S["choice_types"], S["coefs"], S["offsets"])
            ax.set_ylabel(ylab)
            if n_c == 1:
                ax.set_xlim(0.5, 1.5)
            else:
                ax.set_xlim(0.5, n_c + 0.5)
            ax.set_xticks(np.arange(1, n_c + 1))
            ax.set_xticklabels(S["xlabels"])
            ax.set_ylim(ylim)

        outp = out_dir / f"plots_coefs_{S['name']}.png"
        fig.savefig(outp, dpi=dpi)
        fig.savefig(outp.with_suffix(".svg"))
        plt.close(fig)
        paths.append(outp)
    return paths


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()
    for p in plot_glm_figure(args.repo_root, dpi=args.dpi):
        print(p)


if __name__ == "__main__":
    main()
