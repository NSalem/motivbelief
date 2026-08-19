"""Load Free confidence fits, t-tests, information criteria, and Free BMC."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from scipy import stats

# Numeric act/intent/confirm grid plus the string-flag covert_conf variant
# (factor = model's own covert confidence on mismatch trials; see conf_core).
REPLAYED_MISMATCH_COEFS = (-1, 0, 1, "covert_conf")
FREE_EXPERIMENTS_VIOLIN = ("exp1a", "exp2")
REPLAYED_EXPERIMENT = "exp3"
# When several variant CSVs exist for the same cohort, prefer current Free tags.
CONF_FIT_TAG_PRIORITY = ("pe_wt_v", "bel_bias_v")

_KNOWN_CONDITIONS = ("Free", "Replayed", "Observed", "Forced")
# Numeric (_mcm-1/_mcm0/_mcm1) or named string flags (_mcmcovert_conf).
_MCM_SUFFIX_RE = re.compile(r"^(?P<tag>.*)_mcm(?P<mcm>-?\d+|[A-Za-z]\w*)$")


def parse_mismatch_coef_token(raw: str) -> int | str:
    """Parse a ``_mcm…`` suffix token to int (numeric grid) or str (named flag)."""
    try:
        return int(raw)
    except ValueError:
        return raw


def format_mismatch_coef(mcm: int | float | str) -> str:
    """Compact label for a mismatch_coef grid point (numeric or named)."""
    if isinstance(mcm, str):
        return mcm
    return f"{mcm:g}"


def split_condition_stem(stem: str) -> tuple[str, str | None]:
    """Split a ``results_<condition>[_<fit_tag>]`` filename stem into ``(condition, fit_tag)``."""
    if stem.startswith("results_"):
        stem = stem[len("results_") :]
    for condition in _KNOWN_CONDITIONS:
        if stem == condition:
            return condition, None
        if stem.startswith(condition + "_"):
            return condition, stem[len(condition) + 1 :]
    raise ValueError(f"Stem {stem!r} does not start with a known condition {_KNOWN_CONDITIONS}")


def parse_conf_fit_stem(exp: str, stem: str) -> dict | None:
    """Parse a ``results_<condition>[_<fit_tag>][_mcm{coef}]`` stem living under ``fits_conf/<exp>/``.

    A trailing ``_mcm{-?\\d+}`` or ``_mcm{name}`` on the fit tag (e.g.
    ``pe_wt_v_mcm-1``, written by optional nonfree fit scripts) is pulled
    out into ``mismatch_coef``; the rest of the tag stays opaque.
    """
    try:
        condition, fit_tag = split_condition_stem(stem)
    except ValueError:
        return None
    mismatch_coef = None
    if fit_tag is not None:
        m = _MCM_SUFFIX_RE.match(fit_tag)
        if m is not None:
            mismatch_coef = parse_mismatch_coef_token(m.group("mcm"))
            fit_tag = m.group("tag") or None
    return {"exp": exp, "condition": condition, "fit_tag": fit_tag, "mismatch_coef": mismatch_coef}


def _fit_tag_priority(fit_tag: str | None) -> int:
    if not fit_tag:
        return len(CONF_FIT_TAG_PRIORITY)
    try:
        return CONF_FIT_TAG_PRIORITY.index(fit_tag)
    except ValueError:
        return len(CONF_FIT_TAG_PRIORITY) + 1


def _select_conf_fit_paths(fits_dir: Path) -> list[Path]:
    """One CSV per (experiment, condition, mismatch_coef, fit_tag), preferring canonical fit tags."""
    fits_dir = Path(fits_dir)
    by_key: dict[tuple[str, str, int | str | None, str | None], list[tuple[int, Path]]] = {}
    for exp_dir in sorted(p for p in fits_dir.iterdir() if p.is_dir()):
        for path in sorted(exp_dir.glob("*.csv")):
            meta = parse_conf_fit_stem(exp_dir.name, path.stem)
            if meta is None:
                continue
            key = (meta["exp"], meta["condition"], meta["mismatch_coef"], meta["fit_tag"])
            rank = _fit_tag_priority(meta.get("fit_tag"))
            by_key.setdefault(key, []).append((rank, path))
    return [sorted(items, key=lambda t: t[0])[0][1] for items in by_key.values()]


def coerce_mismatch_coef(value) -> int | str | None:
    """Normalize a dataframe / metadata mismatch_coef cell to int, str, or None."""
    if value is None or (isinstance(value, float) and np.isnan(value)) or pd.isna(value):
        return None
    if isinstance(value, str):
        return parse_mismatch_coef_token(value)
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        ivalue = int(value)
        if float(value) == float(ivalue):
            return ivalue
        return format_mismatch_coef(float(value))
    return parse_mismatch_coef_token(str(value))


def model_label(condition: str, mismatch_coef: int | str | None) -> str:
    if condition == "Free":
        return "Free"
    if mismatch_coef is not None:
        return f"{condition} (mcm={format_mismatch_coef(mismatch_coef)})"
    return str(condition)


def load_conf_fits(fits_dir: Path) -> pd.DataFrame:
    """Load confidence-fit CSVs (``fits_conf/<exp>/<condition>[_<tag>].csv``) into one table."""
    fits_dir = Path(fits_dir)
    frames: list[pd.DataFrame] = []
    for path in sorted(_select_conf_fit_paths(fits_dir), key=lambda p: (p.parent.name, p.name)):
        meta = parse_conf_fit_stem(path.parent.name, path.stem)
        assert meta is not None
        df = pd.read_csv(path)
        df["experiment"] = meta["exp"]
        df["choiceType"] = meta["condition"]
        if "mismatch_coef" not in df.columns and meta["mismatch_coef"] is not None:
            df["mismatch_coef"] = meta["mismatch_coef"]
        elif "mismatch_coef" in df.columns:
            df["mismatch_coef"] = df["mismatch_coef"].map(coerce_mismatch_coef)
        df["model_label"] = [
            model_label(str(cond), coerce_mismatch_coef(mcm))
            for cond, mcm in zip(df["choiceType"], df.get("mismatch_coef", [None] * len(df)))
        ]
        df["fit_tag"] = meta.get("fit_tag")
        df["source_file"] = path.name
        frames.append(df)
    if not frames:
        raise FileNotFoundError(f"No confidence fit CSVs under {fits_dir}")
    return pd.concat(frames, ignore_index=True)


def one_sample_ttests(
    data: pd.DataFrame,
    *,
    parameters: Iterable[str] = ("pe_wt", "pe_wt_v"),
    model_labels: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Two-sided one-sample t-tests vs 0 (plus Wilcoxon) per scope × parameter."""
    if model_labels is None:
        model_labels = ["Free"] + [
            model_label("Replayed", m) for m in REPLAYED_MISMATCH_COEFS
        ]

    rows: list[dict] = []
    scopes: list[tuple[str, str, str, pd.DataFrame]] = []

    for ml in model_labels:
        sub_ml = data.loc[data["model_label"] == ml]
        if sub_ml.empty:
            continue
        scopes.append((f"pooled | {ml}", "all", ml, sub_ml))
        for exp in sorted(sub_ml["experiment"].unique()):
            sub = sub_ml.loc[sub_ml["experiment"] == exp]
            scopes.append((f"{exp} | {ml}", exp, ml, sub))

    for scope, exp, ml, sub in scopes:
        for par in parameters:
            if par not in sub.columns:
                continue
            x = sub[par].dropna().to_numpy(dtype=float)
            if len(x) < 2:
                continue
            tt = stats.ttest_1samp(x, popmean=0.0, alternative="two-sided")
            try:
                wil = stats.wilcoxon(x, alternative="two-sided", zero_method="wilcox")
                w_p = float(wil.pvalue)
            except (ValueError, RuntimeWarning):
                w_p = np.nan
            rows.append(
                {
                    "scope": scope,
                    "experiment": exp,
                    "model_label": ml,
                    "parameter": par,
                    "n": len(x),
                    "mean": float(np.mean(x)),
                    "std": float(np.std(x, ddof=1)) if len(x) > 1 else np.nan,
                    "sem": float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else np.nan,
                    "t": float(tt.statistic),
                    "t_p": float(tt.pvalue),
                    "wilcoxon_p": w_p,
                }
            )
    return pd.DataFrame(rows)


