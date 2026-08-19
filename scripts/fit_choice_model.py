# -*- coding: utf-8 -*-
"""
Fit models of choice

Saves results flat under results/modeling/fits_choice/<exp>/, one pooled
(incentive-blind) fit and one per-incentive fit per (exp, condition):
- results_<condition>.csv / results_<condition>_by_incentive.csv: per-participant parameters, ll, AICc, n_trials
- <stem>.metadata.json: model spec (parnames, bounds, fixed_pars) + fitting config
- <stem>.fitting_log.json: per-participant diagnostics (time_sec, n_trials)
"""

import time
from pathlib import Path

import numpy as np
import pandas as pd

from motivbelief.modeling.choice import psychofun_ll
from motivbelief.modeling.optimize import fit_model_LBFGS, DEFAULT_CHOICE_PRIORS, DEFAULT_CHOICE_PARAM_BOUNDS
from motivbelief.modeling.io import resolve_fit_paths, save_fit_metadata, save_fit_results, save_fit_diagnostics

# MODEL CONFIG
PARNAMES = ["sens_noise", "sens_bias", "p_lapse"]
PLAUSIBLE_LOWER = [DEFAULT_CHOICE_PARAM_BOUNDS[p][0] for p in PARNAMES]
PLAUSIBLE_UPPER = [DEFAULT_CHOICE_PARAM_BOUNDS[p][1] for p in PARNAMES]
LOWER_BOUNDS = [DEFAULT_CHOICE_PARAM_BOUNDS[p][2] for p in PARNAMES]
UPPER_BOUNDS = [DEFAULT_CHOICE_PARAM_BOUNDS[p][3] for p in PARNAMES]
X0 = [DEFAULT_CHOICE_PARAM_BOUNDS[p][4] for p in PARNAMES]

cfg = {"parnames": PARNAMES, "fixedpars": {}, "priors": DEFAULT_CHOICE_PRIORS}
modelinfoChoice = {
    "plb": PLAUSIBLE_LOWER,
    "pub": PLAUSIBLE_UPPER,
    "bounds": [LOWER_BOUNDS, UPPER_BOUNDS],
    "x0": X0,
    "myfun": psychofun_ll,
    "cfg": cfg,
    "options": {},
}

expNames = ["exp1a", "exp2", "exp1b", "exp3"]
conditions = ["Free", "Replayed", "Observed", "Forced"]
# Only Free/Replayed feed the conf-model pipeline. Observed/Forced appear in
# psyfun as empirical curves only (no choice fits).
CHOICE_FIT_CONDITIONS = ["Free", "Replayed"]
OUT_ROOT = "results/modeling/fits_choice"
Path(OUT_ROOT).mkdir(parents=True, exist_ok=True)


def find_incentive_col(df):
    for c in ["incentive", "incentive_abs", "inc", "stake", "reward"]:
        if c in df.columns:
            return c
    return None


