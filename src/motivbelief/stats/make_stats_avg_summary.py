"""
 aggregate average-level summary CSVs into stats_tables.md.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

RESPVARS = ["correct", "conf", "confSym", "calib", "rt_log"]
RESPVAR_LABELS = {
    "correct": "Accuracy",
    "conf": "Belief",
    "confSym": "|Belief-50|",
    "calib": "Calibration",
    "rt_log": "log(RT)",
}
COEF_ORDER = {"b0": 0, "b_inc": 1, "b_abs": 2}


def _html_table_from_wide(wide: pd.DataFrame) -> str:
    """Render wide stats as HTML (same idea as make_stats_xpatt_summary: pipe md breaks on <br/> in cells)."""
    if wide.empty:
        return "<p><em>None</em></p>"
    cols = list(wide.columns)
    lines = ["<table>", "<thead>", "<tr>"]
    for c in cols:
        lines.append(f'<th scope="col">{html.escape(str(c))}</th>')
    lines.extend(["</tr>", "</thead>", "<tbody>"])
    for _, row in wide.iterrows():
        lines.append("<tr>")
        for c in cols:
            val = row[c]
            if pd.isna(val):
                lines.append("<td></td>")
            else:
                # Cells are pre-rendered HTML from format_cell / format_ttest_cell
                lines.append(f"<td>{val}</td>")
        lines.append("</tr>")
    lines.extend(["</tbody>", "</table>"])
    return "\n".join(lines)


def sig_symbol(p: float) -> str:
    if pd.isna(p) or not isinstance(p, (int, float)):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return ""


def format_p(p: float) -> str:
    if pd.isna(p) or not isinstance(p, (int, float)):
        return ""
    if p < 0.001:
        return ".000"
    return f"{float(p):.3f}"


def pick_raw_p(df: pd.DataFrame) -> str:
    return "p" if "p" in df.columns else ""


def format_cell(mean: float, se: float, t: float, dfv: float, p: float) -> str:
    if pd.isna(mean):
        return ""
    if pd.isna(dfv) or abs(dfv - round(dfv)) < 1e-9:
        df_str = f"<sub>{int(round(dfv))}</sub>"
    else:
        df_str = f"<sub>{dfv:.2f}</sub>"
    sig = sig_symbol(float(p)) if pd.notna(p) else ""
    p_str = format_p(float(p)) if pd.notna(p) else ""
    return f"{mean:.2f} ± {se:.2f}<br/>t{df_str} = {t:.2f}<br/>p = {p_str} {sig}".rstrip()


def respvar_from_name(name: str) -> str:
    m = re.search(r".*__([^\\.]+)\.csv$", name)
    return m.group(1) if m else ""


def sort_coef_key(coef: str) -> int:
    return COEF_ORDER.get(str(coef), 999)


def build_within_table(
    stem: str,
    out_root: Path,
    *,
    respvars: Optional[List[str]] = None,
    respvar_labels: Optional[Dict[str, str]] = None,
) -> str:
    respvars = list(RESPVARS if respvars is None else respvars)
    respvar_labels = RESPVAR_LABELS if respvar_labels is None else respvar_labels
    stem_dir = out_root / stem
    files = sorted(stem_dir.glob("within_summary__*.csv"))
    if not files:
        return "<p><em>None</em></p>\n"
    dfs = []
    for fp in files:
        rv = respvar_from_name(fp.name)
        d = pd.read_csv(fp)
        d = d.assign(respvar=rv)
        dfs.append(d)
    d = pd.concat(dfs, ignore_index=True)
    if len(respvars):
        d_keep = d[d["respvar"].isin(respvars)]
        if len(d_keep) > 0:
            d = d_keep
    if d.empty:
        return "<p><em>None</em></p>\n"
    pcol = pick_raw_p(d) or "p"

    col_order = [respvar_labels.get(rv, rv) for rv in respvars]

    d2 = d.copy()
    d2["cell"] = [
        format_cell(row["mean"], row["se"], row["t"], row["df"], row[pcol]) for _, row in d2.iterrows()
    ]
    d2["rv_lab"] = d2["respvar"].map(lambda x: respvar_labels.get(x, x))
    d2["coef_f"] = d2["coef"].map(sort_coef_key)
    d2 = d2[["choiceType", "coef", "coef_f", "rv_lab", "cell"]]

    # Pivot d2 directly. Merging drop_duplicates with d2 renames overlapping cols to cell_x/cell_y.
    wide = d2.pivot_table(
        index=["choiceType", "coef", "coef_f"], columns="rv_lab", values="cell", aggfunc="first"
    )
    wide = wide.reset_index().sort_values(["choiceType", "coef_f", "coef"])
    wide = wide.rename(columns={"choiceType": "group"})
    first_cols = ["group", "coef"]
    ordered = first_cols + [c for c in col_order if c in wide.columns] + [
        c for c in wide.columns if c not in first_cols + col_order and c != "coef_f"
    ]
    wide = wide[[c for c in ordered if c in wide.columns]].drop(columns=["coef_f"], errors="ignore")

    between_files = sorted(stem_dir.glob("between_summary__*.csv"))
    if between_files:
        dfs_b = []
        for fp in between_files:
            rv = respvar_from_name(fp.name)
            db = pd.read_csv(fp)
            db = db.assign(respvar=rv)
            dfs_b.append(db)
        d_b = pd.concat(dfs_b, ignore_index=True)
        if len(respvars):
            dk = d_b[d_b["respvar"].isin(respvars)]
            if len(dk) > 0:
                d_b = dk
        if not d_b.empty:
            pcol_b = pick_raw_p(d_b) or "p"
            d2b = d_b.copy()
            d2b["cell"] = [
                format_cell(row["mean"], row["se"], row["t"], row["df"], row[pcol_b])
                for _, row in d2b.iterrows()
            ]
            d2b["rv_lab"] = d2b["respvar"].map(lambda x: respvar_labels.get(x, x))
            d2b["coef_f"] = d2b["coef"].map(sort_coef_key)
            d2b = d2b.rename(columns={"pair": "group"})
            d2b = d2b[["group", "coef", "coef_f", "rv_lab", "cell"]]
            wide_b = d2b.pivot_table(
                index=["group", "coef", "coef_f"], columns="rv_lab", values="cell", aggfunc="first"
            )
            wide_b = wide_b.reset_index().sort_values(["group", "coef_f", "coef"])
            ordered_b = first_cols + [c for c in col_order if c in wide_b.columns] + [
                c for c in wide_b.columns if c not in first_cols + col_order and c != "coef_f"
            ]
            wide_b = wide_b[[c for c in ordered_b if c in wide_b.columns]].drop(columns=["coef_f"], errors="ignore")
            wide = pd.concat([wide, wide_b], ignore_index=True)

    return _html_table_from_wide(wide) + "\n"


def format_ttest_cell(t: float, dfv: float, p: float) -> str:
    sig = sig_symbol(float(p)) if pd.notna(p) else ""
    p_txt = "" if pd.isna(p) else (".000" if float(p) < 0.001 else f"{float(p):.3f}")
    df_i = int(round(dfv)) if pd.notna(dfv) else 0
    return f"t<sub>{df_i}</sub> = {t:.2f}<br/>p = {p_txt} {sig}".rstrip()


def build_ttests_table(
    stem: str,
    out_root: Path,
    *,
    respvars: Optional[List[str]] = None,
    respvar_labels: Optional[Dict[str, str]] = None,
) -> str:
    respvars = list(RESPVARS if respvars is None else respvars)
    respvar_labels = RESPVAR_LABELS if respvar_labels is None else respvar_labels
    stem_dir = out_root / stem
    files = sorted(stem_dir.glob("ttests_incentives__*.csv"))
    if not files:
        return "<p><em>None</em></p>\n"
    dfs = []
    for fp in files:
        rv = respvar_from_name(fp.name)
        d = pd.read_csv(fp)
        d = d.assign(respvar=rv)
        dfs.append(d)
    d = pd.concat(dfs, ignore_index=True)
    if len(respvars):
        dk = d[d["respvar"].isin(respvars)]
        if len(dk) > 0:
            d = dk
    if d.empty:
        return "<p><em>None</em></p>\n"
    col_order = [respvar_labels.get(rv, rv) for rv in respvars]
    d2 = d.copy()
    d2["cell"] = [format_ttest_cell(row["t"], row["df"], row["p"]) for _, row in d2.iterrows()]
    d2["rv_lab"] = d2["respvar"].map(lambda x: respvar_labels.get(x, x))
    d2 = d2[["group", "comparison", "rv_lab", "cell"]]
    d2["group_f"] = pd.Categorical(d2["group"], categories=sorted(d2["group"].unique()), ordered=True)
    d2["comparison_f"] = pd.Categorical(d2["comparison"], categories=sorted(d2["comparison"].unique()), ordered=True)
    wide = d2.pivot_table(
        index=["group", "comparison", "group_f", "comparison_f"],
        columns="rv_lab",
        values="cell",
        aggfunc="first",
    )
    wide = wide.reset_index().sort_values(["group_f", "comparison_f"])
    wide = wide.drop(columns=["group_f", "comparison_f"], errors="ignore")
    lead = ["group", "comparison"]
    ordered = lead + [c for c in col_order if c in wide.columns] + [
        c for c in wide.columns if c not in lead + col_order
    ]
    wide = wide[[c for c in ordered if c in wide.columns]]
    return _html_table_from_wide(wide) + "\n"


def discover_stem_paths(out_root: Path) -> List[Path]:
    patterns = (
        "within_summary__*.csv",
        "between_summary__*.csv",
        "ttests_incentives__*.csv",
        "gain_loss_corr__*.csv",
    )
    seen = set()
    for pat in patterns:
        for fp in out_root.rglob(pat):
            seen.add(fp.parent.resolve())
    return sorted(seen)


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
    ap.add_argument("--out-root", type=Path, default=Path("results/stats/average"))
    ap.add_argument("--output-md", type=Path, default=None)
    args = ap.parse_args()
    out_root = args.out_root.resolve()
    output_md = args.output_md or (out_root / "stats_tables.md")
    if not out_root.is_dir():
        raise SystemExit(f"OUT_ROOT does not exist: {out_root}")

    stem_paths = discover_stem_paths(out_root)
    if not stem_paths:
        raise SystemExit(f"No summary CSVs found under: {out_root}")

    lines: List[str] = ["# Aggregate stats summary", ""]
    for stem_path in stem_paths:
        stem = stem_path.name
        lines.append(f"## Dataset: {stem}")
        lines.append("")
        lines.append("### Within- and between-group effects")
        lines.append("")
        lines.append(build_within_table(stem, out_root))
        lines.append("---")
        lines.append("")
        lines.append("### Paired t-tests between incentive conditions")
        lines.append("")
        lines.append(build_ttests_table(stem, out_root))
        lines.append("")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {output_md}")


if __name__ == "__main__":
    main()
