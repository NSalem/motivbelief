"""
Stats on Bayesian individual meta-d′ fits (``results/hmeta_d/``).

For each participant × choiceType × incentive, we first fit
    meta-d′ ~ 1 + coh3
on the model-implied incentive × coh3 grid, giving per-participant intercept
(``beta0``, overall metacognitive sensitivity) and slope (``beta1``, its
coherence-dependence).

``beta0`` and ``beta1`` are then analyzed exactly like the average-level
behavioral outcomes in :mod:`motivbelief.stats.stats_avg` (accuracy, belief,
calibration, ...): per participant, regress the response variable onto
incentive (``y ~ 1 + incentive`` or, for signed −1/0/+1 designs,
``y ~ 1 + incentive + |incentive|``), then test the resulting participant-level
coefficients (``b0``, ``b_inc``, ``b_abs``) against zero at the sample level
(within-group one-sample t-tests; between-group Welch/paired t-tests; pairwise
paired t-tests across incentive levels; gain/loss correlation for −1/0/+1
designs). See :mod:`motivbelief.stats.stats_avg` for the shared implementation.

Outputs under ``results/stats/hmeta/<dataset>/``.

Usage:
  python -m motivbelief.stats.stats_hmeta
  python -m motivbelief.stats.stats_hmeta --dataset exp1a
"""

from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np
import pandas as pd

from motivbelief.stats.stats_avg import (
    compute_participant_coefs,
    get_gain_loss_corr_table,
    get_ttests_table,
    render_md_avg_summary,
    summarize_between_groups,
    summarize_within_group,
)

HMETA_DATASETS = ("exp1a", "exp1b", "exp2", "exp3")
COH3_LEVELS = (-1.0, 0.0, 1.0)
RESPVARS = ("beta0", "beta1")


def hmeta_fit_dir(repo: Path, dataset: str) -> Path:
    return repo.resolve() / "results" / "hmeta_d" / dataset


