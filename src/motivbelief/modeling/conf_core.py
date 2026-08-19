"""Generative confidence model: core, simulation, and expected confidence.

Likelihood scoring and BADS fitting live in :mod:`motivbelief.modeling.conf_ll`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm

from motivbelief.modeling.choice import psychofun_inv

MC_DTYPE = np.float32

# Confidence forced to this value on a lapse trial (not a fitted parameter).
CONF_LAPSE_VALUE = 0.5

# Numeric defaults for resolve_params.
DEFAULT_PARAMS: dict = {
    "pe_wt": 0.0,
    "pe_wt_v": 0.0,
    "bel_bias_v": 0.0,
    "bel_bias": 0.0,
    "pe_add": 0.0,
    "pe_add_v": 0.0,
    "sens_noise": 0.0,
    "bel_noise": 0.0,
    "sens_bias": 0.0,
    "p_lapse": 0.0,
    "mismatch_coef": 1.0,
    "mismatch_gate_baseline": 1.0,
    "evidence_offset_mult": 1.96,
}

_PARAM_KEYS = tuple(DEFAULT_PARAMS.keys())


# ---------------------------------------------------------------------------
# Parameter resolution
# ---------------------------------------------------------------------------

def resolve_params(pardict: dict | None = None, cfg: dict | None = None) -> dict:
    """Merge defaults, pardict, and cfg overrides.

    cfg's ``fixedpars`` wins over pardict. Adds the Bayesian read-out
    scalars ``mu_hat`` and ``sigma_total`` (see :func:`truncation_scalars`).
    """
    p = {**DEFAULT_PARAMS, **(pardict or {})}
    if cfg:
        for k, v in cfg.get("fixedpars", {}).items():
            p[k] = v if isinstance(v, str) else (float(v) if np.isscalar(v) else v)

    for key in _PARAM_KEYS:
        val = p.get(key, DEFAULT_PARAMS[key])
        # mismatch_coef may be the string flag 'covert_conf' (simulation-time option)
        p[key] = val if isinstance(val, str) else float(val)

    mu_hat, sigma_total = truncation_scalars(p)
    p["mu_hat"] = float(mu_hat)
    p["sigma_total"] = float(sigma_total)
    return p

def _stim_channels(stim: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    stim = np.asarray(stim, dtype=float).ravel()
    s_r = np.abs(stim * (stim > 0))
    s_l = np.abs(stim * (stim < 0))
    return s_r, s_l

def truncation_scalars(pardict: dict) -> tuple[float, float]:
    """Return (mu_hat, sigma_total) for the Bayesian confidence read-out.

    sigma_total combines sensory noise (doubled, from the x_r - x_l
    comparison) and belief noise, so the read-out's assumed noise matches
    the noise actually injected into x_conf (see conf_core module docstring
    and the paper's Methods/SOM). mu_hat is the inverse psychometric
    function (probit-lapse) at 75% accuracy, scaled by sigma_total.

    sens_bias is deliberately excluded: it shifts the decision variable in a
    fixed direction regardless of stimulus side, so it cancels out over a
    symmetric left/right trial set and should not enter the threshold
    magnitude here -- only sens_noise/p_lapse do.
    """
    sens_noise = float(pardict.get("sens_noise", 1e-4))
    p_lapse = float(pardict.get("p_lapse", 0.0))
    bel_noise = float(pardict.get("bel_noise", 0.0))
    sigma_diff = np.sqrt(2.0 * sens_noise**2)
    sigma_total = float(np.sqrt(sigma_diff**2 + bel_noise**2))
    mu_hat = float(psychofun_inv([0.0, sigma_total, p_lapse], 0.75))
    return mu_hat, sigma_total

def build_mc_cache(n_trials: int, n_mc: int, rng: np.random.Generator) -> dict:
    """Fixed (n_trials, n_mc) float32 latents for MC integration / fitting."""
    return {
        "z_r": rng.normal(0.0, 1.0, size=(n_trials, n_mc)).astype(MC_DTYPE),
        "z_l": rng.normal(0.0, 1.0, size=(n_trials, n_mc)).astype(MC_DTYPE),
        "z_conf": rng.normal(0.0, 1.0, size=(n_trials, n_mc)).astype(MC_DTYPE),
        "u_lapse": rng.random(size=(n_trials, n_mc)).astype(MC_DTYPE),
    }


# ---------------------------------------------------------------------------
# Generative core (NumPy)
# ---------------------------------------------------------------------------

def confidence_core(
    data: dict,
    params: dict,
) -> np.ndarray:
    """
    Map latents + action -> confidence, vectorized over (trial, MC).

    ``data`` keys: z_r, z_l, z_conf, u_lapse, sr, sl, a, incentive.
    ``params``: from :func:`resolve_params` (or any dict with the same keys).

    Implements the generative model described in the Methods and SOM:
    sensory evidence x_r/x_l = s_r/s_l + sens_noise*z_r/z_l +/- sens_bias/2
    (split symmetrically across channels, zeroed on lapse); covert choice
    sign(x_r - x_l); negative evidence handled by an offset-and-clip
    transform (shift by sens_noise*evidence_offset_mult, clip at 0); belief
    evidence as a motivated weighted difference of chosen/unchosen evidence
    (weights w_c=1+delta, w_u=1-delta, delta=tanh(pe_wt + pe_wt_v*incentive)),
    plus belief noise; and a Gaussian likelihood-ratio read-out (mu_hat,
    sigma_total) mapping that evidence to a probability, forced to 50% on a
    lapse trial.

    ``mismatch_coef``/``mismatch_gate_baseline`` implement the three
    congruence models (Action/Intention/Confirmation) from the Methods: they
    rescale the motivated terms when the given action disagrees with the
    model's own covert choice. This only has an effect for Non-Free
    conditions -- on Free trials the action always equals the covert choice,
    so the rescaling factor is 1 throughout.
    """
    p = params
    z_r, z_l, z_conf = data["z_r"], data["z_l"], data["z_conf"]
    u_lapse = data["u_lapse"]
    sr, sl, a, incentive = data["sr"], data["sl"], data["a"], data["incentive"]

    sens_noise = np.float32(p["sens_noise"])
    sens_bias = np.float32(p["sens_bias"])
    p_lapse = np.float32(p["p_lapse"])
    lap = np.where(u_lapse <= p_lapse, np.float32(1.0), np.float32(0.0))
    half_bias = np.float32(0.5) * sens_bias
    xr = (np.float32(1.0) - lap) * (sr + sens_noise * z_r + half_bias)
    xl = (np.float32(1.0) - lap) * (sl + sens_noise * z_l - half_bias)

    a_b = a.reshape(-1, 1) if a.ndim == 1 else a

    # sens_bias is already baked into xr/xl (split symmetrically across
    # channels, as in Rahnev et al. 2024's PosEv model), so it propagates
    # into x_chosen/x_unchosen -> xconf, not just this gate.
    covert_choice = np.sign(xr - xl) * (np.float32(1.0) - lap)

    # Bayesian LR read-out scalars (also used for covert_conf on mismatch trials).
    # Equal-variance Gaussian LR p_c/(p_c+p_u) == sigmoid(2*mu_hat*x/sigma_total**2).
    mu_hat = np.float32(p["mu_hat"])
    sigma_total = np.float32(p["sigma_total"])
    inv_var = np.float32(1.0) / (sigma_total * sigma_total)
    covert_conf = np.float32(1.0) / (
        np.float32(1.0) + np.exp(np.float32(-2.0) * mu_hat * inv_var * np.abs(xr - xl))
    )

    offset = sens_noise * np.float32(p["evidence_offset_mult"])
    xl_pos = np.clip(xl + offset, 0, None)
    xr_pos = np.clip(xr + offset, 0, None)

    x_chosen = np.where(a_b > 0.0, xr_pos, xl_pos)
    x_unchosen = np.where(a_b > 0.0, xl_pos, xr_pos)

    inc = incentive.reshape(-1, 1) if incentive.ndim == 1 else incentive

    # factor rescales the incentive-linked ("motivated") terms on a mismatch
    # trial (action != covert choice), per the Action-/Intention-/
    # Confirmation-congruent models. mismatch_gate_baseline additionally
    # controls whether the baseline (non-incentive) pe_wt/pe_add/bel_bias is
    # rescaled too (factor_base). On Free trials the action is always the
    # model's own covert choice, so mismatch never fires and both factors
    # stay at 1; this only matters for Non-Free simulation.
    mismatch = ((a_b != covert_choice) & (covert_choice != 0.0)).astype(MC_DTYPE)

    factor = np.where(mismatch > 0.5, np.float32(p["mismatch_coef"]), np.float32(1.0))

    gate_base = np.float32(1.0) if p["mismatch_gate_baseline"] >= 0.5 else np.float32(0.0)
    factor_base = np.float32(1.0) + gate_base * (factor - np.float32(1.0))

    x_chosen = x_chosen + factor_base*np.float32(p["pe_add"]) + factor*np.float32(p["pe_add_v"]) * inc

    w = np.tanh(factor_base*np.float32(p["pe_wt"]) + factor*np.float32(p["pe_wt_v"]) * inc)

    # bel_noise is genuine metacognitive noise, not a motivated-bias
    # mechanism -- never gated by mismatch (unlike bel_bias_v/bel_bias below).
    conf_noise = np.float32(p["bel_noise"]) * z_conf
    xconf = (
        (1+w) * x_chosen - (1-w) * x_unchosen
        + factor*np.float32(p["bel_bias_v"]) * inc
        + conf_noise
        + factor_base*np.float32(p["bel_bias"])
    )
    conf = np.float32(1.0) / (
        np.float32(1.0) + np.exp(np.float32(-2.0) * mu_hat * inv_var * xconf)
    )
    conf = np.clip(conf, np.float32(1e-4), np.float32(1.0 - 1e-4))

    conf = np.where(lap > 0.5, np.float32(CONF_LAPSE_VALUE), conf)

    return conf


def draw_free_choice_action(
    stim: np.ndarray,
    pardict: dict,
    *,
    z_r: np.ndarray,
    z_l: np.ndarray,
    u_lapse: np.ndarray,
    u_tie: np.ndarray,
) -> np.ndarray:
    """Covert choice from sensory evidence; ties broken by ``u_tie < 0.5``."""
    sens_noise = float(pardict.get("sens_noise", 1e-4))
    sens_bias = float(pardict.get("sens_bias", 0.0))
    p_lapse = float(pardict.get("p_lapse", 0.0))
    s_r, s_l = _stim_channels(stim)
    s_r = s_r.reshape(-1, *([1] * (z_r.ndim - 1)))
    s_l = s_l.reshape(-1, *([1] * (z_l.ndim - 1)))
    lap = (u_lapse <= p_lapse).astype(float)
    half_bias = 0.5 * sens_bias
    xr = (1.0 - lap) * (s_r + sens_noise * z_r + half_bias)
    xl = (1.0 - lap) * (s_l + sens_noise * z_l - half_bias)
    covert_choice = np.sign(xr - xl) * (1.0 - lap)
    return np.where(covert_choice != 0.0, covert_choice, np.where(u_tie < 0.5, -1.0, 1.0))


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

def simulate_act_conf(df: pd.DataFrame, pardict: dict, *, rng: np.random.Generator | None = None):
    """
    One (action, confidence) draw per trial.

    Free choice (no ``a`` column): action from the same sensory draw as confidence.
    Observed (``a`` present): action taken as given; fresh sensory draw for conf.
    """
    rng = rng or np.random.default_rng()
    stim = np.asarray(df["stim"].values, dtype=float)
    incentive = np.asarray(df.get("incentive", np.zeros_like(stim)).values, dtype=float)
    t = len(stim)
    mc = build_mc_cache(t, 1, rng)

    if "a" in df.columns:
        a = np.asarray(df["a"].values, dtype=MC_DTYPE)
    else:
        u_tie = rng.random(size=(t, 1)).astype(MC_DTYPE)
        a = draw_free_choice_action(
            stim, pardict, z_r=mc["z_r"], z_l=mc["z_l"], u_lapse=mc["u_lapse"], u_tie=u_tie
        ).ravel().astype(MC_DTYPE)

    s_r, s_l = _stim_channels(stim)
    data = {
        **mc,
        "sr": s_r.astype(MC_DTYPE)[:, None],
        "sl": s_l.astype(MC_DTYPE)[:, None],
        "a": a,
        "incentive": incentive.astype(MC_DTYPE),
    }
    conf = confidence_core(data, resolve_params(pardict))

    out = df.copy()
    out["a"] = a.astype(float)
    out["correct"] = (np.sign(a) == np.sign(stim)) * 1
    out["conf"] = conf.ravel().astype(float) * 100.0
    return out


def simulate_replayed_act_conf(df: pd.DataFrame, pardict: dict, *, rng: np.random.Generator | None = None):
    """Choice and confidence from two independent sensory draws (no ``a`` in df)."""
    if "a" in df.columns:
        raise ValueError("simulate_replayed_act_conf expects trials without 'a'")
    rng = rng or np.random.default_rng()
    stim = np.asarray(df["stim"].values, dtype=float)
    incentive = np.asarray(df.get("incentive", np.zeros_like(stim)).values, dtype=float)
    t = len(stim)

    mc1 = build_mc_cache(t, 1, rng)
    u_tie = rng.random(size=(t, 1)).astype(MC_DTYPE)
    a = draw_free_choice_action(
        stim, pardict, z_r=mc1["z_r"], z_l=mc1["z_l"], u_lapse=mc1["u_lapse"], u_tie=u_tie
    ).ravel().astype(MC_DTYPE)

    mc2 = build_mc_cache(t, 1, rng)
    s_r, s_l = _stim_channels(stim)
    data = {
        **mc2,
        "sr": s_r.astype(MC_DTYPE)[:, None],
        "sl": s_l.astype(MC_DTYPE)[:, None],
        "a": a,
        "incentive": incentive.astype(MC_DTYPE),
    }
    conf = confidence_core(data, resolve_params(pardict))

    out = df.copy()
    out["a"] = a.astype(float)
    out["correct"] = (np.sign(a) == np.sign(stim)) * 1
    out["conf"] = conf.ravel().astype(float) * 100.0
    return out


# ---------------------------------------------------------------------------
# Trial arrays / param packing (shared by LL + prediction)
# ---------------------------------------------------------------------------

def _trial_arrays(
    df: pd.DataFrame, *, stimcol: str = "stim", confcol: str | None = "conf", choicecol: str = "a"
) -> dict:
    stim = np.asarray(df[stimcol].values, dtype=MC_DTYPE).ravel()
    a = np.asarray(df[choicecol].values, dtype=MC_DTYPE).ravel()
    incentive = (
        np.asarray(df["incentive"].values, dtype=MC_DTYPE).ravel()
        if "incentive" in df.columns
        else np.zeros_like(stim)
    )
    s_r, s_l = _stim_channels(stim.astype(np.float64))
    out = {
        "stim": stim,
        "a": a,
        "incentive": incentive,
        "sr": s_r.astype(MC_DTYPE)[:, None],
        "sl": s_l.astype(MC_DTYPE)[:, None],
    }
    if confcol is not None:
        out["conf_obs"] = np.asarray(df[confcol].values, dtype=MC_DTYPE).ravel()
    return out


def simulate_joint_conf(
    stim: np.ndarray,
    incentive: np.ndarray,
    pardict: dict,
    *,
    z_r: np.ndarray,
    z_l: np.ndarray,
    z_conf: np.ndarray,
    u_lapse: np.ndarray,
    u_tie: np.ndarray | None = None,
    a: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Forward-simulate (choice, confidence) jointly, once per condition row.

    Free choice (``a=None``): action is the model's own covert choice,
    derived from the same evidence draw as confidence (needs ``u_tie`` for
    tie-breaking, via :func:`draw_free_choice_action`) -- every one of the
    ``n_mc`` draws is a genuine, self-consistent (choice, confidence) sample;
    none are discarded or down-weighted.
    Non-free (``a`` given, one value per condition row -- Observed/Forced/
    Replayed): action is imposed externally rather than modeled, so only
    confidence is simulated, conditional on that fixed action.

    ``stim``/``incentive``: one value per condition, shape ``(n_cond,)``.
    ``z_r``/``z_l``/``z_conf``/``u_lapse``(/``u_tie``): shared latents, shape
    ``(n_cond, n_mc)``.

    Returns ``(a, conf_pct)``, each shape ``(n_cond, n_mc)`` (``conf_pct`` on
    the 0-100 scale; for non-free, ``a`` is just the input broadcast to that
    shape).
    """
    p = resolve_params(pardict)
    stim = np.asarray(stim, dtype=float).ravel()
    incentive = np.asarray(incentive, dtype=float).ravel()

    if a is None:
        if u_tie is None:
            raise ValueError("u_tie is required when a is None (free choice)")
        a_arr = draw_free_choice_action(stim, p, z_r=z_r, z_l=z_l, u_lapse=u_lapse, u_tie=u_tie)
    else:
        a_arr = np.broadcast_to(np.asarray(a, dtype=MC_DTYPE).reshape(-1, 1), z_r.shape)

    s_r, s_l = _stim_channels(stim)
    data = {
        "z_r": z_r, "z_l": z_l, "z_conf": z_conf, "u_lapse": u_lapse,
        "sr": s_r.astype(MC_DTYPE)[:, None], "sl": s_l.astype(MC_DTYPE)[:, None],
        "a": a_arr.astype(MC_DTYPE),
        "incentive": np.broadcast_to(incentive[:, None], a_arr.shape).astype(MC_DTYPE),
    }
    conf = confidence_core(data, p)
    conf_pct = np.clip(conf * 100.0, 0.0, 100.0)
    return a_arr, conf_pct


def expected_confidence(
    df: pd.DataFrame,
    pardict: dict,
    *,
    condition_is_free: bool,
    n_mc: int = 200,
    seed: int = 0,
    stimcol: str = "stim",
    choicecol: str = "a",
) -> np.ndarray:
    """MC E[confidence | stim, incentive, a] on 0-100 scale.

    Free: conditional mean of the jointly forward-simulated draws that match
    the observed action (see :func:`simulate_joint_conf`) -- degrades
    gracefully to a 50% fallback instead of collapsing to a spurious point
    estimate when P(covert choice == a) is tiny (0 matching draws) under the
    current parameters.
    Non-free: plain (unweighted) MC mean; action is given directly, not
    conditioned on the model's own covert draw.
    """
    arrays = _trial_arrays(df, stimcol=stimcol, choicecol=choicecol, confcol=None)
    stim, incentive, a_obs = arrays["stim"], arrays["incentive"], arrays["a"]

    if condition_is_free:
        cond_key = np.column_stack([stim.astype(np.float64), incentive.astype(np.float64)])
        uniq, cond_idx = np.unique(cond_key, axis=0, return_inverse=True)
        cond_idx = np.asarray(cond_idx, dtype=np.int64).ravel()
        n_cond = int(uniq.shape[0])

        rng = np.random.default_rng(seed)
        z_r = rng.normal(size=(n_cond, n_mc)).astype(MC_DTYPE)
        z_l = rng.normal(size=(n_cond, n_mc)).astype(MC_DTYPE)
        z_conf = rng.normal(size=(n_cond, n_mc)).astype(MC_DTYPE)
        u_lapse = rng.random(size=(n_cond, n_mc)).astype(MC_DTYPE)
        u_tie = rng.random(size=(n_cond, n_mc)).astype(MC_DTYPE)

        a_sim, conf_sim = simulate_joint_conf(
            uniq[:, 0], uniq[:, 1], pardict,
            z_r=z_r, z_l=z_l, z_conf=z_conf, u_lapse=u_lapse, u_tie=u_tie,
        )  # (n_cond, n_mc) each
        is_pos = a_sim > 0.0
        n_pos = is_pos.sum(axis=1)
        n_neg = (~is_pos).sum(axis=1)
        sum_pos = np.where(is_pos, conf_sim, 0.0).sum(axis=1)
        sum_neg = np.where(is_pos, 0.0, conf_sim).sum(axis=1)
        mean_pos = np.where(n_pos > 0, sum_pos / np.maximum(n_pos, 1), 50.0)
        mean_neg = np.where(n_neg > 0, sum_neg / np.maximum(n_neg, 1), 50.0)
        cond_mean = np.stack([mean_neg, mean_pos], axis=1)  # (n_cond, 2)

        a_idx_obs = (np.asarray(a_obs, dtype=float) > 0.0).astype(np.int64)
        return cond_mean[cond_idx, a_idx_obs]

    mc_cache = build_mc_cache(len(stim), n_mc, np.random.default_rng(seed))
    data = {**arrays, **mc_cache}
    conf = confidence_core(data, resolve_params(pardict))
    return np.mean(conf, axis=1) * 100.0