def _ll_column(df: pd.DataFrame) -> str:
    if "ll_data_eval" in df.columns:
        return "ll_data_eval"
    if "ll_data" in df.columns:
        return "ll_data"
    if "ll" in df.columns:
        return "ll"
    raise KeyError("Need ll_data_eval, ll_data or ll column for BMC")


def compute_information_criteria(
    df: pd.DataFrame,
    *,
    ll_col: str = "ll_data_eval",
    n_col: str = "n_trials",
    k_col: str = "n_params",
) -> pd.DataFrame:
    """Per-row BIC and AICc from log-likelihood and trial count."""
    out = df.copy()
    ll = out[ll_col].astype(float)
    n = out[n_col].astype(float)
    if k_col not in out.columns:
        raise KeyError(f"Missing {k_col}")
    k = out[k_col].astype(float)
    out["bic"] = -2.0 * ll + k * np.log(n)
    denom = n - k - 1.0
    out["aicc"] = np.where(
        denom > 0,
        -2.0 * ll + 2.0 * k + (2.0 * k * (k + 1.0)) / denom,
        np.nan,
    )
    return out


def summarize_ic_by_model(ic: pd.DataFrame, *, group_cols: list[str]) -> pd.DataFrame:
    """Mean BIC / AICc per model scope."""
    rows = []
    for keys, sub in ic.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = dict(zip(group_cols, keys))
        row["n"] = len(sub)
        row["mean_bic"] = float(sub["bic"].mean())
        row["mean_aicc"] = float(sub["aicc"].mean())
        if len(sub) > 1:
            row["sem_bic"] = float(sub["bic"].std(ddof=1) / np.sqrt(len(sub)))
            row["sem_aicc"] = float(sub["aicc"].std(ddof=1) / np.sqrt(len(sub)))
        else:
            row["sem_bic"] = np.nan
            row["sem_aicc"] = np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def build_model_ll_matrix(
    data: pd.DataFrame,
    *,
    model_col: str,
    evidence_col: str = "ll_data_eval",
    id_cols: Iterable[str] = ("participant",),
) -> tuple[np.ndarray, list, list[str]]:
    """Model × subject log-evidence matrix for groupBMC.

    ``id_cols`` identifies a subject; pass more than just ``"participant"``
    (e.g. ``("experiment", "participant")``) when pooling across experiments
    whose raw participant numbers can collide between different real people.
    """
    id_cols = tuple(id_cols)
    models = sorted(data[model_col].dropna().unique())
    by_participant: dict[tuple, dict[str, float]] = {}
    for _, row in data.iterrows():
        pid = tuple(row[c] for c in id_cols)
        ml = str(row[model_col])
        by_participant.setdefault(pid, {})[ml] = float(row[evidence_col])
    complete = {
        pid: ev for pid, ev in by_participant.items() if all(m in ev for m in models)
    }
    if not complete:
        raise ValueError("No participants with all models present")
    participants = sorted(complete)
    L = np.asarray([[complete[p][m] for p in participants] for m in models], dtype=float)
    return L, participants, models


