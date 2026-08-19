from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd

from motivbelief.modeling.conf_ll import expected_confidence, simulate_act_conf
from motivbelief.modeling.io import load_exp_df

sLevels = [-38, -9, -5, -3, -1, 1, 3, 5, 9, 38]
pRightObs = [0.0308, 0.1675, 0.2842, 0.34, 0.4496, 0.5504, 0.66, 0.7158, 0.8325, 0.9692]
incLevels = [-1, 0, 1]
nreps = 8
s = []
inc = []
for irep in range(nreps):
    for iinc in incLevels:
        for ic in sLevels:
            s.append(ic)
            inc.append(iinc)
s = np.array(s)
inc = np.array(inc)

# Pooled Free-choice cohort; pass --experiments to restrict (e.g. exp1a-only).
EXPERIMENTS = ("exp1a", "exp2")
CONDITION = "Free"
DEFAULT_FIT_TAG = "pe_wt_v"
FITS_CONF_DIR = "results/modeling/fits_conf"
CHOICE_ROOT = "results/modeling/fits_choice"
DEFAULT_N_MC = 5000
SIM_OUT_DIR = "results/sims"

# Scalar conf params that may appear in a Free fit CSV.
# Absent params are set to 0 (identity for additive/multiplicative terms).
KNOWN_CONF_PARAMS = (
    "pe_wt",
    "pe_wt_v",
    "bel_bias",
    "bel_bias_v",
    "pe_add",
    "pe_add_v",
    "bel_noise",
)

os.makedirs(SIM_OUT_DIR, exist_ok=True)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=(
            "Simulate act/intent/confirm belief models from Free confidence fits, "
            f"pooling {', '.join(EXPERIMENTS)} into one cohort by default."
        )
    )
    ap.add_argument(
        "--experiments",
        nargs="+",
        default=list(EXPERIMENTS),
        help=f"Experiments to pool into one simulated cohort (default: {list(EXPERIMENTS)}).",
    )
    ap.add_argument(
        "--fit-tag",
        default=DEFAULT_FIT_TAG,
        help=(
            "Free confidence-fit tag; resolves to "
            f"{FITS_CONF_DIR}/<exp>/results_{CONDITION}_<fit-tag>.csv per experiment "
            f"(default: {DEFAULT_FIT_TAG!r})."
        ),
    )
    ap.add_argument(
        "--mode",
        choices=("forward", "mc"),
        default="mc",
        help=(
            "mc (default): expected_confidence's MC E[confidence] "
            "(conditional mean for Free, plain mean for Observed). "
            "forward: one forward draw per trial via simulate_act_conf -- actual "
            "choices for Free trials, pRightObs-drawn actions for Observed."
        ),
    )
    ap.add_argument(
        "--n-mc",
        type=int,
        default=DEFAULT_N_MC,
        help="Monte Carlo samples used by expected_confidence when --mode mc.",
    )
    ap.add_argument(
        "--out-dir",
        default=SIM_OUT_DIR,
        help=f"Directory for sims_{{act,intent,confirm}}.csv (default: {SIM_OUT_DIR}).",
    )
    ap.add_argument(
        "--mismatch-gate-baseline",
        type=int,
        nargs="+",
        choices=(0, 1),
        default=(1,),
        help=(
            "Which mismatch_gate_baseline value(s) to simulate (default: 1 only; "
            "one full sims_{act,intent,confirm}[.suffix].csv set per value). "
            "1: a mismatch trial's mismatch_coef rescaling also applies to the "
            "baseline (non-incentive) pe_wt/pe_add/bel_bias, i.e. the baseline "
            "bias is itself agency-dependent; written to sims_{act,intent,confirm}.csv. "
            "0: mismatch_coef only rescales the incentive-linked terms, leaving "
            "baseline weighting/bias untouched by mismatch; written to "
            "sims_{act,intent,confirm}_nogatebase.csv instead. This choice isn't "
            "identifiable from Free-choice fitting (mismatch never fires there), "
            "so it's a simulation-time-only assumption."
        ),
    )
    return ap.parse_args()


def load_conf_fit_table(conf_path: Path) -> tuple[pd.DataFrame, list[str]]:
    """Load a confidence fit CSV → DataFrame with participant + present conf params."""
    df = pd.read_csv(conf_path)
    if "participant" not in df.columns:
        raise ValueError(f"{conf_path}: missing 'participant' column")
    present = [p for p in KNOWN_CONF_PARAMS if p in df.columns]
    if not present:
        raise ValueError(
            f"{conf_path}: no known conf params among columns {list(df.columns)}; "
            f"expected any of {KNOWN_CONF_PARAMS}"
        )
    out = df[["participant"] + present].copy()
    out["participant"] = out["participant"].astype(int)
    return out, present


