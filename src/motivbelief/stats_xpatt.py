"""
Trial-level confidence (xpatt) OLS, group tests, CSV/Markdown writers.

Reads the same behavioural CSVs as ``stats_avg`` via ``build_analysis_specs``. Fits
per-participant models (e.g. ``conf ~ incentive * correct * difficulty``) and writes
``sample_xpatt_*.csv``, coefficient summaries, and tests under ``<out-root>/<stem>/``.
Default ``--out-root`` is ``results/stats/trial``.
"""

from __future__ import annotations

import argparse
import itertools
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats


LEVELS_DIFFICULTY = [-0.5, 0.0, 0.5]
EPS_RT = 1e-3
UMINUS = "\u2212"  

EFFECT_CODES = [
    "intercept_corr",
    "intercept_err",
    "logRT_z",
    "difficulty_corr",
    "difficulty_err",
    "incentive_corr",
    "incentive_err",
    "incdiff_corr",
    "incdiff_err",
]

EFFECT_LABELS = {
    "intercept_corr": "(Intercept)|Correct",
    "intercept_err": "(Intercept)|Error",
    "difficulty": "Difficulty",
    "incentive": "Incentive",
    "logRT_z": "z(log(RT))",
    "difficulty_corr": "Difficulty|Correct",
    "difficulty_err": "Difficulty|Error",
    "incdiff": "Incentive×Difficulty",
    "incentive_corr": "Incentive|Correct",
    "incentive_err": "Incentive|Error",
    "incdiff_corr": "Incentive×Difficulty|Correct",
    "incdiff_err": "Incentive×Difficulty|Error",
}

GROUP_LEVELS = ["Free", "Non-Free", "Observed", "Forced", "Replayed"]

COL_NAMES_BASE = [
    "correctFError",
    "correctFCorrect",
    "correctFError:incentive",
    "correctFCorrect:incentive",
    "correctFError:difficulty",
    "correctFCorrect:difficulty",
    "correctFError:incentive:difficulty",
    "correctFCorrect:incentive:difficulty",
]


def _fit_ordered_ls(y: np.ndarray, X: np.ndarray, names: List[str]) -> Dict[str, float]:
    """
    R-like aliasing: keep columns by term order if they increase rank,
    fit only kept columns, mark dropped columns as NaN.
    """
    kept_idx: List[int] = []
    rank_cur = 0
    for j in range(X.shape[1]):
        cand_idx = kept_idx + [j]
        rank_new = np.linalg.matrix_rank(X[:, cand_idx])
        if rank_new > rank_cur:
            kept_idx.append(j)
            rank_cur = rank_new

    coef = {nm: np.nan for nm in names}
    if kept_idx:
        beta_kept, *_ = np.linalg.lstsq(X[:, kept_idx], y, rcond=None)
        for b, j in zip(beta_kept, kept_idx):
            coef[names[j]] = float(b)
    return coef


def _design_matrix(inc: np.ndarray, diff: np.ndarray, is_error: np.ndarray) -> np.ndarray:
    Ie = is_error.astype(float)
    Ic = (~is_error).astype(float)
    return np.column_stack(
        [
            Ie,
            Ic,
            Ie * inc,
            Ic * inc,
            Ie * diff,
            Ic * diff,
            Ie * inc * diff,
            Ic * inc * diff,
        ]
    )


