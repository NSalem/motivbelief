# -*- coding: utf-8 -*-
"""Identifiability/recovery analysis from Free cross-fit tables (``scripts/recover_free.py``).

1. Point-estimate confusion matrix (``conf_recovery.classification_accuracy``).
2. Bootstrap-resampled BMC (``analysis_free.bootstrap_model_comparison_bmc``).
"""

import os

import pandas as pd

from motivbelief.modeling.analysis_free import bootstrap_model_comparison_bmc, summarize_bootstrap_bmc
from motivbelief.modeling.conf_recovery import classification_accuracy

N_BOOT = 1000
SEED = 777

CONDITIONS = ["Free"]
ROOT = os.path.join("results", "modeling", "recovery_conf")


def analyze_condition(condition: str) -> None:
    path = os.path.join(ROOT, condition, "identifiability.csv")
    if not os.path.exists(path):
        print(f"[WARN] {path} not found, skipping {condition}")
        return
    df = pd.read_csv(path)

    confusion = classification_accuracy(df, ic_col="aicc")
    out_confusion = os.path.join(ROOT, condition, "confusion_matrix.csv")
    confusion.to_csv(out_confusion, index=False)
    print(f"\n[{condition}] confusion matrix (fraction of participants, by lowest AICc):")
    print(confusion.round(3))
    print(f"  saved {out_confusion}")

    boot_frames = []
    summary_frames = []
    for gen_model in sorted(df["generative_model"].unique()):
        sub = df[df["generative_model"] == gen_model]
        boot = bootstrap_model_comparison_bmc(
            sub, model_col="fitted_model", evidence_col="ll", n_boot=N_BOOT, 
            resample_size = 90,
            seed=SEED,
        )
        
        boot["generative_model"] = gen_model
        boot_frames.append(boot)

        summary = summarize_bootstrap_bmc(boot, model_col="fit_model")
        summary["generative_model"] = gen_model
        summary_frames.append(summary)

    boot_df = pd.concat(boot_frames, ignore_index=True)
    out_boot = os.path.join(ROOT, condition, "bootstrap_bmc.csv")
    boot_df.to_csv(out_boot, index=False)

    summary_df = pd.concat(summary_frames, ignore_index=True)
    out_summary = os.path.join(ROOT, condition, "bootstrap_bmc_summary.csv")
    summary_df.to_csv(out_summary, index=False)
    print(f"[{condition}] bootstrap BMC summary ({N_BOOT} resamples):")
    print(summary_df[["generative_model", "fit_model", "exceedance_probability_mean",
                       "exceedance_probability_lo95", "exceedance_probability_hi95"]].round(3))
    print(f"  saved {out_boot}")
    print(f"  saved {out_summary}")


def main() -> None:
    for condition in CONDITIONS:
        analyze_condition(condition)


if __name__ == "__main__":
    main()