def align_conf_to_cohort(
    conf_df: pd.DataFrame,
    present: list[str],
    participants: np.ndarray,
) -> dict[str, np.ndarray]:
    """Per-participant arrays in choice-cohort order; absent params → 0."""
    by_pid = conf_df.set_index("participant")
    n = len(participants)
    out: dict[str, np.ndarray] = {p: np.zeros(n, dtype=float) for p in KNOWN_CONF_PARAMS}
    for i, pid in enumerate(participants):
        pid = int(pid)
        if pid not in by_pid.index:
            raise KeyError(f"Participant {pid} missing from confidence fit")
        row = by_pid.loc[pid]
        if isinstance(row, pd.DataFrame):
            row = row.iloc[0]
        for p in present:
            out[p][i] = float(row[p])
    return out


def synthetic_design_df() -> pd.DataFrame:
    return pd.DataFrame({"stim": s, "incentive": inc})


def empirical_free_trials(exp: str, participant: int, exp_data: pd.DataFrame) -> pd.DataFrame:
    """Free trials with stim, incentive, and the participant's actual choice (a)."""
    df = exp_data[
        (exp_data["participant"] == participant) & (exp_data["choiceType"] == "Free")
    ]
    if df.empty:
        raise ValueError(f"No Free trials with confidence for {exp} participant {participant}")
    out = df[["stim", "incentive", "a", "correct"]].copy()
    out["correct"] = out["correct"].astype(int)
    return out.reset_index(drop=True)


def sim_observed_action(stim: np.ndarray, pRight: list[float]) -> tuple[np.ndarray, np.ndarray]:
    p = np.array([np.interp(v, sLevels, pRight) for v in stim])
    a = np.random.binomial(1, p)
    a = 2 * a - 1
    return a, p


def _seed_for(sim_index: int, model_index: int, choice_type: str) -> int:
    base = 42 + int(sim_index) * 1_009 + int(model_index) * 100_003
    if choice_type == "Observed":
        base += 7
    return base % (2**32 - 1)


def simulate_forward(
    df_trials: pd.DataFrame,
    pardict: dict,
    *,
    choice_type: str,
) -> pd.DataFrame:
    """Default mode: one forward (action, confidence) draw per trial via
    simulate_act_conf. Free trials already carry the participant's actual
    choice (see empirical_free_trials), so simulate_act_conf takes it as
    given and draws confidence fresh; Observed trials get an action drawn
    from the population psychometric curve (pRightObs) below."""
    df = df_trials.copy()
    pdct = dict(pardict)
    if choice_type == "Free":
        pdct["mismatch_coef"] = 0.0
    if choice_type == "Observed":
        a, _ = sim_observed_action(df["stim"].to_numpy(dtype=float), pRightObs)
        df["a"] = a
    return simulate_act_conf(df, pdct)


def simulate_mc(
    df_trials: pd.DataFrame,
    pardict: dict,
    *,
    choice_type: str,
    n_mc: int,
    seed: int,
) -> pd.DataFrame:
    """
    Free: actual choices from data; confidence = expected_confidence's MC
    E[confidence | a] conditioned on the observed action (condition_is_free=True).

    Observed: population-psychometric action (pRightObs); confidence = plain
    MC mean (condition_is_free=False). Free fits use mismatch_coef=0;
    Observed uses the model's mismatch_coef.
    """
    pdct = dict(pardict)
    if choice_type == "Free":
        pdct["mismatch_coef"] = 0.0

    df = df_trials.copy()
    if choice_type == "Observed":
        # sim_observed_action draws on the global np.random state (unseeded by
        # default), so without this save/seed/restore the synthetic Observed
        # action -- and everything downstream of it (mismatch, confidence,
        # every Non-Free statistic) -- is a fresh coin flip on every run.
        rng_state = np.random.get_state()
        np.random.seed(seed)
        a, _ = sim_observed_action(df["stim"].to_numpy(dtype=float), pRightObs)
        np.random.set_state(rng_state)
        df["a"] = a
    elif "a" not in df.columns:
        rng_state = np.random.get_state()
        np.random.seed(seed)
        act = simulate_act_conf(df[["stim", "incentive"]], pdct)
        np.random.set_state(rng_state)
        df["a"] = act["a"].to_numpy(dtype=float)

    conf = expected_confidence(
        df,
        pdct,
        condition_is_free=(choice_type == "Free"),
        n_mc=n_mc,
        seed=seed,
    )

    conf = np.round(conf,0).clip(0,100) 

    out = df.copy()
    out["a"] = df["a"].to_numpy(dtype=float)
    out["conf"] = conf
    if choice_type == "Free" and "correct" in df_trials.columns:
        out["correct"] = df_trials["correct"].astype(int).to_numpy()
    else:
        out["correct"] = (np.sign(out["a"]) == np.sign(out["stim"])).astype(int)
    return out


