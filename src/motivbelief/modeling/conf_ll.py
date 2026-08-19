"""Confidence log-likelihood (binned joint-simulation) and BADS fitting.

Generative model: :mod:`motivbelief.modeling.conf_core`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d

from motivbelief.modeling.conf_core import (
    MC_DTYPE,
    _stim_channels,
    _trial_arrays,
    confidence_core,
    resolve_params,
    simulate_joint_conf,
)
from motivbelief.modeling.optimize import (
    DEFAULT_CONF_PARAM_BOUNDS,
    DEFAULT_CONF_PRIORS,
    fit_model_BADS,
    log_prior,
)

# Re-exports for callers that historically imported simulate / predict from conf_ll.
from motivbelief.modeling.conf_core import (  # noqa: F401
    expected_confidence,
    simulate_act_conf,
    simulate_replayed_act_conf,
)


DEFAULT_BIN_PAD = 1.0  # fixed pseudo-count per fine bin, NOT divided by n_mc
N_RATING_BINS = 101  # confidence ratings recorded/rounded to whole percentage points, 0..100
GAUSS_TRUNCATE = 4.0  # scipy gaussian_filter1d radius = truncate * sigma


def _params_to_pardict(params: np.ndarray, cfg: dict) -> dict:
    pardict: dict = {}
    for npar, ipar in enumerate(cfg["parnames"]):
        pardict[ipar] = float(params[npar])
    for key, value in cfg.get("fixedpars", {}).items():
        pardict[key] = value if isinstance(value, str) else (float(value) if np.isscalar(value) else value)
    return pardict


# ---------------------------------------------------------------------------
# Joint-simulation likelihood (default for both Free and non-free)
# ---------------------------------------------------------------------------
#
# Forward-simulate choice AND confidence together from the same evidence draw
# and score trials off a padded, Gaussian-smoothed per-condition histogram
# table. Faster than pointwise MC kernel scoring and robust for Free rare
# choice/confidence combinations.


def _gaussian_smooth_rating(counts: np.ndarray, sigma: float) -> np.ndarray:
    """Gaussian-smooth along the rating axis (last axis).

    ``sigma`` is in rating-bin units (1 bin = 1 percentage point). Edges use
    zero padding (no mass below 0 or above 100); callers should self-normalize
    afterward so truncated edge mass stays on the valid bins.
    """
    sig = float(sigma)
    if not np.isfinite(sig) or sig <= 0.0:
        return np.asarray(counts, dtype=np.float64)
    return gaussian_filter1d(
        counts,
        sigma=sig,
        axis=-1,
        mode="constant",
        cval=0.0,
        truncate=GAUSS_TRUNCATE,
    )


def _joint_conf_histogram_density(
    a_sim: np.ndarray,
    conf_sim: np.ndarray,
    *,
    kernel_bw: float,
    bin_pad: float,
) -> np.ndarray:
    """Padded, Gaussian-smoothed P(a, rating) table from joint draws.

    ``a_sim``/``conf_sim``: shape ``(n_cond, n_mc)``, as returned by
    :func:`simulate_joint_conf`. ``kernel_bw`` is the Gaussian σ on the
    0–100 rating scale. Returns a proper joint PMF, shape
    ``(n_cond, 2, N_RATING_BINS)`` (index 0 -> a<=0, index 1 -> a>0), summing
    to 1 over the 2*101 cells for each condition. For non-free conditions
    (fixed ``a`` per row), one of the two action slots just ends up with
    ~all the mass -- harmless, and lets :func:`conf_ll_binned` use the same
    lookup either way.
    """
    n_cond, n_mc = a_sim.shape
    n_bins = N_RATING_BINS

    bin_idx = np.clip(np.round(conf_sim), 0, n_bins - 1).astype(np.int64)
    action_idx = (a_sim > 0.0).astype(np.int64)
    cond_row = np.arange(n_cond, dtype=np.int64)[:, None]
    flat = (cond_row * 2 + action_idx) * n_bins + bin_idx
    counts = np.bincount(flat.ravel(), minlength=n_cond * 2 * n_bins).astype(np.float64)
    counts = counts.reshape(n_cond, 2, n_bins)

    counts = counts + float(bin_pad)  # fixed pseudo-count per fine bin, before smoothing, not scaled by n_mc

    smoothed = _gaussian_smooth_rating(counts, float(kernel_bw))

    # Self-normalize (rather than divide by a fixed n_total*kernel constant):
    # zero-pad truncation near rating 0/100 means edge bins see a short
    # kernel, so a fixed normalizer would silently lose that mass instead of
    # it staying concentrated on the valid bins.
    return smoothed / smoothed.sum(axis=(1, 2), keepdims=True)


def prepare_conf_ll_data_binned(
    df: pd.DataFrame,
    *,
    n_mc: int,
    seed: int,
    condition_is_free: bool,
    kernel_bw: float = 5.0,
    pad: float = DEFAULT_BIN_PAD,
    stimcol: str = "stim",
    confcol: str = "conf",
    choicecol: str = "a",
) -> dict:
    """Per-participant fixed latents + condition mapping for :func:`conf_ll_binned`.

    ``kernel_bw``: Gaussian σ (percentage points) for histogram smoothing.

    Free (``condition_is_free=True``): conditions are unique (stim,
    incentive) design cells -- action is the model's own covert choice (see
    :func:`simulate_joint_conf`), so it's simulated jointly with confidence
    rather than being part of the grouping key.
    Non-free (``condition_is_free=False``): action is imposed externally
    (Observed/Forced/Replayed) and can differ trial-to-trial even for the
    same (stim, incentive) -- e.g. Replayed choices -- so it has to be part
    of the grouping key (conditions are unique (stim, incentive, a) cells)
    rather than modeled.

    Either way, unique condition cells get their own ``(n_mc,)`` latent pool
    -- shared across however many real trials fall in that cell -- rather
    than one pool per trial, since ``n_mc`` draws per *condition* (not per
    trial) is what the joint-simulation approach needs.
    """
    arrays = _trial_arrays(df, stimcol=stimcol, confcol=confcol, choicecol=choicecol)
    stim, incentive, a, conf_obs = arrays["stim"], arrays["incentive"], arrays["a"], arrays["conf_obs"]

    if condition_is_free:
        cond_key = np.column_stack([stim.astype(np.float64), incentive.astype(np.float64)])
    else:
        a_sign = (np.asarray(a, dtype=float) > 0.0).astype(np.float64)
        cond_key = np.column_stack([stim.astype(np.float64), incentive.astype(np.float64), a_sign])
    uniq, cond_idx = np.unique(cond_key, axis=0, return_inverse=True)
    cond_idx = np.asarray(cond_idx, dtype=np.int64).ravel()
    n_cond = int(uniq.shape[0])

    rng = np.random.default_rng(seed)
    z_r = rng.normal(size=(n_cond, n_mc)).astype(MC_DTYPE)
    z_l = rng.normal(size=(n_cond, n_mc)).astype(MC_DTYPE)
    z_conf = rng.normal(size=(n_cond, n_mc)).astype(MC_DTYPE)
    u_lapse = rng.random(size=(n_cond, n_mc)).astype(MC_DTYPE)
    u_tie = rng.random(size=(n_cond, n_mc)).astype(MC_DTYPE) if condition_is_free else None
    cond_a = None if condition_is_free else np.where(uniq[:, 2] > 0.5, 1.0, -1.0)

    a_idx_obs = (np.asarray(a, dtype=float) > 0.0).astype(np.int64)
    rating_idx_obs = np.clip(np.round(np.asarray(conf_obs, dtype=np.float64)), 0, N_RATING_BINS - 1).astype(np.int64)

    return {
        "cond_stim": uniq[:, 0], "cond_incentive": uniq[:, 1], "cond_a": cond_a,
        "cond_idx": cond_idx,
        "a_idx_obs": a_idx_obs, "rating_idx_obs": rating_idx_obs,
        "z_r": z_r, "z_l": z_l, "z_conf": z_conf, "u_lapse": u_lapse, "u_tie": u_tie,
        "kernel_bw": kernel_bw, "pad": pad,
        "n_trials": int(len(a)), "n_cond": n_cond, "n_mc": int(n_mc),
    }


def conf_ll_binned(params: np.ndarray, df: pd.DataFrame, cfg: dict) -> float:
    """Confidence log-likelihood via joint forward-simulation, scored against
    a padded, Gaussian-smoothed per-condition histogram table looked up at
    each trial's observed (a, rating). Default for both Free
    (``condition_is_free=True``) and non-free (action given).

    ``cfg["ll_data_binned"]["kernel_bw"]`` is the Gaussian σ on the 0–100
    rating scale (default 5).
    """
    pardict = _params_to_pardict(params, cfg)
    data = cfg.get("ll_data_binned")
    if data is None:
        return -np.inf

    p = resolve_params(pardict, cfg)
    a_sim, conf_sim = simulate_joint_conf(
        data["cond_stim"], data["cond_incentive"], p,
        z_r=data["z_r"], z_l=data["z_l"], z_conf=data["z_conf"],
        u_lapse=data["u_lapse"], u_tie=data["u_tie"], a=data["cond_a"],
    )  # (n_cond, n_mc) each

    density = _joint_conf_histogram_density(
        a_sim, conf_sim, kernel_bw=data["kernel_bw"], bin_pad=data["pad"]
    )  # (n_cond, 2, N_RATING_BINS)

    trial_p = density[data["cond_idx"], data["a_idx_obs"], data["rating_idx_obs"]]
    trial_p = np.clip(trial_p, 1e-300, None)
    ll_data = float(np.sum(np.log(trial_p)))
    if not np.isfinite(ll_data):
        return -np.inf

    ll_prior = log_prior(pardict, cfg.get("parnames", []), cfg.get("priors", DEFAULT_CONF_PRIORS))
    if not np.isfinite(ll_prior):
        return -np.inf
    return float(ll_data + ll_prior)


def make_conf_modelinfo(
    parnames: list[str],
    plb: list[float] | None = None,
    pub: list[float] | None = None,
    lb: list[float] | None = None,
    ub: list[float] | None = None,
    x0: list[float] | None = None,
) -> dict:
    """Build modelinfo for BADS / LBFGS / :func:`conf_ll_binned`.

    ``myfun`` here is just a placeholder default -- :func:`_conf_fit_modelinfo`
    (used by :func:`fit_conf_bads`) always overrides it with :func:`conf_ll_binned`.
    """
    parnames_list = list(parnames)
    _b = DEFAULT_CONF_PARAM_BOUNDS
    _fallback = (-np.inf, np.inf, -np.inf, np.inf, 0.0)
    if plb is None:
        plb = [_b.get(n, _fallback)[0] for n in parnames_list]
    if pub is None:
        pub = [_b.get(n, _fallback)[1] for n in parnames_list]
    if lb is None:
        lb = [_b.get(n, _fallback)[2] for n in parnames_list]
    if ub is None:
        ub = [_b.get(n, _fallback)[3] for n in parnames_list]
    if x0 is None:
        x0 = [_b.get(n, _fallback)[4] for n in parnames_list]
    if not (len(parnames_list) == len(plb) == len(pub) == len(lb) == len(ub) == len(x0)):
        raise ValueError("parnames, plb, pub, lb, ub, x0 must have equal length")

    cfg: dict = {"parnames": parnames_list, "fixedpars": {}}
    return {
        "plb": list(plb), "pub": list(pub), "bounds": [list(lb), list(ub)], "x0": list(x0),
        "myfun": conf_ll_binned, "cfg": cfg, "options": {},
    }


def _conf_fit_modelinfo(
    modelinfo: dict,
    dfsub: pd.DataFrame,
    *,
    sens_noise: float,
    sens_bias: float,
    p_lapse: float,
    condition_is_free: bool,
    n_mc: int,
    kernel_bw: float,
    priors: dict | None,
    seed: int,
    bin_pad: float = DEFAULT_BIN_PAD,
) -> dict:
    """Per-participant modelinfo with fixed MC data for the fit's ``myfun``.

    ``sens_noise``/``sens_bias``/``p_lapse`` are only added to ``fixedpars``
    when they are not already part of ``cfg["parnames"]`` -- this lets callers
    fit them freely (e.g. Observed/Forced, where they can't be recovered from a
    choice-only stage) by simply including them in ``parnames``.

    Always uses the binned joint-simulation likelihood (:func:`conf_ll_binned`).
    """
    parnames = set(modelinfo["cfg"].get("parnames", []))
    base_fixed = {}
    if "sens_noise" not in parnames:
        base_fixed["sens_noise"] = float(sens_noise)
    if "sens_bias" not in parnames:
        base_fixed["sens_bias"] = float(sens_bias)
    if "p_lapse" not in parnames:
        base_fixed["p_lapse"] = float(p_lapse)

    cfg_base = {
        **modelinfo["cfg"],
        "fixedpars": {
            **base_fixed,
            **modelinfo["cfg"].get("fixedpars", {}),
        },
        "condition_is_free": condition_is_free,
        "priors": priors if priors is not None else DEFAULT_CONF_PRIORS,
        "include_prior": True,
    }

    ll_data_binned = prepare_conf_ll_data_binned(
        dfsub, n_mc=n_mc, seed=seed, condition_is_free=condition_is_free,
        kernel_bw=kernel_bw, pad=bin_pad,
    )
    cfg = {**cfg_base, "ll_data_binned": ll_data_binned}
    return {**modelinfo, "cfg": cfg, "myfun": conf_ll_binned}


def fit_conf_bads(
    modelinfo: dict,
    dfsub: pd.DataFrame,
    *,
    sens_noise: float,
    sens_bias: float,
    p_lapse: float,
    condition_is_free: bool = True,
    n_mc: int = 200,
    kernel_bw: float = 5.0,
    priors: dict | None = None,
    seed: int = 0,
    n_restarts: int = 10,
    max_fun_evals: int = 500,
    n_jobs: int = -1,
    use_x0: bool = True,
    bin_pad: float = DEFAULT_BIN_PAD,
) -> tuple[np.ndarray, float]:
    """Fit via pyBADS (fixed MC; uncertainty_handling off).

    ``kernel_bw``: Gaussian σ on the 0–100 rating scale for the binned LL.
    ``use_x0=False`` draws all ``n_restarts`` starts uniformly from
    ``[plb, pub]`` instead of anchoring the first restart at ``modelinfo["x0"]``.
    """
    fit_modelinfo = _conf_fit_modelinfo(
        modelinfo, dfsub, sens_noise=sens_noise, sens_bias=sens_bias, p_lapse=p_lapse,
        condition_is_free=condition_is_free, n_mc=n_mc, kernel_bw=kernel_bw,
        priors=priors, seed=seed, bin_pad=bin_pad,
    )
    x_hat, ll_hat, _info = fit_model_BADS(
        fit_modelinfo, dfsub,
        options={"max_fun_evals": max_fun_evals, "uncertainty_handling": False},
        n_restarts=n_restarts, seed=seed, n_jobs=n_jobs, use_x0=use_x0,
    )
    return x_hat, float(ll_hat)
