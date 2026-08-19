# -*- coding: utf-8 -*-
"""Shared simulate → cross-fit → record engine for confidence-model recovery.

Supports the Free, Replayed, and Observed_Forced conditions (used for the
paper's Free recovery via ``scripts/recover_free.py``). Identifiability is
the full cross-fit; parameter recovery is the diagonal
``generative_model == fitted_model``.

Condition recipes:
- Free: two-step. Stage 1 fits (sens_noise, sens_bias, p_lapse) once per
  simulated dataset; stage 2 fixes those and fits each confidence variant
  with ``conf_ll.conf_ll_binned`` (``condition_is_free=True``).
- Replayed: same two-step structure and likelihood, but
  ``condition_is_free=False`` (action given at confidence time).
- Observed_Forced: single-step. Actions are external (drawn from a P(right |
  signed coherence) table), so sens_noise/sens_bias/p_lapse are fit jointly
  with confidence params. bel_noise is fixed at 0 unless the variant's
  parnames include it.

Generative truth is always drawn from priors (not empirical fits).

For a distribution over group BMC outcomes, run one cross-fit then
bootstrap-resample participants via
``analysis_free.bootstrap_model_comparison_bmc`` (see
``scripts/analyze_recovery_identifiability.py``).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from motivbelief.modeling.conf_ll import (
    make_conf_modelinfo,
    fit_conf_bads,
    simulate_act_conf,
    simulate_replayed_act_conf,
)
from motivbelief.modeling.optimize import (
    fit_model_LBFGS,
    DEFAULT_CONF_PRIORS,
    draw_from_prior,
    log_prior,
)
from motivbelief.modeling.choice import psychofun_ll

CONDITIONS = ("Free", "Replayed", "Observed_Forced")

# -----------------------------------------------------------------------
# Trial design
# -----------------------------------------------------------------------
S_LEVELS = np.array([-38.0, -9.0, -5.0, -3.0, -1.0, 1.0, 3.0, 5.0, 9.0, 38.0])
P_RIGHT_OBS = np.array(
    [0.0308, 0.1675, 0.2842, 0.34, 0.4496, 0.5504, 0.66, 0.7158, 0.8325, 0.9692]
)
INCENTIVES = [-1.0, 0.0, 1.0]
N_REPS = 8  # 10 signed levels * 3 incentives * 8 reps = 240 trials/participant


def make_trial_design(rng: np.random.Generator) -> pd.DataFrame:
    levels = np.tile(S_LEVELS, len(INCENTIVES) * N_REPS)
    incs = np.repeat(INCENTIVES, len(S_LEVELS) * N_REPS)
    df = pd.DataFrame({"stim": levels, "incentive": incs})
    idx = rng.permutation(len(df))
    return df.iloc[idx].reset_index(drop=True)


def sample_truth_for_parnames(rng: np.random.Generator, parnames: list[str], modelinfo: dict) -> dict:
    """Sample generative truth from DEFAULT_CONF_PRIORS, clipped to hard bounds."""
    truth = {}
    for i, name in enumerate(parnames):
        lb, ub = modelinfo["bounds"][0][i], modelinfo["bounds"][1][i]
        spec = DEFAULT_CONF_PRIORS.get(name)
        if spec is None:
            val = rng.uniform(modelinfo["plb"][i], modelinfo["pub"][i])
        else:
            val = draw_from_prior(spec, rng)
        truth[name] = float(np.clip(val, lb, ub))
    return truth


# -----------------------------------------------------------------------
# Model / sub-model variant spec
# -----------------------------------------------------------------------
@dataclass(frozen=True)
class ModelVariant:
    """One candidate confidence-stage model (free params + fixedpars)."""

    name: str
    parnames: list[str]
    fixedpars: dict = field(default_factory=dict)
    bounds_overrides: dict = field(default_factory=dict)  # name -> (plb, pub, lb, ub, x0)

    def modelinfo(self) -> dict:
        mi = make_conf_modelinfo(self.parnames)
        mi["cfg"]["fixedpars"] = dict(self.fixedpars)
        mi["verbose"] = False
        for pname, (plb, pub, lb, ub, x0) in self.bounds_overrides.items():
            i = self.parnames.index(pname)
            mi["plb"][i], mi["pub"][i] = plb, pub
            mi["bounds"][0][i], mi["bounds"][1][i] = lb, ub
            mi["x0"][i] = x0
        return mi


# -----------------------------------------------------------------------
# Choice-stage fit (Free / Replayed stage 1)
# -----------------------------------------------------------------------
CHOICE_PARNAMES = ["sens_noise", "sens_bias", "p_lapse"]
CHOICE_PRIOR_KEYS = {"sens_noise": "sens_noise", "sens_bias": "sens_bias", "p_lapse": "p_lapse"}
CHOICE_MODELINFO_TEMPLATE = {
    "plb": [1, -5, 0.01],
    "pub": [10, 5, 0.05],
    "bounds": [[0.5, -10, 0.0], [30, 10, 0.1]],
    "x0": [1, 0, 0.01],
    "myfun": None,  # set below after psychofun_ll_with_prior
    "cfg": {"parnames": CHOICE_PARNAMES, "fixedpars": {}},
    "options": {},
    "verbose": False,
}


def choice_log_prior(pardict: dict) -> float:
    renamed = {prior_key: pardict[name] for name, prior_key in CHOICE_PRIOR_KEYS.items()}
    priors = {key: DEFAULT_CONF_PRIORS[key] for key in CHOICE_PRIOR_KEYS.values()}
    return log_prior(renamed, list(CHOICE_PRIOR_KEYS.values()), priors)


def psychofun_ll_with_prior(params: np.ndarray, df: pd.DataFrame, cfg: dict) -> float:
    ll = psychofun_ll(params, df, cfg)
    if not np.isfinite(ll):
        return -np.inf
    pardict = dict(zip(cfg["parnames"], params))
    pardict.update(cfg.get("fixedpars", {}))
    lp = choice_log_prior(pardict)
    return float(ll + lp) if np.isfinite(lp) else -np.inf


CHOICE_MODELINFO_TEMPLATE["myfun"] = psychofun_ll_with_prior


def sample_choice_stage_truth(rng: np.random.Generator) -> dict:
    truth = {}
    for i, name in enumerate(CHOICE_PARNAMES):
        spec = DEFAULT_CONF_PRIORS[CHOICE_PRIOR_KEYS[name]]
        val = draw_from_prior(spec, rng)
        lb, ub = CHOICE_MODELINFO_TEMPLATE["bounds"][0][i], CHOICE_MODELINFO_TEMPLATE["bounds"][1][i]
        truth[name] = float(np.clip(val, lb, ub))
    return truth


def fit_choice_stage(dfsub: pd.DataFrame, seed: int, *, n_restarts: int = 5) -> dict[str, float]:
    x_hat, _ll, _info = fit_model_LBFGS(
        CHOICE_MODELINFO_TEMPLATE, dfsub, n_restarts=n_restarts, seed=seed, n_jobs=n_restarts,
    )
    return dict(zip(CHOICE_PARNAMES, x_hat))


# -----------------------------------------------------------------------
# Per-condition simulate+truth and fit recipes
# -----------------------------------------------------------------------
def _simulate_and_truth_free(rng: np.random.Generator, df_trials: pd.DataFrame, variant: ModelVariant, seed: int):
    choice_truth = sample_choice_stage_truth(rng)
    conf_modelinfo = variant.modelinfo()
    conf_truth = sample_truth_for_parnames(rng, conf_modelinfo["cfg"]["parnames"], conf_modelinfo)
    pardict = {
        "sens_noise": choice_truth["sens_noise"], "sens_bias": choice_truth["sens_bias"],
        "p_lapse": choice_truth["p_lapse"], **conf_truth, **variant.fixedpars,
    }
    df_sim = simulate_act_conf(df_trials, pardict, rng=np.random.default_rng(seed))
    df_sim["conf"] = df_sim["conf"].round()
    truth = {"sens_noise": pardict["sens_noise"], "sens_bias": pardict["sens_bias"], "p_lapse": pardict["p_lapse"], **conf_truth}
    return df_sim, truth


def _simulate_and_truth_replayed(rng: np.random.Generator, df_trials: pd.DataFrame, variant: ModelVariant, seed: int):
    choice_truth = sample_choice_stage_truth(rng)
    conf_modelinfo = variant.modelinfo()
    conf_truth = sample_truth_for_parnames(rng, conf_modelinfo["cfg"]["parnames"], conf_modelinfo)
    pardict = {
        "sens_noise": choice_truth["sens_noise"], "sens_bias": choice_truth["sens_bias"],
        "p_lapse": choice_truth["p_lapse"], **conf_truth, **variant.fixedpars,
    }
    df_sim = simulate_replayed_act_conf(df_trials, pardict, rng=np.random.default_rng(seed))
    truth = {"sens_noise": pardict["sens_noise"], "sens_bias": pardict["sens_bias"], "p_lapse": pardict["p_lapse"], **conf_truth}
    return df_sim, truth


def _simulate_and_truth_observed_forced(rng: np.random.Generator, df_trials: pd.DataFrame, variant: ModelVariant, seed: int):
    modelinfo = variant.modelinfo()
    parnames = modelinfo["cfg"]["parnames"]
    truth = sample_truth_for_parnames(rng, parnames, modelinfo)
    # Fix bel_noise at 0 unless the variant opts in by including it in parnames.
    bel_noise_default = {} if "bel_noise" in parnames else {"bel_noise": 0.0}
    pardict = {**truth, **bel_noise_default, **variant.fixedpars}

    level_to_p = dict(zip(S_LEVELS, P_RIGHT_OBS))
    p_right = df_trials["stim"].map(level_to_p).to_numpy(dtype=float)
    u = rng.random(len(df_trials))
    df_a = df_trials.copy()
    df_a["a"] = np.where(u < p_right, 1.0, -1.0)

    df_sim = simulate_act_conf(df_a, pardict, rng=np.random.default_rng(seed))
    return df_sim, truth


def _fit_free(
    df_sim: pd.DataFrame, variant: ModelVariant, seed: int, *,
    est_choice: dict[str, float],
    n_mc: int, n_restarts: int, n_jobs: int, kernel_bw: float,
    max_fun_evals: int = 500, priors: dict | None = None,
) -> dict:
    modelinfo = variant.modelinfo()
    x_hat, ll_hat = fit_conf_bads(
        modelinfo, df_sim[["stim", "a", "conf", "incentive"]],
        sens_noise=est_choice["sens_noise"], sens_bias=est_choice["sens_bias"],
        p_lapse=est_choice["p_lapse"], condition_is_free=True,
        n_mc=n_mc, kernel_bw=kernel_bw, seed=seed, n_restarts=n_restarts, n_jobs=n_jobs,
        max_fun_evals=max_fun_evals, priors=priors,
    )
    recovered = dict(zip(modelinfo["cfg"]["parnames"], x_hat))
    recovered.update({
        "sens_noise": est_choice["sens_noise"], "sens_bias": est_choice["sens_bias"],
        "p_lapse": est_choice["p_lapse"],
    })
    return {
        "recovered": recovered, "ll": float(ll_hat),
        "n_trials": len(df_sim), "n_params": len(modelinfo["cfg"]["parnames"]),
    }


def _fit_replayed(
    df_sim: pd.DataFrame, variant: ModelVariant, seed: int, *,
    est_choice: dict[str, float],
    n_mc: int, n_restarts: int, n_jobs: int, kernel_bw: float,
    max_fun_evals: int = 500, priors: dict | None = None,
) -> dict:
    modelinfo = variant.modelinfo()
    x_hat, ll_hat = fit_conf_bads(
        modelinfo, df_sim[["stim", "a", "conf", "incentive"]],
        sens_noise=est_choice["sens_noise"], sens_bias=est_choice["sens_bias"],
        p_lapse=est_choice["p_lapse"], condition_is_free=False,
        n_mc=n_mc, kernel_bw=kernel_bw, seed=seed, n_restarts=n_restarts, n_jobs=n_jobs,
        max_fun_evals=max_fun_evals, priors=priors,
    )
    recovered = dict(zip(modelinfo["cfg"]["parnames"], x_hat))
    recovered.update({
        "sens_noise": est_choice["sens_noise"], "sens_bias": est_choice["sens_bias"],
        "p_lapse": est_choice["p_lapse"],
    })
    return {
        "recovered": recovered, "ll": float(ll_hat),
        "n_trials": len(df_sim), "n_params": len(modelinfo["cfg"]["parnames"]),
    }


def _fit_observed_forced(
    df_sim: pd.DataFrame, variant: ModelVariant, seed: int, *,
    n_mc: int, n_restarts: int, n_jobs: int, kernel_bw: float,
    max_fun_evals: int = 500, priors: dict | None = None,
) -> dict:
    modelinfo = variant.modelinfo()
    if "bel_noise" not in modelinfo["cfg"]["parnames"]:
        modelinfo["cfg"]["fixedpars"] = {**modelinfo["cfg"]["fixedpars"], "bel_noise": 0.0}
    x_hat, ll_hat = fit_conf_bads(
        modelinfo, df_sim[["stim", "a", "conf", "incentive"]],
        sens_noise=0.0, sens_bias=0.0, p_lapse=0.0,  # ignored: free via parnames
        condition_is_free=False,
        n_mc=n_mc, kernel_bw=kernel_bw, seed=seed, n_restarts=n_restarts, n_jobs=n_jobs,
        max_fun_evals=max_fun_evals, priors=priors,
    )
    recovered = dict(zip(modelinfo["cfg"]["parnames"], x_hat))
    return {
        "recovered": recovered, "ll": float(ll_hat),
        "n_trials": len(df_sim), "n_params": len(modelinfo["cfg"]["parnames"]),
    }


_SIMULATE_TRUTH = {
    "Free": _simulate_and_truth_free,
    "Replayed": _simulate_and_truth_replayed,
    "Observed_Forced": _simulate_and_truth_observed_forced,
}
_FIT = {
    "Free": _fit_free,
    "Replayed": _fit_replayed,
    "Observed_Forced": _fit_observed_forced,
}


# -----------------------------------------------------------------------
# Cross-fit engine
# -----------------------------------------------------------------------
def run_cross_fit(
    condition: str,
    gen_variants: list[ModelVariant],
    fit_variants: list[ModelVariant],
    n_participants: int,
    seed0: int,
    *,
    n_mc: int = 500,
    n_restarts: int = 5,
    n_jobs: int = 5,
    kernel_bw: float = 5.0,
    max_fun_evals: int = 500,
    priors: dict | None = None,
) -> pd.DataFrame:
    """Simulate ``n_participants`` per generative variant; fit each with every fit variant.

    Diagonal rows (``generative_model == fitted_model``) are the parameter-recovery table.

    ``priors``: fitting-time regularization only (passed to ``fit_conf_bads``;
    ``None`` → ``optimize.DEFAULT_CONF_PRIORS``). Does not affect generative truth,
    which always draws from ``DEFAULT_CONF_PRIORS``.

    For a distribution over group BMC outcomes, bootstrap-resample participants
    from the returned table (``analysis_free.bootstrap_model_comparison_bmc``).
    """
    if condition not in _SIMULATE_TRUTH:
        raise ValueError(f"Unknown condition {condition!r}; expected one of {CONDITIONS}")
    simulate_truth_fn = _SIMULATE_TRUTH[condition]
    fit_fn = _FIT[condition]

    rows = []
    for p in range(n_participants):
        seed = seed0 + p
        rng = np.random.default_rng(seed)
        df_trials = make_trial_design(rng)

        for gen_variant in gen_variants:
            df_sim, truth = simulate_truth_fn(rng, df_trials, gen_variant, seed)

            # Choice stage is shared across fitted conf variants (same data + model).
            fit_kwargs: dict = {
                "n_mc": n_mc, "n_restarts": n_restarts, "n_jobs": n_jobs,
                "kernel_bw": kernel_bw, "max_fun_evals": max_fun_evals, "priors": priors,
            }
            if condition in ("Free", "Replayed"):
                fit_kwargs["est_choice"] = fit_choice_stage(
                    df_sim[["stim", "a"]], seed=seed, n_restarts=n_restarts,
                )

            for fit_variant in fit_variants:
                t0 = time.perf_counter()
                fit_out = fit_fn(df_sim, fit_variant, seed, **fit_kwargs)
                dt = time.perf_counter() - t0

                row = {
                    "participant": p,
                    "generative_model": gen_variant.name,
                    "fitted_model": fit_variant.name,
                    "ll": fit_out["ll"],
                    "n_trials": fit_out["n_trials"],
                    "n_params": fit_out["n_params"],
                    "fit_time_s": dt,
                }
                row.update({f"true_{k}": v for k, v in truth.items()})
                row.update({f"hat_{k}": v for k, v in fit_out["recovered"].items()})
                rows.append(row)
                print(
                    f"[{condition}] participant {p + 1}/{n_participants}  "
                    f"gen={gen_variant.name} fit={fit_variant.name}  "
                    f"ll={fit_out['ll']:.1f}  ({dt:.1f}s)"
                )
                keys = list(truth.keys())
                recovered = fit_out["recovered"]
                truth_str = "  ".join(f"{k}={truth[k]:.3f}" for k in keys)
                recovered_str = "  ".join(f"{k}={recovered[k]:.3f}" for k in keys if k in recovered)
                print(f"    truth:     {truth_str}")
                print(f"    recovered: {recovered_str}")
    return pd.DataFrame(rows)


def classification_accuracy(df: pd.DataFrame, *, ic_col: str = "aicc") -> pd.DataFrame:
    """Per-participant best-IC model vs generative model (confusion matrix)."""
    best = (
        df.sort_values(ic_col)
        .groupby(["participant", "generative_model"], as_index=False)
        .first()[["participant", "generative_model", "fitted_model"]]
        .rename(columns={"fitted_model": "predicted_model"})
    )
    confusion = best.groupby(["generative_model", "predicted_model"]).size().rename("n").reset_index()
    totals = best.groupby("generative_model").size().rename("n_total")
    confusion = confusion.merge(totals, on="generative_model")
    confusion["fraction"] = confusion["n"] / confusion["n_total"]
    return confusion


def add_aicc(df: pd.DataFrame) -> pd.DataFrame:
    """Attach BIC/AICc via ``analysis_free.compute_information_criteria``."""
    from motivbelief.modeling.analysis_free import compute_information_criteria

    return compute_information_criteria(df, ll_col="ll", n_col="n_trials", k_col="n_params")


def correlation_block(df: pd.DataFrame, params: list[str]) -> pd.DataFrame:
    """True(rows) × Recovered(cols) correlation sub-matrix."""
    true_cols = [f"true_{p}" for p in params]
    hat_cols = [f"hat_{p}" for p in params]
    full = df[true_cols + hat_cols].corr()
    block = full.loc[true_cols, hat_cols]
    block.index = params
    block.columns = params
    return block