def trial_design_for_subject(
    participant: int,
    choice_type: str,
    *,
    exp: str,
    exp_data: pd.DataFrame,
) -> pd.DataFrame:
    if choice_type == "Free":
        return empirical_free_trials(exp, participant, exp_data)
    return synthetic_design_df()


def _pardict_for_subject(
    *,
    mismatch_coef: float,
    mismatch_gate_baseline: bool,
    pars_choice: np.ndarray,
    conf_fitted: dict[str, np.ndarray],
    present: list[str],
    nsub: int,
) -> dict:
    """Build pardict: present fit params + explicit 0 for other known conf params."""
    pardict: dict = {
        "mismatch_coef": float(mismatch_coef),
        "mismatch_gate_baseline": float(mismatch_gate_baseline),
        "sens_noise": float(pars_choice[0]),
        "sens_bias": float(pars_choice[1]),
        "p_lapse": float(pars_choice[2]),
    }
    # Explicit zeros first so missing fit columns never inherit leftovers.
    for p in KNOWN_CONF_PARAMS:
        pardict[p] = 0.0
    for p in present:
        pardict[p] = float(conf_fitted[p][nsub])
    return pardict


def load_cohort(
    experiments: list[str],
    fit_tag: str,
) -> tuple[list[tuple[str, int]], np.ndarray, dict[str, np.ndarray], list[str], dict[str, pd.DataFrame]]:
    """Pool per-experiment Free conf + choice fits into one cohort, in experiment order.

    Returns (cohort, pars, conf_fitted, present, exp_data_cache):
      - cohort: [(exp, participant_id), ...], the canonical subject order used
        everywhere below (pars/conf_fitted rows and the output "participant"
        re-index all line up with this).
      - pars: (n, 3) sens_noise/sens_bias/p_lapse, one row per cohort entry.
      - conf_fitted: {param: (n,) array}, one row per cohort entry; a param
        absent from a given experiment's fit is 0 for that experiment's rows.
      - present: KNOWN_CONF_PARAMS actually present in at least one experiment's fit.
      - exp_data_cache: {exp: trial dataframe}, for Free trial lookups later.
    """
    cohort: list[tuple[str, int]] = []
    pars_chunks: list[np.ndarray] = []
    conf_chunks: dict[str, list[np.ndarray]] = {p: [] for p in KNOWN_CONF_PARAMS}
    present_union: set[str] = set()
    exp_data_cache: dict[str, pd.DataFrame] = {}

    for exp in experiments:
        conf_path = Path(FITS_CONF_DIR) / exp / f"results_{CONDITION}_{fit_tag}.csv"
        if not conf_path.is_file():
            raise FileNotFoundError(conf_path)
        # Sidecar metadata must exist next to the fit CSV (sanity check that the
        # fit completed properly); its contents aren't otherwise needed here.
        metadata_path = conf_path.parent / f"{conf_path.stem}.metadata.json"
        if not metadata_path.is_file():
            raise FileNotFoundError(f"Metadata not found: {metadata_path}")

        choice_path = Path(CHOICE_ROOT) / exp / f"results_{CONDITION}.csv"
        if not choice_path.is_file():
            raise FileNotFoundError(f"Choice fit not found: {choice_path}")

        conf_df, present = load_conf_fit_table(conf_path)
        present_union.update(present)

        choice_df = pd.read_csv(choice_path)
        if "participant" not in choice_df.columns:
            raise ValueError(f"{choice_path}: missing 'participant' column")
        participants = np.asarray(choice_df["participant"].unique(), dtype=int)
        participants.sort()

        pars_exp = np.zeros((len(participants), 3), dtype=float)
        for i, pid in enumerate(participants):
            row = choice_df[choice_df["participant"] == pid].iloc[0]
            pars_exp[i] = [row["sens_noise"], row["sens_bias"], row["p_lapse"]]
        pars_chunks.append(pars_exp)

        conf_fitted_exp = align_conf_to_cohort(conf_df, present, participants)
        for p in KNOWN_CONF_PARAMS:
            conf_chunks[p].append(conf_fitted_exp[p])

        exp_data_cache[exp] = load_exp_df(exp)
        cohort.extend((exp, int(pid)) for pid in participants)

        print(f"Conf fit: {conf_path}  (n={len(participants)})", flush=True)
        print(f"  choice fit: {choice_path}", flush=True)
        print(f"  params from fit: {present}", flush=True)

    present = [p for p in KNOWN_CONF_PARAMS if p in present_union]
    pars = np.concatenate(pars_chunks, axis=0)
    conf_fitted = {p: np.concatenate(conf_chunks[p], axis=0) for p in KNOWN_CONF_PARAMS}
    return cohort, pars, conf_fitted, present, exp_data_cache