def model_comparison_bmc(
    data: pd.DataFrame,
    *,
    model_col: str = "fit_model",
    evidence_col: str = "ll_data_eval",
    id_cols: Iterable[str] = ("participant",),
) -> pd.DataFrame:
    """Random-effects BMC over models in ``data``."""
    from groupBMC.groupBMC import GroupBMC

    L, participants, model_names = build_model_ll_matrix(
        data, model_col=model_col, evidence_col=evidence_col, id_cols=id_cols
    )
    result = GroupBMC(L).get_result()
    rows = []
    for i, name in enumerate(model_names):
        rows.append(
            {
                "fit_model": name,
                "expected_frequency": float(result.frequency_mean[i]),
                "exceedance_probability": float(result.exceedance_probability[i]),
                "protected_exceedance_probability": float(
                    result.protected_exceedance_probability[i]
                ),
                "frequency_var": float(result.frequency_var[i]),
            }
        )
    out = pd.DataFrame(rows)
    out.attrs["n_participants"] = len(participants)
    out.attrs["participants"] = participants
    return out


# The two Free confidence models compared in the paper (see Methods and SOM
# Section 9): both share a baseline pe_wt (a data-estimated positive-evidence
# weighting, spanning Kiani & Shadlen-style balance-of-evidence at pe_wt=0 to
# Samaha/Desender/Peters-style positive-evidence-only as it saturates), then
# dissociate how incentive acts on top of it -- reweighting evidence
# (pe_wt_v) vs. shifting the confidence read-out directly (bel_bias_v).
FREE_BMC_FIT_TAGS = ("pe_wt_v", "bel_bias_v")


