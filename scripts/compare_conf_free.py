"""
Bayesian Model Comparison between the two Free confidence models
(FREE_BMC_FIT_TAGS: pe_wt_v vs bel_bias_v). Pools each experiment's
already-completed per-participant fits (no new joint fit) for the
exp1a / exp2 / combined scopes, and saves the result -- no plotting here
(see motivbelief.plotting.fig_bmc.plot_free_bmc_figure for that).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from motivbelief.modeling.analysis_free import FREE_BMC_FIT_TAGS, free_model_bmc, load_conf_fits

SCOPES = {
    "exp1a": ("exp1a",),
    "exp2": ("exp2",),
    "combined": ("exp1a", "exp2"),
}


def run_free_bmc(data: pd.DataFrame) -> pd.DataFrame:
    rows = [free_model_bmc(data, experiments=experiments) for experiments in SCOPES.values()]
    return pd.concat(rows, ignore_index=True)


def average_aicc_by_scope(data: pd.DataFrame) -> pd.DataFrame:
    """Mean/SEM AICc per (scope, fit_tag), plus a paired Wilcoxon signed-rank
    test on each participant's AICc(FREE_BMC_FIT_TAGS[0]) - AICc(FREE_BMC_FIT_TAGS[1])
    -- same participants fit by both models, so paired rather than
    two-sample. Complements free_model_bmc's group-level BMC (which already
    uses this same AICc column as its evidence, converted via -0.5*AICc) with
    the raw per-model averages a reviewer would expect to see reported directly.
    """
    sub = data.loc[(data["choiceType"] == "Free") & data["fit_tag"].isin(FREE_BMC_FIT_TAGS)]
    m0, m1 = FREE_BMC_FIT_TAGS

    rows = []
    for scope, experiments in SCOPES.items():
        scoped = sub.loc[sub["experiment"].isin(experiments)]
        for tag in FREE_BMC_FIT_TAGS:
            vals = scoped.loc[scoped["fit_tag"] == tag, "AICc"].to_numpy(dtype=float)
            rows.append({
                "scope": scope, "fit_tag": tag, "n": len(vals),
                "mean_aicc": float(np.mean(vals)), "sem_aicc": float(np.std(vals, ddof=1) / np.sqrt(len(vals))),
            })

        id_cols = ["experiment", "participant"] if len(experiments) > 1 else ["participant"]
        wide = scoped.pivot_table(index=id_cols, columns="fit_tag", values="AICc")
        paired = wide[[m0, m1]].dropna()
        diff = paired[m0].to_numpy() - paired[m1].to_numpy()
        wil = stats.wilcoxon(diff, alternative="two-sided", zero_method="wilcox")
        rows.append({
            "scope": scope, "fit_tag": f"paired {m0}-{m1}", "n": len(diff),
            "mean_aicc": float(np.mean(diff)), "sem_aicc": float(np.std(diff, ddof=1) / np.sqrt(len(diff))),
            "wilcoxon_p": float(wil.pvalue),
        })
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    model_tag = "_vs_".join(FREE_BMC_FIT_TAGS)
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help=f"Output CSV (default: results/modeling/bmc_conf/bmc_free_{model_tag}.csv)",
    )
    args = ap.parse_args()
    repo_root = args.repo_root.resolve()

    data = load_conf_fits(repo_root / "results" / "modeling" / "fits_conf")

    aicc = average_aicc_by_scope(data)
    out_aicc = repo_root / "results" / "modeling" / "bmc_conf" / f"aicc_free_{model_tag}.csv"
    out_aicc.parent.mkdir(parents=True, exist_ok=True)
    aicc.to_csv(out_aicc, index=False)
    print("Average AICc (lower is better) + paired Wilcoxon on per-participant AICc difference:")
    print(aicc.round(3).to_string(index=False))
    print(f"Wrote {out_aicc}\n")

    bmc = run_free_bmc(data)
    out = args.out or (
        repo_root / "results" / "modeling" / "bmc_conf" / f"bmc_free_{model_tag}.csv"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    bmc.to_csv(out, index=False)
    print("Random-effects BMC (evidence = -0.5*AICc):")
    print(bmc.to_string(index=False))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