def load_json(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def load_preparation(repo: Path, dataset: str) -> dict:
    path = hmeta_fit_dir(repo, dataset) / "preparation.json"
    if path.is_file():
        return load_json(path)
    meta_path = hmeta_fit_dir(repo, dataset) / "meta.json"
    if meta_path.is_file():
        prep = load_json(meta_path).get("preparation")
        if isinstance(prep, dict):
            return prep
    raise FileNotFoundError(path)


def load_subject_summary(repo: Path, dataset: str) -> Optional[pd.DataFrame]:
    path = hmeta_fit_dir(repo, dataset) / "subject_summary.csv"
    if not path.is_file() or path.stat().st_size < 80:
        return None
    df = pd.read_csv(path)
    return None if df.empty or "param" not in df.columns else df


def _incentive_key(inc: float | str | int) -> float:
    return float(inc)


def _incentive_level_strings(prep: dict) -> List[str]:
    coding = prep.get("incentive_coding", {}) or {}
    levels = coding.get("levels") or coding.get("raw_levels") or []
    return [str(x) for x in levels]


def _param_map(summary_g: pd.DataFrame) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for r in summary_g.itertuples():
        if np.isfinite(r.mean):
            out[str(r.param)] = float(r.mean)
    return out


def subject_effective_meta_d(
    summary: pd.DataFrame,
    prep: dict,
    *,
    choice_type: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """
    Reconstruct subject-level model-implied meta-d′ on the incentive × coh3 grid.

    Treatment contrasts (reference = first incentive level):
      log M = Intercept + Σ β_k 1[inc=k] + (γ + Σ β_{k×c} 1[inc=k]) · coh3
      d′ = d′₀ + d′_c · coh3
      meta-d′ = exp(log M) · d′
    """
    df = summary.copy()
    if "choiceType" not in df.columns:
        df["choiceType"] = "Free"
    if choice_type is not None:
        df = df[df["choiceType"].astype(str) == str(choice_type)]
    if df.empty:
        return None
    inc_levels = _incentive_level_strings(prep)
    if len(inc_levels) < 2:
        return None
    ref = inc_levels[0]
    rows: List[dict] = []
    for (pid, ctype), g in df.groupby(["participant", "choiceType"], sort=False):
        p = _param_map(g)
        if "Intercept" not in p or "dprime_Intercept" not in p:
            continue
        for inc_s in inc_levels:
            for coh3 in COH3_LEVELS:
                logm = p.get("Intercept", np.nan) + p.get("coh3", 0.0) * float(coh3)
                if inc_s != ref:
                    b = p.get(f"incentive{inc_s}")
                    bc = p.get(f"incentive{inc_s}:coh3", 0.0)
                    if b is None or not np.isfinite(b):
                        continue
                    logm = logm + float(b) + float(bc) * float(coh3)
                if not np.isfinite(logm):
                    continue
                dp = p.get("dprime_Intercept", np.nan) + p.get("dprime_coh3", 0.0) * float(coh3)
                if not np.isfinite(dp):
                    continue
                rows.append(
                    {
                        "participant": str(pid),
                        "choiceType": str(ctype),
                        "incentive": _incentive_key(inc_s),
                        "coh3": float(coh3),
                        "meta_d": float(np.exp(logm) * dp),
                    }
                )
    return pd.DataFrame(rows) if rows else None


def fit_coh_regressions(meta_df: pd.DataFrame) -> pd.DataFrame:
    """Per participant × choiceType × incentive: meta_d ~ 1 + coh3 -> beta0, beta1."""
    rows: List[dict] = []
    keys = ["participant", "choiceType", "incentive"]
    for key, g in meta_df.groupby(keys, sort=False):
        pid, ctype, inc = key
        g = g.dropna(subset=["meta_d", "coh3"])
        if len(g) < 2:
            continue
        x = g["coh3"].to_numpy(dtype=float)
        y = g["meta_d"].to_numpy(dtype=float)
        X = np.column_stack([np.ones(len(x)), x])
        try:
            coef, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
        except np.linalg.LinAlgError:
            continue
        rows.append(
            {
                "participant": str(pid),
                "choiceType": str(ctype),
                "incentive": float(inc),
                "beta0": float(coef[0]),
                "beta1": float(coef[1]),
                "n_coh": int(len(g)),
            }
        )
    return pd.DataFrame(rows)


def run_one_dataset(repo: Path, dataset: str, out_root: Path) -> Optional[Path]:
    try:
        prep = load_preparation(repo, dataset)
    except FileNotFoundError:
        warnings.warn(f"stats_hmeta: missing preparation for {dataset}; skip")
        return None
    summary = load_subject_summary(repo, dataset)
    if summary is None:
        warnings.warn(f"stats_hmeta: missing subject_summary for {dataset}; skip")
        return None

    meta_grid = subject_effective_meta_d(summary, prep)
    if meta_grid is None or meta_grid.empty:
        warnings.warn(f"stats_hmeta: no effective meta-d′ for {dataset}; skip")
        return None

    fits = fit_coh_regressions(meta_grid)
    if fits.empty:
        warnings.warn(f"stats_hmeta: no coh regressions for {dataset}; skip")
        return None

    out_dir = out_root / dataset
    out_dir.mkdir(parents=True, exist_ok=True)
    meta_grid.to_csv(out_dir / "meta_d_grid.csv", index=False)
    fits.to_csv(out_dir / "coh_fits.csv", index=False)

    inc_vals = pd.to_numeric(fits["incentive"], errors="coerce").dropna().unique().tolist()

    def _has_inc(t: float) -> bool:
        return any(abs(float(v) - t) < 1e-9 for v in inc_vals)

    has_signed_design = _has_inc(-1.0) and _has_inc(0.0) and _has_inc(1.0)

    for respvar in RESPVARS:
        coef_df, compute_abs, inc_levels = compute_participant_coefs(
            fits,
            y_col=respvar,
            inc_col="incentive",
            participant_col="participant",
            group_col="choiceType",
        )
        coef_df.to_csv(out_dir / f"sub_effects__{dataset}__{respvar}.csv", index=False, na_rep="")

        within_tbl = summarize_within_group(coef_df, respvar=respvar, group_col="choiceType")
        within_tbl.to_csv(out_dir / f"within_summary__{dataset}__{respvar}.csv", index=False, na_rep="")

        between_tbl = summarize_between_groups(coef_df, group_col="choiceType")
        between_tbl.to_csv(out_dir / f"between_summary__{dataset}__{respvar}.csv", index=False, na_rep="")

        ttests_tbl = get_ttests_table(
            fits,
            respvar=respvar,
            group_col="choiceType",
            participant_col="participant",
            inc_col="incentive",
        )
        ttests_tbl.to_csv(out_dir / f"ttests_incentives__{dataset}__{respvar}.csv", index=False, na_rep="")

        if has_signed_design:
            corr_tbl = get_gain_loss_corr_table(
                fits,
                respvar=respvar,
                group_col="choiceType",
                participant_col="participant",
                inc_col="incentive",
            )
            corr_tbl.to_csv(out_dir / f"gain_loss_corr__{dataset}__{respvar}.csv", index=False, na_rep="")
        else:
            corr_tbl = pd.DataFrame()

        md = render_md_avg_summary(
            stem=f"{dataset} | meta-d′ AVG-style stats",
            respvar=respvar,
            meta={"compute_abs": compute_abs, "inc_levels": inc_levels},
            within_tbl=within_tbl,
            between_tbl=between_tbl,
            ttests_tbl=ttests_tbl,
            corr_tbl=corr_tbl,
        )
        (out_dir / f"summary__{dataset}__{respvar}.md").write_text(md, encoding="utf-8")

    print(f"[{dataset}] wrote {out_dir}", flush=True)
    return out_dir


def available_hmeta_datasets(repo: Path, wanted: Sequence[str] = HMETA_DATASETS) -> List[str]:
    out = []
    for ds in wanted:
        if (hmeta_fit_dir(repo, ds) / "subject_summary.csv").is_file():
            out.append(ds)
    return out


def main(argv: Optional[Sequence[str]] = None) -> None:
    ap = argparse.ArgumentParser(
        description="Stats on hmeta_d effective meta-d′ (beta0/beta1 coh regressions, AVG-style incentive tests)."
    )
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument(
        "--out-root",
        type=Path,
        default=None,
        help="Default: <repo>/results/stats/hmeta",
    )
    ap.add_argument("--dataset", type=str, default=None, help="Single dataset (default: all available)")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    out_root = (args.out_root if args.out_root is not None else repo / "results" / "stats" / "hmeta")
    out_root = out_root if out_root.is_absolute() else (repo / out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    datasets = [args.dataset] if args.dataset else available_hmeta_datasets(repo)
    if not datasets:
        print("No hmeta_d subject_summary outputs found; nothing to do.", flush=True)
        return
    for ds in datasets:
        run_one_dataset(repo, ds, out_root)


if __name__ == "__main__":
    main()
