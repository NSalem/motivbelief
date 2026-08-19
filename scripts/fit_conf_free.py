# -*- coding: utf-8 -*-
"""Fit confidence model variants for the Free condition.

Free: sens_noise/sens_bias/p_lapse from the standalone Free choice fit;
confidence LL is ``conf_ll.conf_ll_binned`` with ``condition_is_free=True``.

N_JOBS=1 and reduced MAX_FUN_EVALS: each LL eval is cheap, so BADS GP overhead
dominates and process-pool parallelism is not worth it at this scale.
"""

from pathlib import Path

from motivbelief.modeling.fit_conf import fit_confidence_variant
from motivbelief.modeling.io import load_choice_pars_csv, load_exp_df

expNames = ["exp1a", "exp2"]
CONDITION = "Free"

MIN_TRIALS = 20
N_MC = 5000
N_JOBS = 1
N_RESTARTS = 5
KERNEL_BW = 5.0
USE_X0 = False
MAX_FUN_EVALS = 100

OUT_DIR = Path("results/modeling/fits_conf")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Stem/tag names double as file-path labels — keep in sync with
# analysis_free.FREE_BMC_FIT_TAGS and simulate_belief.DEFAULT_FIT_TAG.
MODELS = [
    {
        "name": "pe_wt_v",
        "parnames": ["pe_wt", "pe_wt_v", "bel_noise"],
    },

    {
        "name": "bel_bias_v",
        "parnames": ["pe_wt", "bel_bias_v", "bel_noise"],
    },
]


def main() -> None:
    for iexp in expNames:
        df = load_exp_df(iexp)
        if "choiceType" not in df.columns or CONDITION not in set(df["choiceType"].dropna().unique()):
            print(f"[WARN] {iexp}: no {CONDITION!r} trials; skipping.")
            continue

        df_group = df[df["choiceType"] == CONDITION]
        choice_pars = load_choice_pars_csv(iexp, CONDITION)

        for model in MODELS:
            print(f"\n{'='*60}")
            print(f"Fitting model: {iexp} {CONDITION} {model['name']}")
            print(f"Parameters: {model['parnames']}")
            print(f"{'='*60}")

            fit_confidence_variant(
                iexp=iexp,
                df_group=df_group,
                model=model,
                out_dir=OUT_DIR,
                stem=f"results_{CONDITION}_{model['name']}",
                choice_pars=choice_pars,
                condition_is_free=True,
                min_trials=MIN_TRIALS,
                n_mc=N_MC,
                n_restarts=N_RESTARTS,
                kernel_bw=KERNEL_BW,
                n_jobs=N_JOBS,
                use_x0=USE_X0,
                max_fun_evals=MAX_FUN_EVALS,
            )


if __name__ == "__main__":
    main()
