# -*- coding: utf-8 -*-
"""Free-condition structural identifiability + parameter recovery.

Cross-fit pe_wt_v vs bel_bias_v (mirrors ``fit_conf_free.MODELS``). Parameter
recovery is the diagonal of the same table. Run
``analyze_recovery_identifiability.py`` for bootstrap BMC on the output.

Use ``--n-participants`` for a cheap pilot (cost ∝ n × n_variants²).
"""

import argparse
import os

from motivbelief.modeling.conf_recovery import ModelVariant, run_cross_fit, add_aicc, correlation_block

N_PARTICIPANTS = 250  # synthetic participants per generative model
N_MC = 5000
N_RESTARTS = 5
N_JOBS = 1
MAX_FUN_EVALS = 100
KERNEL_BW = 5.0
SEED0 = 42

OUT_DIR = os.path.join("results", "modeling", "recovery_conf", "Free")
os.makedirs(OUT_DIR, exist_ok=True)

VARIANTS = [
    ModelVariant(
        name="pe_wt_v",
        parnames=["pe_wt", "pe_wt_v", "bel_noise"],
        fixedpars={"mismatch_coef": 0.0},
    ),
    ModelVariant(
        name="bel_bias_v",
        parnames=["pe_wt", "bel_bias_v", "bel_noise"],
        fixedpars={"mismatch_coef": 0.0},
    ),
]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--n-participants",
        type=int,
        default=N_PARTICIPANTS,
        help=f"Synthetic participants per generative model (default: {N_PARTICIPANTS}).",
    )
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    df = run_cross_fit(
        "Free", VARIANTS, VARIANTS, args.n_participants, SEED0,
        n_mc=N_MC, n_restarts=N_RESTARTS, n_jobs=N_JOBS, kernel_bw=KERNEL_BW,
        max_fun_evals=MAX_FUN_EVALS,
    )
    df = add_aicc(df)

    out_csv = os.path.join(OUT_DIR, "identifiability.csv")
    df.to_csv(out_csv, index=False)
    print(f"saved {out_csv}  ({len(df)} rows)")

    for variant in VARIANTS:
        name = variant.name
        diag = df[(df["generative_model"] == name) & (df["fitted_model"] == name)]

        out_recovery = os.path.join(OUT_DIR, f"param_recovery_{name}.csv")
        diag.to_csv(out_recovery, index=False)
        print(f"saved {out_recovery}  ({len(diag)} rows)")

        corr = correlation_block(diag, variant.parnames)
        out_corr = os.path.join(OUT_DIR, f"param_recovery_corr_{name}.csv")
        corr.to_csv(out_corr)
        print(f"saved {out_corr}")
        print(f"[{name}]")
        print(corr.round(2))


if __name__ == "__main__":
    main()
