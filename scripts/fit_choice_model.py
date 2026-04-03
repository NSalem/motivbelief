# -*- coding: utf-8 -*-
"""
Fit models of choice

Saves ONLY:
- Pickle per experiment x existing choiceType (as before)
- CSV per experiment x existing choiceType (pooled across incentives):
    participant, [parnames], ll
- CSV per experiment x existing choiceType (fit separately per incentive, if incentive column exists):
    participant, incentive, [parnames], ll
"""

#%%
import os
import numpy as np
import pandas as pd
import pickle

from motivbelief.psychofun import psychofun_ll,fit_model_LBFGS

# -----------------------------
# MODEL CONFIG
# -----------------------------
plb = [1, -5, 0.01]
pub = [10,  5, 0.05]
ub  = [30, 10, 0.1]
lb  = [0.5, -10, 0.0]
x0  = [1, 0, 0.01]

cfg = {}
cfg["parnames"] = ["sigma_act", "choice_bias", "p_lapse"]
cfg["fixedpars"] = {}

options = {}
modelinfoChoice = {
    "plb": plb,
    "pub": pub,
    "bounds": [lb, ub],
    "x0": x0,
    "myfun": psychofun_ll,
    "cfg": cfg,
    "options": options
}

expNames = ["exp1a", "exp2", "exp1b", "exp3"]
conditions = ["Free", "Replayed", "Observed", "Forced"]

# -----------------------------
# OUTPUT DIRS
# -----------------------------
OUT_ROOT = "results"
OUT_PKL  = os.path.join(OUT_ROOT, "fits_choice")
OUT_CSV  = os.path.join(OUT_ROOT, "fits_choice")
os.makedirs(OUT_ROOT, exist_ok=True)
os.makedirs(OUT_PKL, exist_ok=True)
os.makedirs(OUT_CSV, exist_ok=True)

def find_incentive_col(df):
    candidates = ["incentive", "incentive_abs", "inc", "stake", "reward"]
    for c in candidates:
        if c in df.columns:
            return c
    return None

for iexp in expNames:

    df = pd.read_csv("data/data_" + iexp + ".csv")

    # -----------------------------
    # PREPROCESS (close to original)
    # -----------------------------
    df = df[~pd.isna(df["conf"])].copy()
    df["correct"] = df["correct"].astype(int)

    resp_num = (df["resp"] == "right") * 1 + (df["resp"] == "left") * -1
    df["a"] = resp_num
    
    # replace left/right with 1 and -1
    side = df["dir"].copy()
    side = side.replace({"right": 1, "left": -1})

    df["stim"] = df["coh"].to_numpy().copy() * side.to_numpy()

    # incentive column (optional) + handle duplicate column names safely
    inc_col = find_incentive_col(df)
    if inc_col is not None:
        inc_series = df.loc[:, inc_col]
        if isinstance(inc_series, pd.DataFrame):
            # duplicate column names -> keep first occurrence
            df = df.loc[:, ~df.columns.duplicated()].copy()
        inc_levels = pd.unique(df[inc_col].dropna())
    else:
        inc_levels = None

    # only loop over choice types that exist in this experiment
    if "choiceType" not in df.columns:
        print(f"[WARN] {iexp}: no 'choiceType' column; skipping.")
        continue

    existing_groups = [g for g in conditions if g in set(df["choiceType"].dropna().unique())]

    for igroup in existing_groups:
        print(iexp, " ", igroup)

        df_group = df[df["choiceType"] == igroup]
        subs = np.unique(df_group["participant"])
        number_subs = len(subs)

        if number_subs == 0:
            continue

        # pooled arrays (to keep pickle similar to your original)
        pars_choice_group = np.zeros((number_subs, len(cfg["parnames"])))
        ll_choice_group   = np.zeros((number_subs,))

        # pooled csv rows
        pooled_rows = []
        # incentive csv rows
        inc_rows = []

        for nsub, isub in enumerate(subs):
            print("_____PARTICIPANT N%d(S%d) %s___________:" % (nsub, isub, igroup))

            # ---- pooled across incentives
            dfsub_allinc = df_group[df_group["participant"] == isub][["a", "stim", "correct"]].dropna()
            if len(dfsub_allinc) == 0:
                continue

            resc = fit_model_LBFGS(
                modelinfoChoice,
                dfsub_allinc,
                options={"max_fun_evals": 300, "display": "off"}
            )

            pars_choice_group[nsub] = resc[0]
            ll_choice_group[nsub]   = resc[1]

            row = {"participant": isub, "ll": resc[1]}
            for p, v in zip(cfg["parnames"], resc[0]):
                row[p] = v
            pooled_rows.append(row)

            # ---- incentive-specific fits
            if inc_col is not None:
                for inc in inc_levels:
                    dfsub_inc = df_group[
                        (df_group["participant"] == isub) & (df_group[inc_col] == inc)
                    ][["a", "stim", "correct"]].dropna()

                    # skip if too few trials
                    if len(dfsub_inc) < 10:
                        continue

                    resc_inc = fit_model_LBFGS(
                        modelinfoChoice,
                        dfsub_inc,
                        options={"max_fun_evals": 300, "display": "off"}
                    )

                    rowi = {"participant": isub, "incentive": inc, "ll": resc_inc[1]}
                    for p, v in zip(cfg["parnames"], resc_inc[0]):
                        rowi[p] = v
                    inc_rows.append(rowi)

        # -----------------------------
        # SAVE PICKLE (once per group)
        # -----------------------------
        results = {
            "pars_choice": pars_choice_group,
            "ll_choice": ll_choice_group,
            "modelinfo_choice": modelinfoChoice,
            "participants": subs,
        }
        out_pkl = os.path.join(OUT_PKL, f"pars_choice_{iexp}_{igroup}.p")
        with open(out_pkl, "wb") as f:
            pickle.dump(results, f)

        # -----------------------------
        # SAVE CSVs (once per group)
        # -----------------------------
        pooled_df = pd.DataFrame(pooled_rows)
        out_csv_pooled = os.path.join(OUT_CSV, f"pars_choice_{iexp}_{igroup}.csv")
        pooled_df.to_csv(out_csv_pooled, index=False)

        if inc_col is not None:
            inc_df = pd.DataFrame(inc_rows)
            out_csv_inc = os.path.join(OUT_CSV, f"pars_choice_{iexp}_{igroup}_byIncentive.csv")
            inc_df.to_csv(out_csv_inc, index=False)