# -*- coding: utf-8 -*-
"""Shared per-(experiment, condition) confidence-model fitting loop.

Used by ``scripts/fit_conf_free.py`` for the paper's Free confidence fits.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from motivbelief.modeling.conf_ll import fit_conf_bads, make_conf_modelinfo
from motivbelief.modeling.io import (
    FitPaths,
    resolve_fit_paths,
    save_fit_diagnostics,
    save_fit_metadata,
    save_fit_results,
)

# Free/Replayed: sens_noise/sens_bias/p_lapse from a standalone choice fit.
# Observed/Forced: those are fit jointly with confidence params.
JOINT_CHOICE_PARNAMES = ["sens_noise", "sens_bias", "p_lapse"]


def fit_confidence_variant(
    *,
    iexp: str,
    df_group: pd.DataFrame,
    model: Dict[str, Any],
    out_dir: Path,
    stem: str,
    choice_pars: Optional[Dict[int, Dict[str, float]]],
    condition_is_free: bool,
    mismatch_coef: Optional[float | str] = None,
    min_trials: int = 20,
    n_mc: int = 500,
    n_restarts: int = 3,
    kernel_bw: float = 5.0,
    n_jobs: int = 3,
    use_x0: bool = True,
    max_fun_evals: int = 500,
    priors: Optional[Dict[str, tuple]] = None,
) -> FitPaths:
    """Fit one confidence-model variant for one (experiment, condition).

    ``choice_pars``: per-participant sens_noise/sens_bias/p_lapse for
    Free/Replayed. Pass ``None`` for Observed/Forced (joint choice params).

    ``mismatch_coef``: if given, fixes that nuisance (see ``conf_core.confidence_core``).

    ``priors``: same ``{name: (kind, *args)}`` format as
    ``optimize.DEFAULT_CONF_PRIORS`` (used when ``None``).
    """
    choice_backed = choice_pars is not None
    parnames_base = list(model["parnames"])
    parnames_full = parnames_base if choice_backed else JOINT_CHOICE_PARNAMES + parnames_base

    modelinfo = make_conf_modelinfo(parnames_full)
    fixedpars = dict(model.get("fixedpars", {}))
    if mismatch_coef is not None:
        fixedpars["mismatch_coef"] = mismatch_coef
    modelinfo["cfg"]["fixedpars"] = fixedpars

    parnames = modelinfo["cfg"]["parnames"]

    if choice_backed:
        participants = list(choice_pars.items())
    else:
        subs = sorted(int(p) for p in df_group["participant"].dropna().unique())
        participants = [(isub, None) for isub in subs]

    rows = []
    diagnostics: Dict[int, Dict[str, Any]] = {}
    nsubs_total = len(participants)
    for nsub, (isub, choice_row) in enumerate(participants, start=1):
        print(f"\n== Fitting participant {isub} ({nsub}/{nsubs_total}) ==")

        dfsub = df_group[df_group["participant"] == isub][
            ["stim", "a", "conf", "incentive"]
        ].dropna()
        if len(dfsub) < min_trials:
            continue

        if choice_backed:
            sens_noise = choice_row["sens_noise"]
            sens_bias = choice_row["sens_bias"]
            p_lapse = choice_row["p_lapse"]
        else:
            # Placeholders; joint params are already in parnames_full.
            sens_noise, sens_bias, p_lapse = 0.0, 0.0, 0.0

        fit_kw = dict(
            sens_noise=sens_noise,
            sens_bias=sens_bias,
            p_lapse=p_lapse,
            condition_is_free=condition_is_free,
            n_mc=n_mc,
            n_restarts=n_restarts,
            kernel_bw=kernel_bw,
            seed=isub,
            use_x0=use_x0,
            max_fun_evals=max_fun_evals,
            priors=priors,
        )

        t0 = time.perf_counter()
        x_bads, ll_bads = fit_conf_bads(modelinfo, dfsub, n_jobs=n_jobs, **fit_kw)
        dt_bads = time.perf_counter() - t0

        row = {"participant": isub, "ll": ll_bads, "n_trials": len(dfsub)}
        row.update(zip(parnames, x_bads))
        rows.append(row)

        diagnostics[int(isub)] = {"n_trials": len(dfsub), "time_sec": dt_bads}

        par_str = ", ".join(f"{p}={v:.3f}" for p, v in zip(parnames, x_bads))
        print(f"BADS took {dt_bads:.1f}s: {par_str}")

    bounds_dict = {
        "lower": modelinfo.get("bounds", [[], []])[0],
        "upper": modelinfo.get("bounds", [[], []])[1],
        "plausible_lower": modelinfo.get("plb", []),
        "plausible_upper": modelinfo.get("pub", []),
    }
    model_spec_extra = {"evidence_treatment": "offset"}
    fitting_config_dict = {
        "optimizer": "BADS",
        "n_restarts": n_restarts,
        "n_jobs": n_jobs,
        "n_mc": n_mc,
        "kernel_bw": kernel_bw,
        "max_fun_evals": max_fun_evals,
        "likelihood": "conf_ll_binned",
        "priors": "default" if priors is None else "custom",
    }

    paths = resolve_fit_paths(out_dir, iexp, stem)
    save_fit_metadata(
        paths,
        parnames=parnames,
        bounds=bounds_dict,
        fixed_pars=fixedpars,
        model_spec_extra=model_spec_extra,
        fitting_config=fitting_config_dict,
    )
    save_fit_results(paths, pd.DataFrame(rows))
    save_fit_diagnostics(paths, diagnostics)

    print(f"\nSaved to {paths.results_dir}")
    print(f"  {paths.metadata_path.name}")
    print(f"  {paths.results_path.name}")
    print(f"  {paths.diagnostics_path.name}")
    return paths