def _fit_xpatt_outcome(dsub: pd.DataFrame, outcome: str) -> Optional[sm.regression.linear_model.RegressionResultsWrapper]:
    d = dsub.copy()
    d["incentive"] = pd.to_numeric(d["incentive"], errors="coerce")
    d["difficulty"] = pd.to_numeric(d["difficulty"], errors="coerce")
    d["correctF"] = pd.Categorical(d["correctF"], categories=["Error", "Correct"], ordered=True)
    y = pd.to_numeric(d[outcome], errors="coerce")
    inc = d["incentive"].to_numpy(dtype=float)
    diff = d["difficulty"].to_numpy(dtype=float)
    is_err = d["correctF"].astype(str).to_numpy() == "Error"
    ok = np.isfinite(y.to_numpy()) & np.isfinite(inc) & np.isfinite(diff) & d["correctF"].notna().to_numpy()
    if ok.sum() < 3:
        return None
    yv = y.to_numpy(dtype=float)[ok]
    inc_ok = inc[ok]
    diff_ok = diff[ok]
    err_ok = is_err[ok]
    X = _design_matrix(inc_ok, diff_ok, err_ok)
    res = sm.OLS(yv, X).fit()
    res._exog_names = COL_NAMES_BASE  # type: ignore[attr-defined]
    res._coef_map = _fit_ordered_ls(yv, X, COL_NAMES_BASE)  # type: ignore[attr-defined]
    return res


def _fit_xpatt_conf_ctrlrt(dsub: pd.DataFrame) -> Optional[sm.regression.linear_model.RegressionResultsWrapper]:
    d = dsub.copy()
    d["incentive"] = pd.to_numeric(d["incentive"], errors="coerce")
    d["difficulty"] = pd.to_numeric(d["difficulty"], errors="coerce")
    d["log_rt_z"] = pd.to_numeric(d["log_rt_z"], errors="coerce")
    d["correctF"] = pd.Categorical(d["correctF"], categories=["Error", "Correct"], ordered=True)
    conf = pd.to_numeric(d["conf"], errors="coerce")
    inc = d["incentive"].to_numpy(dtype=float)
    diff = d["difficulty"].to_numpy(dtype=float)
    zrt = d["log_rt_z"].to_numpy(dtype=float)
    is_err = d["correctF"].astype(str).to_numpy() == "Error"
    ok = (
        np.isfinite(conf.to_numpy())
        & np.isfinite(zrt)
        & np.isfinite(inc)
        & np.isfinite(diff)
        & d["correctF"].notna().to_numpy()
    )
    if ok.sum() < 3:
        return None
    yv = conf.to_numpy(dtype=float)[ok]
    inc_ok = inc[ok]
    diff_ok = diff[ok]
    zrt_ok = zrt[ok]
    err_ok = is_err[ok]
    Xb = _design_matrix(inc_ok, diff_ok, err_ok)
    X = np.column_stack([Xb, zrt_ok])
    names = COL_NAMES_BASE + ["log_rt_z"]
    res = sm.OLS(yv, X).fit()
    res._exog_names = names  # type: ignore[attr-defined]
    res._coef_map = _fit_ordered_ls(yv, X, names)  # type: ignore[attr-defined]
    return res


def _b(res: sm.regression.linear_model.RegressionResultsWrapper, name: str) -> float:
    cmap = getattr(res, "_coef_map", None)
    if isinstance(cmap, dict) and name in cmap:
        val = cmap[name]
        return float(val) if np.isfinite(val) else np.nan
    names = getattr(res, "_exog_names", COL_NAMES_BASE)
    params = res.params
    if name in names:
        i = names.index(name)
        return float(params[i])
    return 0.0


