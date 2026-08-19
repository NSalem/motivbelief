"""Data loading and fit results I/O."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

_INCENTIVE_CANDIDATES = ["incentive", "incentive_abs", "inc", "stake", "reward"]

DEFAULT_CHOICE_PARS_DIR = os.path.join("results", "modeling", "fits_choice")

# The 5 coherence levels used across experiments (also referenced as the
# positive half of choice.py-adjacent stimulus-level constants).
COH_LEVELS = (1.0, 3.0, 5.0, 9.0, 38.0)

SIM_STEM_TO_FILE = {
    "sim_act": "sims_act.csv",
    "sim_intent": "sims_intent.csv",
    "sim_confirm": "sims_confirm.csv",
}


def _find_incentive_col(df: pd.DataFrame) -> str | None:
    for c in _INCENTIVE_CANDIDATES:
        if c in df.columns:
            return c
    return None


def load_exp_df(iexp: str, data_dir: str = "data") -> pd.DataFrame:
    """Load and preprocess one experiment's trial CSV.

    Drops no-confidence trials, derives ``a`` (response as +-1) and ``stim``
    (signed coherence), and normalizes the incentive column name to
    ``"incentive"`` if present under a different name.
    """
    df = pd.read_csv(os.path.join(data_dir, f"data_{iexp}.csv"))
    df = df[~pd.isna(df["conf"])].copy()
    df["correct"] = df["correct"].astype(int)

    df["a"] = (df["resp"] == "right") * 1 + (df["resp"] == "left") * -1
    side = df["dir"].replace({"right": 1, "left": -1})
    df["stim"] = df["coh"].to_numpy() * side.to_numpy()

    inc_col = _find_incentive_col(df)
    if inc_col is not None and inc_col != "incentive":
        df = df.rename(columns={inc_col: "incentive"})
    return df


def load_merged_human_trials(repo: Path) -> pd.DataFrame:
    """exp1a + exp2 Free + exp3, with choiceType remapped to Free/Non-Free."""
    parts = []
    for exp, tag in (("exp1a", "Exp1a"), ("exp2", "Exp2"), ("exp3", "Exp3")):
        df = load_exp_df(exp, data_dir=str(repo / "data"))
        df = df.copy()
        df["participant"] = tag + "_" + df["participant"].astype(str)
        df["experiment"] = exp
        if exp == "exp2":
            df = df[df["choiceType"].astype(str) == "Free"].copy()
        parts.append(df)
    out = pd.concat(parts, ignore_index=True)
    out["choiceType"] = np.where(out["choiceType"].astype(str) == "Free", "Free", "Non-Free")
    out["group"] = out["choiceType"]
    return out


def load_sim_trials(repo: Path, stem: str) -> pd.DataFrame:
    """Load one belief-simulation CSV (see ``scripts/simulate_belief.py``), remapped like above."""
    fname = SIM_STEM_TO_FILE.get(stem)
    if fname is None:
        raise KeyError(f"Unknown sim stem {stem!r}")
    path = repo / "results" / "sims" / fname
    df = pd.read_csv(path)
    df = df.copy()
    df["participant"] = f"Sims {stem}_" + df["participant"].astype(str)
    df["choiceType"] = np.where(df["choiceType"].astype(str) == "Free", "Free", "Non-Free")
    df["group"] = df["choiceType"]
    if "coh" not in df.columns and "stim" in df.columns:
        df["coh"] = np.abs(df["stim"].astype(float))
    return df


def load_choice_pars_csv(
    iexp: str, igroup: str, choice_dir: str = DEFAULT_CHOICE_PARS_DIR
) -> dict[int, dict[str, float]]:
    """Per-participant ``sens_noise``/``sens_bias``/``p_lapse`` from a choice-model fit CSV."""
    path = os.path.join(choice_dir, iexp, f"results_{igroup}.csv")
    df = pd.read_csv(path)
    return {
        int(row["participant"]): {
            "sens_noise": float(row["sens_noise"]),
            "sens_bias": float(row["sens_bias"]),
            "p_lapse": float(row["p_lapse"]),
        }
        for _, row in df.iterrows()
    }


@dataclass
class FitPaths:
    """Resolved on-disk paths for one fit (one stem under one experiment folder)."""

    results_dir: Path
    metadata_path: Path
    results_path: Path
    diagnostics_path: Path


def resolve_fit_paths(outdir: Path, exp: str, stem: str) -> FitPaths:
    """Resolve (and create) paths for one fit's results/metadata/diagnostics."""
    results_dir = Path(outdir) / exp
    results_dir.mkdir(parents=True, exist_ok=True)
    return FitPaths(
        results_dir=results_dir,
        metadata_path=results_dir / f"{stem}.metadata.json",
        results_path=results_dir / f"{stem}.csv",
        diagnostics_path=results_dir / f"{stem}.fitting_log.json",
    )