def main() -> None:
    args = parse_args()
    experiments = list(dict.fromkeys(args.experiments))  # dedupe, preserve order
    fit_tag = args.fit_tag

    cohort, pars, conf_fitted, present, exp_data_cache = load_cohort(experiments, fit_tag)

    print(f"Experiments: {experiments}  fit_tag={fit_tag!r}  total n={len(cohort)}", flush=True)
    for p in present:
        vals = conf_fitted[p]
        print(f"  {p}: mean={vals.mean():.4g}  sd={vals.std():.4g}", flush=True)
    absent = [p for p in KNOWN_CONF_PARAMS if p not in present]
    if absent:
        print(f"  absent (set to 0): {absent}", flush=True)

    mode = args.mode
    n_mc = int(args.n_mc)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # Dedupe while preserving order (argparse won't collapse "--mismatch-gate-baseline 1 1").
    gate_values = list(dict.fromkeys(int(v) for v in args.mismatch_gate_baseline))

    model_names = ["act", "intent", "confirm"]
    mismatch_coefs = [1.0, -1.0, 0.0]

    if mode == "forward":
        np.random.seed(42)

    print(
        f"Simulation mode: {mode}"
        + (f" (n_mc={n_mc}, Free uses actual choices)" if mode == "mc" else "")
        + f"; mismatch_gate_baseline values: {gate_values}",
        flush=True,
    )

    for gate_value in gate_values:
        mismatch_gate_baseline = bool(gate_value)
        # Keep sims_{act,intent,confirm}.csv unchanged for gate=1, since
        # stats_avg.py hardcodes those filenames; the gate=0 variant is a
        # separate, additional simulation-time assumption (see
        # --mismatch-gate-baseline help), not a replacement.
        out_suffix = "" if mismatch_gate_baseline else "_nogatebase"

        for imod, mismatch_coef in enumerate(mismatch_coefs):
            df_sim_mod = pd.DataFrame()
            for nsub, (exp, pid) in enumerate(cohort):
                exp_data = exp_data_cache[exp]

                pardict = _pardict_for_subject(
                    mismatch_coef=mismatch_coef,
                    mismatch_gate_baseline=mismatch_gate_baseline,
                    pars_choice=pars[nsub],
                    conf_fitted=conf_fitted,
                    present=present,
                    nsub=nsub,
                )

                for choice_type in ("Free", "Observed"):
                    df_trials = trial_design_for_subject(
                        pid, choice_type, exp=exp, exp_data=exp_data,
                    )
                    seed = _seed_for(nsub, imod, choice_type)
                    if mode == "forward":
                        df_sim_sub = simulate_forward(df_trials, pardict, choice_type=choice_type)
                    else:
                        df_sim_sub = simulate_mc(
                            df_trials,
                            pardict,
                            choice_type=choice_type,
                            n_mc=n_mc,
                            seed=seed,
                        )
                    df_sim_sub["conf"] = np.round(df_sim_sub["conf"]) #round to intger in [0,100]
                    df_sim_sub["participant"] = nsub + 1
                    df_sim_sub["choiceType"] = choice_type
                    df_sim_mod = pd.concat([df_sim_mod, df_sim_sub], ignore_index=True)

            df_sim_mod["coh"] = np.abs(df_sim_mod["stim"])
            out_path = out_dir / f"sims_{model_names[imod]}{out_suffix}.csv"
            df_sim_mod.to_csv(out_path, index=False)
            n_free = int((df_sim_mod["choiceType"] == "Free").sum())
            n_obs = int((df_sim_mod["choiceType"] == "Observed").sum())
            print(
                f"Wrote {out_path} ({n_free} Free + {n_obs} Observed trials, "
                f"mode={mode}, mismatch_gate_baseline={gate_value})",
                flush=True,
            )


if __name__ == "__main__":
    main()