for iexp in expNames:
    df = pd.read_csv("data/data_" + iexp + ".csv")

    df = df[~pd.isna(df["conf"])].copy()
    df["correct"] = df["correct"].astype(int)
    df["a"] = (df["resp"] == "right") * 1 + (df["resp"] == "left") * -1
    side = df["dir"].replace({"right": 1, "left": -1})
    df["stim"] = df["coh"].to_numpy().copy() * side.to_numpy()

    inc_col = find_incentive_col(df)
    if inc_col is not None:
        inc_series = df.loc[:, inc_col]
        if isinstance(inc_series, pd.DataFrame):
            df = df.loc[:, ~df.columns.duplicated()].copy()
        inc_levels = pd.unique(df[inc_col].dropna())
    else:
        inc_levels = None

    if "choiceType" not in df.columns:
        print(f"[WARN] {iexp}: no 'choiceType' column; skipping.")
        continue

    existing_groups = [
        g for g in conditions
        if g in CHOICE_FIT_CONDITIONS and g in set(df["choiceType"].dropna().unique())
    ]

    for igroup in existing_groups:
        print(iexp, " ", igroup)

        df_group = df[df["choiceType"] == igroup]
        subs = np.unique(df_group["participant"])
        if len(subs) == 0:
            continue

        pooled_rows = []
        pooled_diag = {}
        byinc_rows = []
        byinc_diag = {}

        for nsub, isub in enumerate(subs):
            print("_____PARTICIPANT N%d(S%d) %s___________:" % (nsub, isub, igroup))

            dfsub_allinc = df_group[df_group["participant"] == isub][["a", "stim", "correct"]].dropna()
            if len(dfsub_allinc) == 0:
                continue

            t0 = time.perf_counter()
            resc = fit_model_LBFGS(
                modelinfoChoice,
                dfsub_allinc,
                options={"maxiter": 300},
                n_restarts=5,
                use_x0=False,
                n_jobs=1,  # restarts are too cheap here for process-pool overhead to pay off
            )
            dt = time.perf_counter() - t0

            row = {"participant": isub, "ll": resc[1], "n_trials": len(dfsub_allinc)}
            for p, v in zip(cfg["parnames"], resc[0]):
                row[p] = v
            pooled_rows.append(row)
            pooled_diag[int(isub)] = {"n_trials": len(dfsub_allinc), "time_sec": dt}

            if inc_col is not None:
                for inc in inc_levels:
                    dfsub_inc = df_group[
                        (df_group["participant"] == isub) & (df_group[inc_col] == inc)
                    ][["a", "stim", "correct"]].dropna()

                    if len(dfsub_inc) < 10:
                        continue

                    t0_inc = time.perf_counter()
                    resc_inc = fit_model_LBFGS(
                        modelinfoChoice,
                        dfsub_inc,
                        options={"maxiter": 300},
                        n_restarts=5,
                        use_x0=False,
                        n_jobs=1,  # restarts are too cheap here for process-pool overhead to pay off
                    )
                    dt_inc = time.perf_counter() - t0_inc

                    rowi = {
                        "participant": isub,
                        "incentive": inc,
                        "ll": resc_inc[1],
                        "n_trials": len(dfsub_inc),
                    }
                    for p, v in zip(cfg["parnames"], resc_inc[0]):
                        rowi[p] = v
                    byinc_rows.append(rowi)
                    byinc_diag[f"{int(isub)}_inc{inc}"] = {
                        "n_trials": len(dfsub_inc),
                        "time_sec": dt_inc,
                    }

        bounds_dict = {
            "lower": LOWER_BOUNDS,
            "upper": UPPER_BOUNDS,
            "plausible_lower": PLAUSIBLE_LOWER,
            "plausible_upper": PLAUSIBLE_UPPER,
        }
        fitting_config_dict = {
            "optimizer": "LBFGS",
            "maxiter": 300,
            "n_restarts": 5,
            "use_x0": False,
        }

        paths_pooled = resolve_fit_paths(OUT_ROOT, iexp, f"results_{igroup}")
        save_fit_metadata(
            paths_pooled,
            parnames=PARNAMES,
            bounds=bounds_dict,
            fixed_pars={},
            fitting_config=fitting_config_dict,
        )
        save_fit_results(paths_pooled, pd.DataFrame(pooled_rows))
        save_fit_diagnostics(paths_pooled, pooled_diag)
        print(f"Saved pooled fit to {paths_pooled.results_path}")

        if byinc_rows:
            paths_byinc = resolve_fit_paths(OUT_ROOT, iexp, f"results_{igroup}_by_incentive")
            save_fit_metadata(
                paths_byinc,
                parnames=PARNAMES,
                bounds=bounds_dict,
                fixed_pars={},
                fitting_config=fitting_config_dict,
            )
            save_fit_results(paths_byinc, pd.DataFrame(byinc_rows))
            save_fit_diagnostics(paths_byinc, byinc_diag)
            print(f"Saved by-incentive fit to {paths_byinc.results_path}")