def save_fit_metadata(
    paths: FitPaths,
    parnames: List[str],
    bounds: Dict[str, List[float]],
    fixed_pars: Optional[Dict[str, float]] = None,
    model_spec_extra: Optional[Dict[str, Any]] = None,
    fitting_config: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Save model metadata and fitting configuration.

    Parameters
    ----------
    parnames : list
        Parameter names
    bounds : dict
        Bounds dict with keys "lower", "upper", "plausible_lower", "plausible_upper"
    fixed_pars : dict, optional
        Fixed parameters (default: empty dict)
    model_spec_extra : dict, optional
        Additional model-specific fields (e.g., evidence_treatment)
    fitting_config : dict, optional
        Fitting hyperparameters (e.g., optimizer, n_restarts, max_fun_evals)
    """
    if fixed_pars is None:
        fixed_pars = {}
    if model_spec_extra is None:
        model_spec_extra = {}
    if fitting_config is None:
        fitting_config = {}

    model_spec = {
        "parnames": parnames,
        "bounds": bounds,
        "fixed_pars": fixed_pars,
    }
    model_spec.update(model_spec_extra)

    metadata = {
        "model_spec": model_spec,
        "fitting_config": fitting_config,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    with open(paths.metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)


def save_fit_results(paths: FitPaths, df_results: pd.DataFrame) -> None:
    """Save per-participant results CSV with AICc from ``analysis_free.compute_information_criteria``."""
    from motivbelief.modeling.analysis_free import compute_information_criteria

    df = df_results.copy()

    # Load parnames from metadata to compute AICc
    if paths.metadata_path.exists():
        with open(paths.metadata_path) as f:
            metadata = json.load(f)
        parnames = metadata["model_spec"]["parnames"]
        k = len(parnames)
    else:
        raise FileNotFoundError(f"Metadata not found at {paths.metadata_path}. Save metadata first.")

    df["_n_params"] = k
    df = compute_information_criteria(df, ll_col="ll", n_col="n_trials", k_col="_n_params")
    df = df.rename(columns={"aicc": "AICc"}).drop(columns=["bic", "_n_params"])

    # Ensure columns are in standard order
    standard_cols = ["participant"]
    if "incentive" in df.columns:
        # Put incentive after participant for incentive-specific fits
        standard_cols.append("incentive")

    standard_cols.extend(parnames)
    standard_cols.extend(["ll", "AICc", "n_trials"])

    # Keep only standard cols that exist
    cols_to_keep = [c for c in standard_cols if c in df.columns]
    df = df[cols_to_keep]

    df.to_csv(paths.results_path, index=False)


def save_fit_diagnostics(paths: FitPaths, diagnostics_dict: Dict[int, Dict[str, Any]]) -> None:
    """
    Save per-participant fitting diagnostics.

    Parameters
    ----------
    diagnostics_dict : dict
        Mapping participant ID → dict of diagnostics
        Example: {1: {"n_trials": 150, "time_sec": 45.2, "n_function_evals": 1234, "converged": True}}
    """
    with open(paths.diagnostics_path, "w") as f:
        json.dump(diagnostics_dict, f, indent=2)


def load_fit_metadata(metadata_path: Path) -> Dict[str, Any]:
    """
    Load a `<stem>.metadata.json` file and return structured metadata.

    Returns
    -------
    dict
        Keys: model_spec (dict), fitting_config (dict), timestamp (str)
    """
    with open(metadata_path) as f:
        return json.load(f)