def extract_effects_xpatt(res: sm.regression.linear_model.RegressionResultsWrapper, has_logrt: bool) -> Dict[str, float]:
    intercept_err = _b(res, "correctFError")
    intercept_corr = _b(res, "correctFCorrect")
    incentive_err = _b(res, "correctFError:incentive")
    incentive_corr = _b(res, "correctFCorrect:incentive")
    difficulty_err = _b(res, "correctFError:difficulty")
    difficulty_corr = _b(res, "correctFCorrect:difficulty")
    incdiff_err = _b(res, "correctFError:incentive:difficulty")
    incdiff_corr = _b(res, "correctFCorrect:incentive:difficulty")
    logrt = _b(res, "log_rt_z") if has_logrt else float("nan")
    # Aliasing is encoded directly in _coef_map from ordered fit.

    return {
        "intercept_corr": float(intercept_corr) if np.isfinite(intercept_corr) else np.nan,
        "intercept_err": float(intercept_err) if np.isfinite(intercept_err) else np.nan,
        "logRT_z": float(logrt) if np.isfinite(logrt) else np.nan,
        "difficulty_corr": float(difficulty_corr) if np.isfinite(difficulty_corr) else np.nan,
        "difficulty_err": float(difficulty_err) if np.isfinite(difficulty_err) else np.nan,
        "incentive_corr": float(incentive_corr) if np.isfinite(incentive_corr) else np.nan,
        "incentive_err": float(incentive_err) if np.isfinite(incentive_err) else np.nan,
        "incdiff_corr": float(incdiff_corr) if np.isfinite(incdiff_corr) else np.nan,
        "incdiff_err": float(incdiff_err) if np.isfinite(incdiff_err) else np.nan,
    }


def _predict_xpatt(res: sm.regression.linear_model.RegressionResultsWrapper, grid: pd.DataFrame) -> np.ndarray:
    names = getattr(res, "_exog_names", COL_NAMES_BASE)
    inc = grid["incentive"].to_numpy(dtype=float)
    diff = grid["difficulty"].to_numpy(dtype=float)
    is_err = grid["correctF"].astype(str).to_numpy() == "Error"
    X = _design_matrix(inc, diff, is_err)
    if len(names) > X.shape[1]:
        # ctrl-RT model: append log_rt_z from grid
        X = np.column_stack([X, grid["log_rt_z"].to_numpy(dtype=float)])
    coef = res.params
    return (X @ coef).astype(float)


def recode_vars(df: pd.DataFrame, experiment_name: str = "") -> pd.DataFrame:
    out = df.copy()
    out["experiment"] = experiment_name
    out["coh"] = np.round(pd.to_numeric(out["coh"], errors="coerce")).astype("Int64").astype(float)
    cor = pd.to_numeric(out["correct"], errors="coerce")
    out["correct"] = np.where(cor == 0, -0.5, np.where(cor == 1, 0.5, np.nan))
    out["correctF"] = np.where(out["correct"] > 0, "Correct", "Error")
    out["conf"] = np.round(pd.to_numeric(out["conf"], errors="coerce"))
    cmap = {
        "Free": "Free",
        "Observed": "Observed",
        "Forced": "Forced",
        "Replayed": "Replayed",
        "Non-Free": "Non-Free",
    }
    out["group"] = out["choiceType"].astype(str).map(cmap)
    if out["group"].isna().any():
        bad = out.loc[out["group"].isna(), "choiceType"].dropna().unique().tolist()
        raise ValueError(f"Unmapped choiceType for group: {bad}")

    def _diff(coh: float) -> Optional[float]:
        if coh in (1, 3):
            return LEVELS_DIFFICULTY[0]
        if coh == 5:
            return LEVELS_DIFFICULTY[1]
        if coh in (9, 38):
            return LEVELS_DIFFICULTY[2]
        return None

    out["difficulty"] = out["coh"].map(_diff)
    if out["difficulty"].isna().any():
        bad = out.loc[out["difficulty"].isna(), "coh"].dropna().unique().tolist()
        raise ValueError(f"Unmapped coherence levels: {bad}")

    out["group"] = pd.Categorical(out["group"], categories=GROUP_LEVELS, ordered=True)

    if "rt" in out.columns:
        rt = pd.to_numeric(out["rt"], errors="coerce")
        out["log_rt"] = np.log(rt + EPS_RT)

        def _z(s: pd.Series) -> pd.Series:
            m = float(s.mean())
            sdv = float(s.std(ddof=1)) if len(s) > 1 else 0.0
            if sdv == 0 or not np.isfinite(sdv):
                return pd.Series(0.0, index=s.index)
            return (s - m) / sdv

        out["log_rt_z"] = out.groupby("participant", group_keys=False)["log_rt"].apply(_z)
    return out


