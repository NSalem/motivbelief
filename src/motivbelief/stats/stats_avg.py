"""
Participant-level incentive regressions, group tests, CSV/Markdown writers.

Reads trial CSVs from ``data/data_<exp>.csv`` (see ``build_analysis_specs`` for stems
such as ``exp1a``, merged simulation stems). Writes per-dataset outputs under
``<out-root>/<stem>/``: e.g. ``sample_avg_*.csv``, ``within_summary__*.csv``,
``between_summary__*.csv``, ``ttests_incentives__*.csv``. Default ``--out-root`` is
``results/stats/average`` (set via CLI).
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats


GROUP_ORDER = ["Free", "Replayed", "Forced", "Observed", "Non-Free"]


def read_data(path: Path, tag: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.copy()
    df["participant"] = tag + "_" + df["participant"].astype(str)
    return df


def build_analysis_specs(repo_root: Path) -> Dict[str, Dict[str, Callable[[], pd.DataFrame]]]:
    data = repo_root / "data"

    def bind(*frames: pd.DataFrame) -> pd.DataFrame:
        return pd.concat(frames, ignore_index=True)

    return {
        "exp1a": {"build": lambda: read_data(data / "data_exp1a.csv", "Exp1a")},
        "exp1b": {"build": lambda: read_data(data / "data_exp1b.csv", "Exp1b")},
        "exp2": {"build": lambda: read_data(data / "data_exp2.csv", "Exp2")},
        "exp3": {"build": lambda: read_data(data / "data_exp3.csv", "Exp3")},
        "exp1a_exp3": {
            "build": lambda: bind(
                read_data(data / "data_exp1a.csv", "Exp1a"),
                read_data(data / "data_exp3.csv", "Exp3"),
            )
        },
        "exp1a_exp2free_exp3": {
            "build": lambda: (
                lambda d: d.assign(
                    choiceType=np.where(d["choiceType"].astype(str) == "Free", "Free", "Non-Free")
                )
            )(
                bind(
                    read_data(data / "data_exp1a.csv", "Exp1a"),
                    read_data(data / "data_exp2.csv", "Exp2")
                    .loc[lambda x: x["choiceType"].astype(str) == "Free"]
                    .copy(),
                    read_data(data / "data_exp3.csv", "Exp3"),
                )
            )
        },
        "sim_act": {
            "build": lambda: read_data(repo_root / "results/sims/sims_act.csv", "Sims Act").assign(
                choiceType=lambda d: np.where(d["choiceType"].astype(str) == "Free", "Free", "Non-Free")
            )
        },
        "sim_intent": {
            "build": lambda: read_data(repo_root / "results/sims/sims_intent.csv", "Sims Int").assign(
                choiceType=lambda d: np.where(d["choiceType"].astype(str) == "Free", "Free", "Non-Free")
            )
        },
        "sim_confirm": {
            "build": lambda: read_data(repo_root / "results/sims/sims_confirm.csv", "Sims Con").assign(
                choiceType=lambda d: np.where(d["choiceType"].astype(str) == "Free", "Free", "Non-Free")
            )
        },
    }


def compute_participant_coefs(
    df: pd.DataFrame,
    y_col: str,
    inc_col: str = "incentive",
    participant_col: str = "participant",
    group_col: str = "choiceType",
) -> Tuple[pd.DataFrame, bool, np.ndarray]:
    sub = df[[participant_col, group_col, inc_col, y_col]].copy()
    sub = sub.groupby([participant_col, group_col, inc_col], as_index=False)[y_col].mean()
    wide = sub.pivot_table(
        index=[participant_col, group_col],
        columns=inc_col,
        values=y_col,
        aggfunc="first",
    )
    wide = wide.reset_index()

    def _col_to_float(c: object) -> Optional[float]:
        if c in (participant_col, group_col):
            return None
        try:
            return float(c)
        except (TypeError, ValueError):
            return None

    inc_levels = []
    for c in wide.columns:
        v = _col_to_float(c)
        if v is not None and np.isfinite(v):
            inc_levels.append(v)
    x = np.sort(np.unique(np.array(inc_levels, dtype=float)))
    if x.size == 0:
        return pd.DataFrame(), False, x

    def _pivot_col_for_level(v: float) -> object:
        for c in wide.columns:
            if c in (participant_col, group_col):
                continue
            cv = _col_to_float(c)
            if cv is not None and abs(cv - v) < 1e-9:
                return c
        return None

    col_names = []
    for v in x:
        pc = _pivot_col_for_level(float(v))
        if pc is None:
            return pd.DataFrame(), False, x
        col_names.append(pc)
    for cn in col_names:
        if cn not in wide.columns:
            wide[cn] = np.nan
    wide_cc = wide[[participant_col, group_col] + col_names].dropna(subset=col_names, how="any")
    if wide_cc.empty:
        return pd.DataFrame(), False, x

    compute_abs = bool((x < 0).any() and (x > 0).any())
    if compute_abs:
        X = np.column_stack([np.ones(len(x)), x, np.abs(x)])
        x_cols = ["b0", "b_inc", "b_abs"]
    else:
        X = np.column_stack([np.ones(len(x)), x])
        x_cols = ["b0", "b_inc"]
    Xpinv = np.linalg.pinv(X)
    Y = wide_cc[col_names].to_numpy(dtype=float)
    B = Y @ Xpinv.T
    coef_df = pd.DataFrame(B, columns=x_cols)
    coef_df.insert(0, group_col, wide_cc[group_col].values)
    coef_df.insert(0, participant_col, wide_cc[participant_col].values)
    return coef_df, compute_abs, x


def summarize_within_group(coef_df: pd.DataFrame, respvar: str, group_col: str = "choiceType") -> pd.DataFrame:
    if coef_df.empty:
        return pd.DataFrame(columns=["choiceType", "coef", "mean", "se", "t", "df", "p"])
    coef_cols = [c for c in coef_df.columns if c not in ("participant", group_col)]
    intercept_mu = 50.0 if respvar in ("correct", "conf", "confSym") else 0.0
    rows = []
    for grp, gdf in coef_df.groupby(group_col, sort=False):
        for coef in coef_cols:
            vals = gdf[coef].to_numpy(dtype=float)
            vals = vals[np.isfinite(vals)]
            if vals.size == 0:
                continue
            mu0 = intercept_mu if coef == "b0" else 0.0
            tt = stats.ttest_1samp(vals, popmean=mu0)
            rows.append(
                {
                    "choiceType": grp,
                    "coef": coef,
                    "mean": float(np.mean(vals)),
                    "se": float(np.std(vals, ddof=1) / np.sqrt(len(vals))) if len(vals) > 1 else float("nan"),
                    "t": float(tt.statistic),
                    "df": float(tt.df),
                    "p": float(tt.pvalue),
                }
            )
    return pd.DataFrame(rows)


def summarize_between_groups(
    coef_df: pd.DataFrame, group_col: str = "choiceType", participant_col: str = "participant"
) -> pd.DataFrame:
    """Between-group contrast (e.g. Non-Free vs Free) for each participant-level coefficient.

    Uses a paired t-test whenever the two groups are the exact same set of
    participants (one row each, no duplicates) -- true for our model
    simulations, where every subject's Free and Non-Free coefficients come
    from one fitted model, so the comparison is inherently within-subject.
    Falls back to a Welch two-sample t-test otherwise (the real-data case,
    where Free and Non-Free draw on disjoint subject pools). The point
    estimate (mean difference) is identical either way; only se/t/df/p
    differ, since pairing removes between-subject variance that has
    nothing to do with how consistently a given model's own prediction
    shifts between conditions.

    The paired-vs-Welch decision is made from each group's FULL participant
    roster -- not from the subset that happens to have a non-NaN value for
    this particular coefficient -- since cohort identity doesn't depend on
    which coefficient we're testing. Otherwise a handful of participants
    with a NaN coefficient in only one of the two conditions would silently
    break the exact-set-equality check and downgrade a same-cohort
    comparison to Welch. When paired, those participants are instead
    dropped available-case (paired on the intersection of non-NaN ids).
    """
    if coef_df.empty:
        return pd.DataFrame(columns=["pair", "coef", "mean", "se", "t", "df", "p", "test"])
    coef_cols = [c for c in coef_df.columns if c not in ("participant", group_col)]
    present = coef_df[group_col].unique().tolist()
    group_levels = [g for g in GROUP_ORDER if g in present]
    if len(group_levels) < 2:
        group_levels = sorted(present)
    rows = []
    for i, g1 in enumerate(group_levels):
        for g2 in group_levels[i + 1 :]:
            d1 = coef_df.loc[coef_df[group_col] == g1]
            d2 = coef_df.loc[coef_df[group_col] == g2]
            p1_full, p2_full = d1[participant_col], d2[participant_col]
            cohort_paired = (
                len(p1_full) > 1
                and set(p1_full) == set(p2_full)
                and not p1_full.duplicated().any()
                and not p2_full.duplicated().any()
            )
            for cn in coef_cols:
                sub1 = d1[[participant_col, cn]].copy()
                sub2 = d2[[participant_col, cn]].copy()
                sub1[cn] = pd.to_numeric(sub1[cn], errors="coerce")
                sub2[cn] = pd.to_numeric(sub2[cn], errors="coerce")
                sub1 = sub1[np.isfinite(sub1[cn])]
                sub2 = sub2[np.isfinite(sub2[cn])]
                if sub1.empty or sub2.empty:
                    continue
                if cohort_paired:
                    merged = sub1.merge(sub2, on=participant_col, suffixes=("_1", "_2"))
                    diff = (merged[f"{cn}_2"] - merged[f"{cn}_1"]).to_numpy(dtype=float)
                    diff = diff[np.isfinite(diff)]
                    if diff.size < 2:
                        continue
                    tt = stats.ttest_1samp(diff, popmean=0.0)
                    mean_ = float(np.mean(diff))
                    se_ = float(np.std(diff, ddof=1) / np.sqrt(diff.size))
                    test_name = "paired"
                else:
                    x1 = sub1[cn].to_numpy(dtype=float)
                    x2 = sub2[cn].to_numpy(dtype=float)
                    if x1.size < 2 or x2.size < 2:
                        continue
                    tt = stats.ttest_ind(x2, x1, equal_var=False)
                    mean_ = float(np.mean(x2) - np.mean(x1))
                    se_ = float(np.sqrt(np.var(x1, ddof=1) / x1.size + np.var(x2, ddof=1) / x2.size))
                    test_name = "welch"
                rows.append(
                    {
                        "pair": f"{g2} - {g1}",
                        "coef": cn,
                        "mean": mean_,
                        "se": se_,
                        "t": float(tt.statistic),
                        "df": float(tt.df),
                        "p": float(tt.pvalue),
                        "test": test_name,
                    }
                )
    return pd.DataFrame(rows)


def _format_comparison(a: float, b: float) -> str:
    if a == int(a) and b == int(b):
        return f"{int(a)} - {int(b)}"
    return f"{a} - {b}"


def get_ttests_table(
    df_m: pd.DataFrame,
    respvar: str,
    group_col: str = "choiceType",
    participant_col: str = "participant",
    inc_col: str = "incentive",
) -> pd.DataFrame:
    inc_levels = np.sort(df_m[inc_col].unique())
    has0 = np.any(inc_levels == 0)
    has_pos = np.any(inc_levels > 0)
    has_neg = np.any(inc_levels < 0)
    pairs: List[Tuple[float, float]] = []
    if has0 and has_pos and has_neg and (-1 in inc_levels) and (1 in inc_levels):
        pairs = [(1.0, 0.0), (-1.0, 0.0), (1.0, -1.0)]
    elif has0 and has_pos and not has_neg:
        pos_levels = np.sort(inc_levels[inc_levels > 0])[::-1]
        pairs = [(float(a), 0.0) for a in pos_levels]
        for i, a in enumerate(pos_levels):
            for b in pos_levels[i + 1 :]:
                pairs.append((float(a), float(b)))
    else:
        lev_desc = np.sort(inc_levels)[::-1]
        for i, a in enumerate(lev_desc):
            for b in lev_desc[i + 1 :]:
                pairs.append((float(a), float(b)))

    present = df_m[group_col].unique().tolist()
    group_levels = [g for g in GROUP_ORDER if g in present]
    if len(group_levels) == 0:
        group_levels = sorted(present)
    rows = []
    for grp in group_levels:
        sub = df_m.loc[df_m[group_col] == grp]
        for a, b in pairs:
            sa = sub.loc[sub[inc_col] == a, [participant_col, respvar]]
            sb = sub.loc[sub[inc_col] == b, [participant_col, respvar]]
            merged = sa.merge(sb, on=participant_col, suffixes=("_a", "_b"))
            merged = merged.dropna(subset=[f"{respvar}_a", f"{respvar}_b"])
            if len(merged) < 2:
                continue
            xa = merged[f"{respvar}_a"].to_numpy(dtype=float)
            xb = merged[f"{respvar}_b"].to_numpy(dtype=float)
            tt = stats.ttest_rel(xa, xb)
            rows.append(
                {
                    "group": grp,
                    "comparison": _format_comparison(a, b),
                    "t": float(tt.statistic),
                    "df": float(tt.df),
                    "p": float(tt.pvalue),
                }
            )
    return pd.DataFrame(rows)


def _pivot_inc_col(wide: pd.DataFrame, target: float) -> Optional[object]:
    for c in wide.columns:
        try:
            if abs(float(c) - float(target)) < 1e-9:
                return c
        except (TypeError, ValueError):
            continue
    return None


def get_gain_loss_corr_table(
    df_m: pd.DataFrame,
    respvar: str,
    group_col: str = "choiceType",
    participant_col: str = "participant",
    inc_col: str = "incentive",
) -> pd.DataFrame:
    rows = []
    for grp in sorted(df_m[group_col].unique()):
        sub = df_m.loc[df_m[group_col] == grp]
        wide = sub.pivot_table(index=participant_col, columns=inc_col, values=respvar, aggfunc="first")
        c_neg = _pivot_inc_col(wide, -1.0)
        c0 = _pivot_inc_col(wide, 0.0)
        c_pos = _pivot_inc_col(wide, 1.0)
        if c_neg is None or c0 is None or c_pos is None:
            rows.append({"group": grp, "r": np.nan, "p": np.nan, "n": 0})
            continue
        w2 = wide[[c_neg, c0, c_pos]].dropna(how="any")
        if len(w2) < 3:
            rows.append({"group": grp, "r": np.nan, "p": np.nan, "n": int(len(w2))})
            continue
        gain = w2[c_pos].to_numpy(dtype=float) - w2[c0].to_numpy(dtype=float)
        loss = w2[c_neg].to_numpy(dtype=float) - w2[c0].to_numpy(dtype=float)
        r, p = stats.pearsonr(gain, loss)
        rows.append({"group": grp, "r": float(r), "p": float(p), "n": int(len(w2))})
    return pd.DataFrame(rows)


def kable_md(df: pd.DataFrame, digits: int = 3) -> str:
    if df is None or df.empty:
        return "_None_\n"
    return df.round(digits).to_markdown(index=False) + "\n"


def render_md_avg_summary(
    stem: str,
    respvar: str,
    meta: Dict[str, Any],
    within_tbl: pd.DataFrame,
    between_tbl: pd.DataFrame,
    ttests_tbl: pd.DataFrame,
    corr_tbl: pd.DataFrame,
) -> str:
    model_line = "- `y ~ 1 + incentive + |incentive|`" if meta.get("compute_abs") else "- `y ~ 1 + incentive`"
    inc_levels = meta.get("inc_levels", np.array([]))
    inc_str = ", ".join(str(v) for v in np.asarray(inc_levels).ravel())
    parts = [
        f"# {stem}",
        "",
        f"## Response variable: `{respvar}`",
        "",
        "### Model used for participant coefficients",
        "",
        model_line,
        f"- Incentive levels: {inc_str}",
        "",
        "### Within-group tests (participant coefficients vs 0)",
        "",
        kable_md(within_tbl, digits=4),
        "",
        "### Between-group tests (pairwise Welch)",
        "",
        kable_md(between_tbl, digits=4),
        "",
        "### Paired t-tests between incentive conditions (within group)",
        "",
        kable_md(ttests_tbl, digits=4),
        "",
        "### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))",
        "",
        kable_md(corr_tbl, digits=4),
        "",
    ]
    return "\n".join(parts)


def run_one_dataset(
    stem: str,
    df: pd.DataFrame,
    out_root: Path,
    respvars: Optional[List[str]] = None,
) -> None:
    if respvars is None:
        respvars = ["correct", "conf", "confSym", "calib", "rt_log"]

    outdir = out_root / stem
    outdir.mkdir(parents=True, exist_ok=True)

    df = df.copy()
    if "rt" in df.columns:
        df["rt_log"] = np.log(np.maximum(pd.to_numeric(df["rt"], errors="coerce").fillna(np.nan), 1e-6))
    else:
        df["rt_log"] = np.nan

    df_m = (
        df.groupby(["participant", "incentive", "choiceType"], as_index=False)
        .agg(correct=("correct", "mean"), conf=("conf", "mean"), rt_log=("rt_log", "mean"))
    )
    df_m["correct"] = df_m["correct"] * 100.0
    df_m["calib"] = df_m["conf"] - df_m["correct"]
    df_m["confSym"] = 50.0 + np.abs(df_m["conf"] - 50.0)

    if df_m["rt_log"].isna().all():
        respvars = [r for r in respvars if r != "rt_log"]

    sub_avg = pd.DataFrame(
        {
            "agency": (df_m["choiceType"].astype(str) == "Free").astype(int),
            "participant": df_m["participant"],
            "incentive": df_m["incentive"],
            "correct": df_m["correct"],
            "conf": df_m["conf"],
            "confSym": df_m["confSym"],
            "calib": df_m["calib"],
            "log_rt": df_m["rt_log"],
            "group": df_m["choiceType"],
        }
    )
    sub_avg.to_csv(outdir / f"sub_avg_{stem}.csv", index=False, na_rep="")

    def sem(x: pd.Series) -> float:
        x = x[np.isfinite(x.to_numpy(dtype=float))]
        if len(x) <= 1:
            return float("nan")
        return float(x.std(ddof=1) / np.sqrt(len(x)))

    sample_avg = (
        sub_avg.groupby(["group", "agency", "incentive"], as_index=False)
        .agg(
            correct_mean=("correct", "mean"),
            correct_sem=("correct", sem),
            conf_mean=("conf", "mean"),
            conf_sem=("conf", sem),
            confSym_mean=("confSym", "mean"),
            confSym_sem=("confSym", sem),
            calib_mean=("calib", "mean"),
            calib_sem=("calib", sem),
            log_rt_mean=("log_rt", "mean"),
            log_rt_sem=("log_rt", sem),
        )
    )
    sample_avg.to_csv(outdir / f"sample_avg_{stem}.csv", index=False, na_rep="")

    for respvar in respvars:
        coef_df, compute_abs, inc_levels = compute_participant_coefs(df_m, y_col=respvar)
        coef_df.to_csv(outdir / f"sub_effects__{stem}__{respvar}.csv", index=False, na_rep="")

        within_tbl = summarize_within_group(coef_df, respvar=respvar, group_col="choiceType")
        within_tbl.to_csv(outdir / f"within_summary__{stem}__{respvar}.csv", index=False, na_rep="")

        between_tbl = summarize_between_groups(coef_df, group_col="choiceType")
        between_tbl.to_csv(outdir / f"between_summary__{stem}__{respvar}.csv", index=False, na_rep="")

        ttests_tbl = get_ttests_table(df_m, respvar=respvar)
        ttests_tbl.to_csv(outdir / f"ttests_incentives__{stem}__{respvar}.csv", index=False, na_rep="")

        inc_vals = pd.to_numeric(df_m["incentive"], errors="coerce").dropna().unique().tolist()

        def _has_inc(t: float) -> bool:
            return any(abs(float(v) - t) < 1e-9 for v in inc_vals)

        if _has_inc(-1.0) and _has_inc(0.0) and _has_inc(1.0):
            corr_tbl = get_gain_loss_corr_table(df_m, respvar=respvar)
            corr_tbl.to_csv(outdir / f"gain_loss_corr__{stem}__{respvar}.csv", index=False, na_rep="")
        else:
            corr_tbl = pd.DataFrame()

        md = render_md_avg_summary(
            stem=f"{stem} | AVG stats",
            respvar=respvar,
            meta={"compute_abs": compute_abs, "inc_levels": inc_levels},
            within_tbl=within_tbl,
            between_tbl=between_tbl,
            ttests_tbl=ttests_tbl,
            corr_tbl=corr_tbl,
        )
        (outdir / f"summary__{stem}__{respvar}.md").write_text(md, encoding="utf-8")


def _bootstrap_path() -> None:
    import sys

    repo_src = Path(__file__).resolve().parents[2] / "src"
    s = str(repo_src)
    if s not in sys.path:
        sys.path.insert(0, s)


def main() -> None:
    if __package__ in (None, ""):
        _bootstrap_path()
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--out-root", type=Path, default=Path("results/stats/average"))
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    specs = build_analysis_specs(repo)
    args.out_root.mkdir(parents=True, exist_ok=True)
    for stem, spec in specs.items():
        df = spec["build"]()
        run_one_dataset(stem, df, args.out_root)


if __name__ == "__main__":
    main()
