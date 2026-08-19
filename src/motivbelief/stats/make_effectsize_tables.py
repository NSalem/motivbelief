"""
Cohen's d tables from average + trial stats CSVs.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd

EXP_ORDER = ["exp1a_exp3", "exp1b", "exp2"]
GROUP_ORDER = ["Observed", "Forced", "Replayed", "Free"]
TARGET_EFFECTS = ["Incentive|Correct", "Incentive|Error"]
TRIAL_STEM = "exp1a_exp2free_exp3"


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        return pd.DataFrame()
    return pd.read_csv(path)


def cohen_d_one_sample(t: float, df: float) -> float:
    if not (np.isfinite(t) and np.isfinite(df)):
        return float("nan")
    n = df + 1.0
    if n <= 0:
        return float("nan")
    return float(t / np.sqrt(n))


def cohen_d_unpaired(x: np.ndarray, y: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    y = y[np.isfinite(y)]
    if len(x) < 2 or len(y) < 2:
        return float("nan")
    s1 = float(np.std(x, ddof=1))
    s2 = float(np.std(y, ddof=1))
    if not (np.isfinite(s1) and np.isfinite(s2)):
        return float("nan")
    denom = np.sqrt((s1**2 + s2**2) / 2.0)
    if not np.isfinite(denom) or denom == 0:
        return float("nan")
    return float((np.mean(x) - np.mean(y)) / denom)


def normalize_pair(pair: str) -> str:
    t = str(pair)
    for ch in ("\u2212", "\u2013", "\u2014"):
        t = t.replace(ch, "-")
    return re.sub(r"\s+", " ", t).strip()


def split_pair_groups(pairs: pd.Series) -> Tuple[pd.Series, pd.Series]:
    g1 = []
    g2 = []
    for x in pairs.astype(str):
        parts = re.split(r"\s+-\s+", x, maxsplit=1)
        g1.append(parts[0].strip())
        g2.append(parts[1].strip() if len(parts) > 1 else "")
    return pd.Series(g1), pd.Series(g2)


def format_d(x: float, digits: int = 3) -> str:
    if not np.isfinite(x):
        return ""
    return format(float(x), f".{digits}f")


def build_avg_effectsizes(avg_root: Path, coef_name: str) -> pd.DataFrame:
    within_rows = []
    between_rows = []
    all_between_pairs: List[str] = []

    for exp_id in EXP_ORDER:
        within_path = avg_root / exp_id / f"within_summary__{exp_id}__conf.csv"
        between_path = avg_root / exp_id / f"between_summary__{exp_id}__conf.csv"
        effects_path = avg_root / exp_id / f"sub_effects__{exp_id}__conf.csv"

        w = safe_read_csv(within_path)
        if not w.empty and "coef" in w.columns:
            w = w.loc[(w["coef"] == coef_name) & (w["choiceType"].isin(GROUP_ORDER))].copy()
            w["d"] = [cohen_d_one_sample(float(r.t), float(r.df)) for r in w.itertuples(index=False)]
            for r in w.itertuples(index=False):
                within_rows.append({"row": r.choiceType, "experiment": exp_id, "d": r.d})

        b = safe_read_csv(between_path)
        if not b.empty and "coef" in b.columns:
            b = b.loc[b["coef"] == coef_name].copy()
            b["pair"] = b["pair"].map(normalize_pair)
            all_between_pairs.extend(b["pair"].astype(str).tolist())

        eff = safe_read_csv(effects_path)
        bd_list = []
        has_eff = (
            not eff.empty
            and "choiceType" in eff.columns
            and coef_name in eff.columns
            and not b.empty
        )
        if has_eff:
            v = eff[coef_name].to_numpy(dtype=float)
            ct = eff["choiceType"].astype(str).to_numpy()
            for _, br in b.iterrows():
                g1s, g2s = split_pair_groups(pd.Series([br["pair"]]))
                g1, g2 = str(g1s.iloc[0]), str(g2s.iloc[0])
                x1 = v[ct == g1]
                x2 = v[ct == g2]
                bd_list.append({"row": br["pair"], "experiment": exp_id, "d": cohen_d_unpaired(x1, x2)})
        elif not b.empty:
            for _, br in b.iterrows():
                bd_list.append({"row": br["pair"], "experiment": exp_id, "d": np.nan})

        between_rows.extend(bd_list)

    within_long = pd.DataFrame(within_rows)
    between_long = pd.DataFrame(between_rows)
    long = pd.concat([within_long, between_long], ignore_index=True)
    if long.empty:
        return pd.DataFrame(columns=["label"] + EXP_ORDER)

    row_order = GROUP_ORDER + sorted(set(all_between_pairs))
    long["row"] = pd.Categorical(long["row"], categories=row_order, ordered=True)
    long["experiment"] = pd.Categorical(long["experiment"], categories=EXP_ORDER, ordered=True)
    long = long.sort_values(["row", "experiment"])
    out = long.pivot_table(index="row", columns="experiment", values="d", aggfunc="first").reset_index()
    out = out.rename(columns={"row": "label"})
    for col in EXP_ORDER:
        if col not in out.columns:
            out[col] = np.nan
    out = out[["label"] + EXP_ORDER]
    for col in EXP_ORDER:
        out[col] = out[col].map(format_d)
    return out


def build_trial_effectsizes(trial_root: Path) -> pd.DataFrame:
    stem_dir = trial_root / TRIAL_STEM
    within_path = stem_dir / "within_group_conf_xpatt.csv"
    between_path = stem_dir / "between_groups_conf_xpatt_ttests.csv"
    effects_path = stem_dir / "effects_conf_xpatt.csv"

    within = safe_read_csv(within_path)
    if not within.empty:
        within = within.loc[within["Effect"].isin(TARGET_EFFECTS)].copy()
        within["d"] = [cohen_d_one_sample(float(r.t), float(r.df)) for r in within.itertuples(index=False)]
        within = within.assign(row=within["Group"], effect=within["Effect"])[["row", "effect", "d"]]
    else:
        within = pd.DataFrame(columns=["row", "effect", "d"])

    between_raw = safe_read_csv(between_path)
    if not between_raw.empty:
        between_raw = between_raw.loc[between_raw["Effect"].isin(TARGET_EFFECTS)].copy()
        between_raw["row"] = between_raw["Contrast"].map(normalize_pair)
        between_raw = between_raw[["row", "Effect"]].rename(columns={"Effect": "effect"})
    else:
        between_raw = pd.DataFrame(columns=["row", "effect"])

    eff = safe_read_csv(effects_path)
    between_list = []
    if (
        not eff.empty
        and all(c in eff.columns for c in ("group", "incentive_corr", "incentive_err"))
        and not between_raw.empty
    ):
        for _, br in between_raw.iterrows():
            g1s, g2s = split_pair_groups(pd.Series([br["row"]]))
            g1, g2 = str(g1s.iloc[0]), str(g2s.iloc[0])
            eff_name = str(br["effect"])
            if eff_name == "Incentive|Correct":
                d = cohen_d_unpaired(
                    eff.loc[eff["group"] == g1, "incentive_corr"].to_numpy(dtype=float),
                    eff.loc[eff["group"] == g2, "incentive_corr"].to_numpy(dtype=float),
                )
            elif eff_name == "Incentive|Error":
                d = cohen_d_unpaired(
                    eff.loc[eff["group"] == g1, "incentive_err"].to_numpy(dtype=float),
                    eff.loc[eff["group"] == g2, "incentive_err"].to_numpy(dtype=float),
                )
            else:
                d = np.nan
            between_list.append({"row": br["row"], "effect": eff_name, "d": d})
    elif not between_raw.empty:
        for _, br in between_raw.iterrows():
            between_list.append({"row": br["row"], "effect": br["effect"], "d": np.nan})

    between = pd.DataFrame(between_list)
    long = pd.concat([within, between], ignore_index=True)
    row_order = ["Free", "Non-Free", "Free - Non-Free"]
    if long.empty:
        return pd.DataFrame(columns=["label"] + TARGET_EFFECTS)
    long = long.loc[long["row"].isin(row_order)]
    long["row"] = pd.Categorical(long["row"], categories=row_order, ordered=True)
    long["effect"] = pd.Categorical(long["effect"], categories=TARGET_EFFECTS, ordered=True)
    long = long.sort_values(["row", "effect"])
    out = long.pivot_table(index="row", columns="effect", values="d", aggfunc="first").reset_index()
    out = out.rename(columns={"row": "label"})
    for c in TARGET_EFFECTS:
        if c not in out.columns:
            out[c] = np.nan
    out = out[["label"] + TARGET_EFFECTS]
    for c in TARGET_EFFECTS:
        out[c] = out[c].map(format_d)
    return out


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
    ap.add_argument("--avg-root", type=Path, default=Path("results/stats/average"))
    ap.add_argument("--trial-root", type=Path, default=Path("results/stats/trial"))
    ap.add_argument("--out-root", type=Path, default=Path("results/stats/effectsizes"))
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    avg_root = (repo / args.avg_root).resolve() if not args.avg_root.is_absolute() else args.avg_root
    trial_root = (repo / args.trial_root).resolve() if not args.trial_root.is_absolute() else args.trial_root
    out_root = (repo / args.out_root).resolve() if not args.out_root.is_absolute() else args.out_root
    out_root.mkdir(parents=True, exist_ok=True)

    avg_linear = build_avg_effectsizes(avg_root, "b_inc")
    avg_abs = build_avg_effectsizes(avg_root, "b_abs")
    trial_tbl = build_trial_effectsizes(trial_root)

    linear_csv = out_root / "effectsizes_avg_linear_belief.csv"
    abs_csv = out_root / "effectsizes_avg_abs_belief.csv"
    avg_linear.to_csv(linear_csv, index=False, na_rep="")
    avg_abs.to_csv(abs_csv, index=False, na_rep="")

    md_lines = [
        "## Linear incentive (b_inc)",
        "",
        avg_linear.to_markdown(index=False),
        "",
        "## Absolute incentive (b_abs)",
        "",
        avg_abs.to_markdown(index=False),
    ]
    (out_root / "effectsizes_avg_linear_belief.md").write_text("\n".join(md_lines), encoding="utf-8")

    trial_csv = out_root / "effectsizes_trial_merged_belief_xpatt.csv"
    trial_tbl.to_csv(trial_csv, index=False, na_rep="")
    (out_root / "effectsizes_trial_merged_belief_xpatt.md").write_text(
        trial_tbl.to_markdown(index=False), encoding="utf-8"
    )
    print(f"Wrote effect-size tables to: {out_root}")


if __name__ == "__main__":
    main()