def sem(x: pd.Series) -> float:
    v = pd.to_numeric(x, errors="coerce").to_numpy(dtype=float)
    v = v[np.isfinite(v)]
    if len(v) <= 1:
        return float("nan")
    return float(np.std(v, ddof=1) / np.sqrt(len(v)))


def add_agency(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["agency"] = (d["group"].astype(str) == "Free").astype(int)
    return d


def make_sample_conf_avg_by_correct(df: pd.DataFrame) -> pd.DataFrame:
    d = add_agency(df)
    g = (
        d.groupby(["group", "agency", "participant", "incentive", "correct"], observed=True)["conf"]
        .mean()
        .reset_index()
    )
    out = (
        g.groupby(["group", "agency", "incentive", "correct"], observed=True)
        .agg(conf_mean=("conf", "mean"), conf_sem=("conf", sem))
        .reset_index()
    )
    return out[["agency", "incentive", "correct", "conf_mean", "conf_sem", "group"]]


def make_sample_xpatt(df: pd.DataFrame) -> pd.DataFrame:
    d = add_agency(df)
    g = (
        d.groupby(["group", "agency", "participant", "difficulty", "incentive", "correct"], observed=True)["conf"]
        .mean()
        .reset_index()
    )
    out = (
        g.groupby(["group", "agency", "difficulty", "incentive", "correct"], observed=True)
        .agg(conf_mean=("conf", "mean"), conf_sem=("conf", sem))
        .reset_index()
    )
    return out[["agency", "difficulty", "incentive", "correct", "conf_mean", "conf_sem", "group"]]


def make_sub_pred_xpatt(df: pd.DataFrame) -> pd.DataFrame:
    d = add_agency(df)
    inc_levels = np.sort(d["incentive"].unique())
    grid_rows = []
    for inc in inc_levels:
        for diff in LEVELS_DIFFICULTY:
            for cf in ("Error", "Correct"):
                grid_rows.append({"incentive": float(inc), "difficulty": float(diff), "correctF": cf})
    grid = pd.DataFrame(grid_rows)

    parts: List[pd.DataFrame] = []
    for (pid, grp, ag), dsub in d.groupby(["participant", "group", "agency"], observed=True):
        res = _fit_xpatt_outcome(dsub, "conf")
        if res is None:
            continue
        g2 = grid.copy()
        g2["conf"] = _predict_xpatt(res, g2)
        g2["correct"] = np.where(g2["correctF"] == "Correct", 0.5, -0.5)
        g2["participant"] = pid
        g2["group"] = grp
        g2["agency"] = ag
        parts.append(g2)
    if not parts:
        return pd.DataFrame(
            columns=["group", "agency", "participant", "difficulty", "incentive", "correctF", "correct", "conf"]
        )
    out = pd.concat(parts, ignore_index=True)
    return out[["group", "agency", "participant", "difficulty", "incentive", "correctF", "correct", "conf"]]


def extract_effects_all(
    df: pd.DataFrame,
    fitter: Callable[[pd.DataFrame], Optional[sm.regression.linear_model.RegressionResultsWrapper]],
    has_logrt: bool,
) -> pd.DataFrame:
    rows = []
    for (pid, grp), dsub in df.groupby(["participant", "group"], observed=True):
        res = fitter(dsub)
        if res is None:
            continue
        eff = extract_effects_xpatt(res, has_logrt=has_logrt)
        row = {"participant": pid, "group": grp, **eff}
        rows.append(row)
    if not rows:
        return pd.DataFrame(columns=["participant", "group"] + EFFECT_CODES)
    out = pd.DataFrame(rows)
    out["group"] = pd.Categorical(out["group"], categories=GROUP_LEVELS, ordered=True)
    out["participant"] = out["participant"].astype(str)
    out["group"] = out["group"].astype(str)
    for c in EFFECT_CODES:
        if c not in out.columns:
            out[c] = np.nan
    return out[["participant", "group"] + EFFECT_CODES]


def _one_sample_ci(x: np.ndarray, tt: object) -> Tuple[float, float]:
    x = x[np.isfinite(x)]
    ci_m = getattr(tt, "confidence_interval", None)
    if callable(ci_m):
        ci = ci_m()
        return float(ci.low), float(ci.high)
    dfv = float(getattr(tt, "df", np.nan))
    est = float(np.mean(x))
    se = float(np.std(x, ddof=1) / np.sqrt(len(x)))
    if not np.isfinite(dfv) or len(x) < 2:
        return float("nan"), float("nan")
    t_crit = float(stats.t.ppf(0.975, dfv))
    return est - t_crit * se, est + t_crit * se


def _fix_one_sample_estimate(x: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    return float(np.mean(x))


def tidy_one_sample_r(
    x: np.ndarray, label_effect: str, label_group: str
) -> Optional[dict]:
    x = x[np.isfinite(x)]
    if len(x) <= 1:
        return None
    tt = stats.ttest_1samp(x, popmean=0.0)
    se = float(np.std(x, ddof=1) / np.sqrt(len(x)))
    lcl, ucl = _one_sample_ci(x, tt)
    return {
        "Effect": label_effect,
        "Group": label_group,
        "estimate": _fix_one_sample_estimate(x),
        "se": se,
        "t": float(tt.statistic),
        "df": float(tt.df),
        "p": float(tt.pvalue),
        "lcl": lcl,
        "ucl": ucl,
    }


def tidy_pairwise_welch(effects_all: pd.DataFrame, eff: str, label_effect: str) -> pd.DataFrame:
    d = effects_all[["group", eff]].copy()
    d = d[np.isfinite(pd.to_numeric(d[eff], errors="coerce"))]
    d["group"] = pd.Categorical(d["group"], categories=[g for g in GROUP_LEVELS if g in set(d["group"])], ordered=True)
    grps = [g for g in GROUP_LEVELS if g in set(d["group"])]
    if len(grps) < 2:
        return pd.DataFrame(columns=["Effect", "Contrast", "estimate", "se", "t", "df", "p", "lcl", "ucl"])
    rows = []
    for g1, g2 in itertools.combinations(grps, 2):
        x1 = d.loc[d["group"] == g1, eff].to_numpy(dtype=float)
        x2 = d.loc[d["group"] == g2, eff].to_numpy(dtype=float)
        x1 = x1[np.isfinite(x1)]
        x2 = x2[np.isfinite(x2)]
        if len(x1) < 2 or len(x2) < 2:
            continue
        tt = stats.ttest_ind(x1, x2, equal_var=False)
        ci_m = getattr(tt, "confidence_interval", None)
        if callable(ci_m):
            ci = ci_m()
            lcl, ucl = float(ci.low), float(ci.high)
        else:
            lcl, ucl = float("nan"), float("nan")
        rows.append(
            {
                "Effect": label_effect,
                "Contrast": f"{g1} {UMINUS} {g2}",
                "estimate": float(np.mean(x1) - np.mean(x2)),
                "se": float(np.sqrt(np.var(x1, ddof=1) / len(x1) + np.var(x2, ddof=1) / len(x2))),
                "t": float(tt.statistic),
                "df": float(tt.df),
                "p": float(tt.pvalue),
                "lcl": lcl,
                "ucl": ucl,
            }
        )
    return pd.DataFrame(rows)


def make_tidy_group_tables(
    effects_all: pd.DataFrame, effect_codes: List[str], effect_labels: Dict[str, str]
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    within_rows = []
    for code in effect_codes:
        lab = effect_labels[code]
        for grp, gdf in effects_all.groupby("group", observed=True):
            vals = gdf[code].to_numpy(dtype=float)
            row = tidy_one_sample_r(vals, lab, str(grp))
            if row:
                within_rows.append(row)
    within = pd.DataFrame(within_rows)
    if within.empty:
        within = pd.DataFrame(columns=["Effect", "Group", "estimate", "se", "t", "df", "p", "lcl", "ucl"])
    else:
        within = within[["Effect", "Group", "estimate", "se", "t", "df", "p", "lcl", "ucl"]]

    between_rows = []
    for code in effect_codes:
        between_rows.append(tidy_pairwise_welch(effects_all, code, effect_labels[code]))
    between = pd.concat(between_rows, ignore_index=True) if between_rows else pd.DataFrame()
    if between.empty:
        between = pd.DataFrame(columns=["Effect", "Contrast", "estimate", "se", "t", "df", "p", "lcl", "ucl"])
    else:
        between = between[["Effect", "Contrast", "estimate", "se", "t", "df", "p", "lcl", "ucl"]]
    return within, between


def fmt_num(x: float, d: int = 2) -> str:
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "NA"
    return format(float(x), f".{d}f")


def stars(p: float) -> str:
    if not np.isfinite(p):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return ""


def fmt_p_eq(p: float) -> str:
    if not np.isfinite(p):
        return "NA"
    if p < 0.001:
        return "< .001"
    return f"{p:.3f}"


def _md_escape_pipe(s: object) -> str:
    """Avoid breaking GitHub/CommonMark tables: | is a column delimiter."""
    if s is None or (isinstance(s, float) and not np.isfinite(s)):
        return ""
    return str(s).replace("|", "&#124;")


def combine5(
    estimate: float, se: float, t: float, df: float, p: float, lcl: float, ucl: float, digits: int = 2
) -> str:
    df_str = fmt_num(df, 0) if np.isfinite(df) and abs(df - round(df)) < 1e-9 else fmt_num(df, 2)
    return (
        f"{fmt_num(estimate, digits)} "
        f"\u00B1 {fmt_num(se, digits)}<br/>"
        f"t<sub>{df_str}</sub> = {fmt_num(t, digits)}<br/>"
        f"p = {fmt_p_eq(p)}{stars(p)}<br/>"
        f"[{fmt_num(lcl, digits)}, {fmt_num(ucl, digits)}]"
    )


def render_md_summary(
    stem: str, within_tidy: pd.DataFrame, between_tidy: pd.DataFrame, digits: int = 2
) -> str:
    if within_tidy.empty:
        tbl_within = "_(no results)_"
    else:
        w = within_tidy.copy()
        w["Group"] = w["Group"].astype(str)
        w["Effect"] = w["Effect"].map(_md_escape_pipe)
        w["Stats"] = [
            combine5(r.estimate, r.se, r.t, r.df, r.p, r.lcl, r.ucl, digits) for r in w.itertuples(index=False)
        ]
        wide = w.pivot(index="Effect", columns="Group", values="Stats").reset_index()
        wide = wide.sort_values("Effect")
        tbl_within = wide.to_markdown(index=False)

    if between_tidy.empty:
        tbl_between = "_(no results)_"
    else:
        b = between_tidy.copy()
        b["Contrast"] = b["Contrast"].astype(str).map(_md_escape_pipe)
        b["Effect"] = b["Effect"].map(_md_escape_pipe)
        b["Stats"] = [
            combine5(r.estimate, r.se, r.t, r.df, r.p, r.lcl, r.ucl, digits) for r in b.itertuples(index=False)
        ]
        wide_b = b.pivot(index="Effect", columns="Contrast", values="Stats").reset_index()
        wide_b = wide_b.sort_values("Effect")
        tbl_between = wide_b.to_markdown(index=False)

    return (
        f"# Summary: {stem}\n\n"
        f"## Within-group effects\n\n{tbl_within}\n\n"
        f"## Between-groups (pairwise Welch)\n\n{tbl_between}\n"
    )


def run_one_stem(stem: str, df: pd.DataFrame, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    df = recode_vars(df, experiment_name=stem)

    sample_conf_avg = make_sample_conf_avg_by_correct(df)
    sample_xpatt = make_sample_xpatt(df)
    sub_pred_xpatt = make_sub_pred_xpatt(df)

    sample_conf_avg.to_csv(outdir / f"sample_conf_avg_by_correct_{stem}.csv", index=False, na_rep="")
    sample_xpatt.to_csv(outdir / f"sample_xpatt_{stem}.csv", index=False, na_rep="")
    sub_pred_xpatt.to_csv(outdir / f"sub_pred_xpatt_{stem}.csv", index=False, na_rep="")

    eff_conf = extract_effects_all(df, lambda ds: _fit_xpatt_outcome(ds, "conf"), has_logrt=False)
    within_c, between_c = make_tidy_group_tables(eff_conf, EFFECT_CODES, EFFECT_LABELS)
    eff_conf.to_csv(outdir / "effects_conf_xpatt.csv", index=False, na_rep="")
    within_c.to_csv(outdir / "within_group_conf_xpatt.csv", index=False, na_rep="")
    between_c.to_csv(outdir / "between_groups_conf_xpatt_pairwise_welch.csv", index=False, na_rep="")
    md_conf = render_md_summary(f"{stem} | CONF (xpatt emtrends)", within_c, between_c, digits=2)
    (outdir / "summary_conf_xpatt.md").write_text(md_conf, encoding="utf-8")

    if "log_rt" in df.columns:
        eff_logrt = extract_effects_all(df, lambda ds: _fit_xpatt_outcome(ds, "log_rt"), has_logrt=False)
        within_l, between_l = make_tidy_group_tables(eff_logrt, EFFECT_CODES, EFFECT_LABELS)
        eff_logrt.to_csv(outdir / "effects_logrt_xpatt.csv", index=False, na_rep="")
        within_l.to_csv(outdir / "within_group_logrt_xpatt.csv", index=False, na_rep="")
        between_l.to_csv(outdir / "between_groups_logrt_xpatt_pairwise_welch.csv", index=False, na_rep="")
        md_logrt = render_md_summary(f"{stem} | logRT (xpatt emtrends)", within_l, between_l, digits=2)
        (outdir / "summary_logrt_xpatt.md").write_text(md_logrt, encoding="utf-8")

        eff_cc = extract_effects_all(df, _fit_xpatt_conf_ctrlrt, has_logrt=True)
        within_cc, between_cc = make_tidy_group_tables(eff_cc, EFFECT_CODES, EFFECT_LABELS)
        eff_cc.to_csv(outdir / "coef_effects_conf.csv", index=False, na_rep="")
        within_cc.to_csv(outdir / "within_group_conf_ctrlrt_xpatt.csv", index=False, na_rep="")
        between_cc.to_csv(outdir / "between_groups_conf_ctrlrt_xpatt_pairwise_welch.csv", index=False, na_rep="")
        md_cc = render_md_summary(f"{stem} | CONF controlling logRT (xpatt emtrends)", within_cc, between_cc, digits=2)
        (outdir / "summary_conf_ctrlrt_xpatt.md").write_text(md_cc, encoding="utf-8")


def _bootstrap_path() -> None:
    import sys

    repo_src = Path(__file__).resolve().parents[2] / "src"
    s = str(repo_src)
    if s not in sys.path:
        sys.path.insert(0, s)


def main() -> None:
    if __package__ in (None, ""):
        _bootstrap_path()
    from motivbelief.stats_avg import build_analysis_specs

    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--out-root", type=Path, default=Path("results/stats/trial"))
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    specs = build_analysis_specs(repo)
    args.out_root.mkdir(parents=True, exist_ok=True)
    for stem, spec in specs.items():
        df = spec["build"]()
        run_one_stem(stem, df, args.out_root / stem)


if __name__ == "__main__":
    main()