def free_model_bmc(
    data: pd.DataFrame,
    *,
    experiments: Iterable[str],
    evidence_col: str = "AICc",
) -> pd.DataFrame:
    """Random-effects BMC between the two Free confidence models (pe_wt_v vs bel_bias_v).

    Free fit CSVs carry no ``ll_data_eval``, only ``AICc`` (lower is better),
    so it's sign-flipped (``-0.5 * AICc``) into a log-evidence groupBMC can use.
    Pools each experiment's already-completed per-participant fits rather than
    running a new joint fit; when more than one experiment is given, subjects
    are keyed by ``(experiment, participant)`` since raw participant numbers
    can collide across experiments.
    """
    experiments = tuple(experiments)
    sub = data.loc[
        (data["choiceType"] == "Free")
        & data["experiment"].isin(experiments)
        & data["fit_tag"].isin(FREE_BMC_FIT_TAGS)
    ].copy()
    if sub.empty:
        raise ValueError(f"No Free fits for experiments={experiments}")
    sub["_bmc_evidence"] = -0.5 * sub[evidence_col].astype(float)
    id_cols = ("experiment", "participant") if len(experiments) > 1 else ("participant",)
    bmc = model_comparison_bmc(
        sub, model_col="fit_tag", evidence_col="_bmc_evidence", id_cols=id_cols
    )
    bmc["scope"] = "+".join(experiments)
    return bmc


def bootstrap_model_comparison_bmc(
    data: pd.DataFrame,
    *,
    model_col: str = "fit_model",
    evidence_col: str = "ll_data_eval",
    n_boot: int = 1000,
    resample_size: int | None = None,
    seed: int = 0,
) -> pd.DataFrame:
    """Bootstrap-resampled random-effects BMC.

    Builds the model x participant log-evidence matrix ONCE, then resamples
    participants (columns) with replacement ``n_boot`` times and reruns
    groupBMC on each resample -- a distribution over model-comparison
    outcomes under sampling noise, without re-simulating or re-fitting
    anything. This is the same resampling logic intended for a real-data BMC
    with a fixed set of participants, so it applies unchanged there too.

    ``resample_size``: how many participants each bootstrap draw contains
    (default: None -> same as the original cohort, ``L.shape[1]``, the
    standard bootstrap). Set smaller (e.g. to a projected/planned N) to ask
    "how noisy would this conclusion be with fewer participants" instead of
    "how noisy is it with the N we actually have" -- still drawn WITH
    replacement from the same fixed participant pool, so this doesn't
    simulate new data or add information a smaller real sample would lack
    (e.g. narrower per-participant coverage); it only reflects sampling
    variance of the resample size itself.

    Returns one row per (boot_iter, fit_model) with expected_frequency /
    exceedance_probability / protected_exceedance_probability. Summarize
    with :func:`summarize_bootstrap_bmc`.
    """
    from groupBMC.groupBMC import GroupBMC

    L, participants, model_names = build_model_ll_matrix(
        data, model_col=model_col, evidence_col=evidence_col
    )
    n_participants = L.shape[1]
    draw_size = n_participants if resample_size is None else int(resample_size)
    rng = np.random.default_rng(seed)

    rows = []
    for b in range(int(n_boot)):
        idx = rng.integers(0, n_participants, size=draw_size)
        result = GroupBMC(L[:, idx]).get_result()
        for i, name in enumerate(model_names):
            rows.append(
                {
                    "boot_iter": b,
                    "fit_model": name,
                    "expected_frequency": float(result.frequency_mean[i]),
                    "exceedance_probability": float(result.exceedance_probability[i]),
                    "protected_exceedance_probability": float(
                        result.protected_exceedance_probability[i]
                    ),
                }
            )
    out = pd.DataFrame(rows)
    out.attrs["n_participants"] = n_participants
    out.attrs["resample_size"] = draw_size
    return out


def summarize_bootstrap_bmc(boot_df: pd.DataFrame, *, model_col: str = "fit_model") -> pd.DataFrame:
    """Mean + 95% percentile interval per model from a
    :func:`bootstrap_model_comparison_bmc` table."""
    metrics = ("expected_frequency", "exceedance_probability", "protected_exceedance_probability")
    rows = []
    for model, sub in boot_df.groupby(model_col):
        row = {model_col: model, "n_boot": len(sub)}
        for metric in metrics:
            vals = sub[metric].to_numpy(dtype=float)
            row[f"{metric}_mean"] = float(np.mean(vals))
            row[f"{metric}_lo95"] = float(np.percentile(vals, 2.5))
            row[f"{metric}_hi95"] = float(np.percentile(vals, 97.5))
        rows.append(row)
    return pd.DataFrame(rows)

