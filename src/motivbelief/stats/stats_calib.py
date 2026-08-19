"""
Mixed-effects analysis of confidence–accuracy calibration curves.

On subject × coherence × incentive cells (same aggregation as the calib figures):

    conf ~ acc_c * incentive + (… | participant)

``acc_c`` is accuracy centered within group (Free / Non-Free). Linear ``incentive``
(−1 / 0 / +1) matches the average-level incentive coding.

Main ``incentive``: vertical curve shift at mean accuracy.
``acc_c:incentive``: does incentive change the calibration slope (curve fan).
"""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from motivbelief.modeling.io import COH_LEVELS, load_merged_human_trials
from motivbelief.plotting.style import INC_LEVELS

# Progressive random-effect structures (richest first). Full acc*incentive RE is
# often singular on these cell counts; we fall back until one converges.
RE_FORMULAS: Tuple[str, ...] = (
    "~ acc_c * incentive",
    "~ acc_c + incentive",
    "~ incentive",
    "~ 1",
)


def subject_calib_cells(
    df: pd.DataFrame,
    *,
    allowed_incentives: Sequence[float] | None = INC_LEVELS,
) -> pd.DataFrame:
    """Per subject × coh × incentive: accuracy and mean confidence."""
    d = df.copy()
    if "coh" not in d.columns:
        d["coh"] = np.abs(d["stim"].astype(float))
    else:
        d["coh"] = np.abs(d["coh"].astype(float))
    d["incentive"] = d["incentive"].astype(float)
    d["correct"] = d["correct"].astype(int)
    d = d[d["coh"].isin(COH_LEVELS)]
    if allowed_incentives is not None:
        d = d[d["incentive"].isin(list(allowed_incentives))]
    if d.empty:
        return pd.DataFrame()

    rows = []
    for (pid, coh, inc), g in d.groupby(["participant", "coh", "incentive"]):
        rows.append(
            {
                "participant": str(pid),
                "coh": float(coh),
                "incentive": float(inc),
                "acc": float(g["correct"].mean()),
                "conf": float(g["conf"].mean()),
                "n_trials": int(len(g)),
            }
        )
    return pd.DataFrame(rows)


def prepare_group_cells(cells: pd.DataFrame, group: str) -> pd.DataFrame:
    """Drop non-finite rows and center accuracy within the analysis group."""
    d = cells.copy()
    d["group"] = group
    d = d[np.isfinite(d["acc"]) & np.isfinite(d["conf"]) & np.isfinite(d["incentive"])]
    d = d.reset_index(drop=True)
    d["acc_c"] = d["acc"] - d["acc"].mean()
    return d


def fit_calib_mixedlm(
    cells: pd.DataFrame,
    *,
    re_formulas: Sequence[str] = RE_FORMULAS,
) -> Tuple[Any, str]:
    """
    Fit ``conf ~ acc_c * incentive`` with mixed effects.

    Returns ``(result, re_formula_used)``.
    """
    if cells["participant"].nunique() < 3 or len(cells) < 10:
        raise ValueError(f"Too few cells/subjects for MixedLM (n={len(cells)})")

    last_err: Optional[Exception] = None
    for re_f in re_formulas:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = smf.mixedlm(
                    "conf ~ acc_c * incentive",
                    cells,
                    groups=cells["participant"],
                    re_formula=re_f,
                )
                # reml=True is default; lbfgs is more stable than powell here
                result = model.fit(method="lbfgs", reml=True, maxiter=500, disp=False)
            if not np.isfinite(result.llf):
                raise RuntimeError("non-finite llf")
            if not bool(getattr(result, "converged", True)):
                raise RuntimeError("optimizer did not converge")
            return result, re_f
        except Exception as exc:  # noqa: BLE001 — try next RE structure
            last_err = exc
            continue
    raise RuntimeError(f"MixedLM failed for all RE formulas; last error: {last_err}")


def _coef_table(result: Any, group: str, re_formula: str, n_subj: int, n_cells: int) -> pd.DataFrame:
    rows = []
    fe = result.fe_params
    bse = result.bse_fe
    # statsmodels MixedLMResults has pvalues for FE
    pvals = result.pvalues
    for name in fe.index:
        rows.append(
            {
                "group": group,
                "term": name,
                "estimate": float(fe[name]),
                "se": float(bse[name]),
                "z": float(fe[name] / bse[name]) if bse[name] else np.nan,
                "p": float(pvals.get(name, np.nan)),
                "re_formula": re_formula,
                "n_subjects": n_subj,
                "n_cells": n_cells,
                "converged": bool(getattr(result, "converged", True)),
                "llf": float(result.llf),
            }
        )
    return pd.DataFrame(rows)


def run_merged_calib_mixedlm(repo_root: Path, out_dir: Path) -> pd.DataFrame:
    """Fit Free and Non-Free on merged human cells; write CSV + markdown."""
    repo_root = repo_root.resolve()
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    trials = load_merged_human_trials(repo_root)
    tables: List[pd.DataFrame] = []
    summaries: List[str] = [
        "# Calibration mixed-effects (merged data)",
        "",
        "Model: `conf ~ acc_c * incentive + (RE | participant)`",
        "Cells: subject × coherence × incentive (pooled correct/error).",
        "`acc_c` = accuracy centered within Free / Non-Free.",
        "`incentive` coded linearly (−1, 0, +1).",
        "",
    ]

    for group in ("Free", "Non-Free"):
        gtrials = trials[trials["choiceType"].astype(str) == group]
        cells = prepare_group_cells(subject_calib_cells(gtrials), group)
        cells.to_csv(out_dir / f"cells_calib_{group.replace('-', '').lower()}.csv", index=False)

        result, re_f = fit_calib_mixedlm(cells)
        tab = _coef_table(
            result,
            group,
            re_f,
            n_subj=int(cells["participant"].nunique()),
            n_cells=len(cells),
        )
        tables.append(tab)

        summaries.append(f"## {group}")
        summaries.append("")
        summaries.append(f"- Subjects: {cells['participant'].nunique()}")
        summaries.append(f"- Cells: {len(cells)}")
        summaries.append(f"- RE formula used: `{re_f}`")
        summaries.append(f"- Converged: {bool(getattr(result, 'converged', True))}")
        summaries.append(f"- LLF: {result.llf:.2f}")
        summaries.append("")
        summaries.append("| term | estimate | SE | z | p |")
        summaries.append("|---|---:|---:|---:|---:|")
        for _, r in tab.iterrows():
            summaries.append(
                f"| `{r['term']}` | {r['estimate']:.4f} | {r['se']:.4f} | {r['z']:.2f} | {r['p']:.4g} |"
            )
        summaries.append("")

        # Keep a text dump of the full statsmodels summary for debugging
        with open(out_dir / f"mixedlm_{group.replace('-', '').lower()}.txt", "w", encoding="utf-8") as f:
            f.write(str(result.summary()))

    out = pd.concat(tables, ignore_index=True)
    out.to_csv(out_dir / "mixedlm_fe_coefs.csv", index=False)
    (out_dir / "mixedlm_summary.md").write_text("\n".join(summaries) + "\n", encoding="utf-8")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Calibration conf~acc×incentive mixed-effects.")
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Default: <repo>/results/stats/calib",
    )
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    out_dir = args.out_dir or (repo / "results" / "stats" / "calib")
    tab = run_merged_calib_mixedlm(repo, out_dir)
    print(tab.to_string(index=False))
    print(f"\nWrote {out_dir / 'mixedlm_fe_coefs.csv'}")
    print(f"Wrote {out_dir / 'mixedlm_summary.md'}")


if __name__ == "__main__":
    main()
