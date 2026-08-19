"""
Build a single markdown document aggregating within-group CONF (xpatt) tables
across experiments and data vs simulation models.
"""

from __future__ import annotations

import argparse
import html
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import pandas as pd

from motivbelief.stats.stats_xpatt import UMINUS, combine5


def _read_within(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Missing within-group table: {path}")
    return pd.read_csv(path)


def _read_between(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Missing between-group table: {path}")
    return pd.read_csv(path)


def _cell_from_row(r: pd.Series, digits: int) -> str:
    return combine5(
        float(r["estimate"]),
        float(r["se"]),
        float(r["t"]),
        float(r["df"]),
        float(r["p"]),
        float(r["lcl"]),
        float(r["ucl"]),
        digits,
    )


def _cell(
    within: pd.DataFrame, effect: str, group: str, digits: int, empty: str = "—"
) -> str:
    sub = within[(within["Effect"] == effect) & (within["Group"] == group)]
    if sub.empty:
        return empty
    return _cell_from_row(sub.iloc[0], digits)


def _effect_order_union(*dfs: pd.DataFrame) -> List[str]:
    seen: Dict[str, None] = {}
    for d in dfs:
        for e in d["Effect"].astype(str):
            if e not in seen:
                seen[e] = None
    return list(seen.keys())


def _th_effect() -> str:
    return '<th rowspan="2" scope="col">Effect</th>'


def _escape_effect_text(s: str) -> str:
    # Escape first so & in entities is not double-escaped; then | → &#124; for display.
    return html.escape(str(s)).replace("|", "&#124;")


def _html_table(
    parent_headers: Sequence[Tuple[str, int]],
    leaf_headers: Sequence[str],
    rows: Sequence[Tuple[str, Sequence[str]]],
) -> str:
    """parent_headers: (label, colspan) for each top header cell (after Effect)."""
    n_leaf = len(leaf_headers)
    if sum(c for _, c in parent_headers) != n_leaf:
        raise ValueError("parent colspan must match number of leaf columns")

    lines = [
        "<table>",
        "<thead>",
        "<tr>",
        _th_effect(),
    ]
    for lab, cs in parent_headers:
        lines.append(f'<th colspan="{cs}" scope="colgroup">{html.escape(lab)}</th>')
    lines.extend(["</tr>", "<tr>"])
    for h in leaf_headers:
        lines.append(f'<th scope="col">{html.escape(h)}</th>')
    lines.extend(["</tr>", "</thead>", "<tbody>"])

    for eff, cells in rows:
        lines.append("<tr>")
        lines.append(f'<th scope="row">{_escape_effect_text(eff)}</th>')
        for c in cells:
            lines.append(f"<td>{c}</td>")
        lines.append("</tr>")

    lines.extend(["</tbody>", "</table>"])
    return "\n".join(lines)


def _html_table_simple(
    column_headers: Sequence[str],
    rows: Sequence[Tuple[str, Sequence[str]]],
) -> str:
    """Single header row: Effect + one column per header."""
    lines = ["<table>", "<thead>", "<tr>", '<th scope="col">Effect</th>']
    for h in column_headers:
        lines.append(f'<th scope="col">{html.escape(h)}</th>')
    lines.extend(["</tr>", "</thead>", "<tbody>"])
    for eff, cells in rows:
        lines.append("<tr>")
        lines.append(f'<th scope="row">{_escape_effect_text(eff)}</th>')
        for c in cells:
            lines.append(f"<td>{c}</td>")
        lines.append("</tr>")
    lines.extend(["</tbody>", "</table>"])
    return "\n".join(lines)


def _md_section(title: str, body: str) -> str:
    return f"## {title}\n\n{body}\n"


def build_table1_across_exp(
    trial_root: Path, digits: int = 2
) -> str:
    p1a = trial_root / "exp1a" / "within_group_conf_xpatt.csv"
    p2 = trial_root / "exp2" / "within_group_conf_xpatt.csv"
    p3 = trial_root / "exp3" / "within_group_conf_xpatt.csv"
    w1 = _read_within(p1a)
    w2 = _read_within(p2)
    w3 = _read_within(p3)
    effects = _effect_order_union(w1, w2, w3)

    parent_headers = [
        ("Exp 1a", 2),
        ("Exp 2", 2),
        ("Exp 3", 2),
    ]
    leaf_headers = ["Free", "Observed", "Free", "Observed", "Replayed", "Forced"]

    specs: List[Tuple[pd.DataFrame, str]] = [
        (w1, "Free"),
        (w1, "Observed"),
        (w2, "Free"),
        (w2, "Observed"),
        (w3, "Replayed"),
        (w3, "Forced"),
    ]

    rows: List[Tuple[str, List[str]]] = []
    for eff in effects:
        cells = [_cell(w, eff, g, digits) for w, g in specs]
        rows.append((eff, cells))

    return _html_table(parent_headers, leaf_headers, rows)


def build_table2_exp1b(trial_root: Path, digits: int = 2) -> str:
    w = _read_within(trial_root / "exp1b" / "within_group_conf_xpatt.csv")
    effects = w["Effect"].astype(str).unique().tolist()
    parent_headers = [("Exp 1b", 2)]
    leaf_headers = ["Free", "Observed"]
    rows = []
    for eff in effects:
        cells = [_cell(w, eff, "Free", digits), _cell(w, eff, "Observed", digits)]
        rows.append((eff, cells))
    return _html_table(parent_headers, leaf_headers, rows)


def build_table3_merged_and_models(trial_root: Path, digits: int = 2) -> str:
    data = _read_within(trial_root / "exp1a_exp2free_exp3" / "within_group_conf_xpatt.csv")
    act = _read_within(trial_root / "sim_act" / "within_group_conf_xpatt.csv")
    intent = _read_within(trial_root / "sim_intent" / "within_group_conf_xpatt.csv")
    confm = _read_within(trial_root / "sim_confirm" / "within_group_conf_xpatt.csv")
    effects = _effect_order_union(data, act, intent, confm)

    parent_headers = [
        ("Data (1a, 2 free, 3)", 2),
        ("All models", 1),
        ("Act model", 1),
        ("Intent model", 1),
        ("Confirm model", 1),
    ]
    leaf_headers = [
        "Free",
        "Non-Free",
        "Free",
        "Non-Free",
        "Non-Free",
        "Non-Free",
    ]

    rows = []
    for eff in effects:
        cells = [
            _cell(data, eff, "Free", digits),
            _cell(data, eff, "Non-Free", digits),
            _cell(act, eff, "Free", digits),
            _cell(act, eff, "Non-Free", digits),
            _cell(intent, eff, "Non-Free", digits),
            _cell(confm, eff, "Non-Free", digits),
        ]
        rows.append((eff, cells))

    tbl = _html_table(parent_headers, leaf_headers, rows)
    note = (
        "<p><em><strong>All models</strong>: Free-condition slopes from the act simulation (one shared Free "
        "column for comparison with the three Non-Free model columns).</em></p>"
    )
    return tbl + "\n\n" + note


def build_table4_free_nonfree_between(trial_root: Path, digits: int = 2) -> str:
    """Free vs Non-Free contrast for merged data and each simulation stem.

    Data uses a Welch two-sample test (Free and Non-Free are disjoint real
    subject pools). Each model column uses a paired t-test instead, because
    the simulations pair every subject's Free and Non-Free prediction from
    one fitted model (see ``tidy_pairwise_group``); the point estimate is
    unchanged by this, only its precision.
    """
    contrast = f"Free {UMINUS} Non-Free"
    stems: List[Tuple[str, Path]] = [
        ("Data (1a, 2 free, 3)", trial_root / "exp1a_exp2free_exp3" / "between_groups_conf_xpatt_ttests.csv"),
        ("Act model", trial_root / "sim_act" / "between_groups_conf_xpatt_ttests.csv"),
        ("Intent model", trial_root / "sim_intent" / "between_groups_conf_xpatt_ttests.csv"),
        ("Confirm model", trial_root / "sim_confirm" / "between_groups_conf_xpatt_ttests.csv"),
    ]
    loaded = [(label, _read_between(p)) for label, p in stems]
    effects = _effect_order_union(*[d for _, d in loaded])

    def cell(between: pd.DataFrame, effect: str) -> str:
        sub = between[(between["Effect"] == effect) & (between["Contrast"].astype(str) == contrast)]
        if sub.empty:
            return "—"
        return _cell_from_row(sub.iloc[0], digits)

    rows: List[Tuple[str, List[str]]] = []
    for eff in effects:
        rows.append((eff, [cell(d, eff) for _, d in loaded]))
    headers = [label for label, _ in loaded]
    tbl = _html_table_simple(headers, rows)
    note = (
        "<p><em>Data: Welch two-sample test (disjoint Free/Non-Free subject pools). "
        "Model columns: paired t-test, since each simulated Non-Free prediction is "
        "generated from the same fitted subject as its Free counterpart -- point "
        "estimates match a Welch test exactly; only se/t/df/p/CI reflect the pairing.</em></p>"
    )
    return tbl + "\n\n" + note


def render_aggregate_xpatt_md(trial_root: Path, digits: int = 2) -> str:
    trial_root = trial_root.resolve()
    parts = [
        "# CONF (xpatt): aggregate tables\n",
        _md_section(
            "1. Across Exp 1a, 2, and 3 (within-group)",
            build_table1_across_exp(trial_root, digits=digits),
        ),
        _md_section(
            "2. Exp 1b (within-group)",
            build_table2_exp1b(trial_root, digits=digits),
        ),
        _md_section(
            "3. Merged human data (1a, 2 free, 3) and simulations (within-group)",
            build_table3_merged_and_models(trial_root, digits=digits),
        ),
        _md_section(
            "4. Free − Non-Free difference (aggregated data and models)",
            build_table4_free_nonfree_between(trial_root, digits=digits),
        ),
    ]
    return "\n".join(parts)


def write_aggregate_xpatt_md(
    trial_root: Path,
    out_path: Optional[Path] = None,
    digits: int = 2,
) -> Path:
    trial_root = trial_root.resolve()
    if out_path is None:
        out_path = trial_root / "summary_conf_xpatt_aggregate.md"
    else:
        out_path = out_path.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = render_aggregate_xpatt_md(trial_root, digits=digits)
    out_path.write_text(text, encoding="utf-8")
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description="Write aggregate xpatt CONF markdown tables.")
    ap.add_argument(
        "--trial-root",
        type=Path,
        default=Path("results/stats/trial"),
        help="Directory containing per-stem subfolders (exp1a, exp2, …).",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output .md path (default: <trial-root>/summary_conf_xpatt_aggregate.md).",
    )
    ap.add_argument("--digits", type=int, default=2)
    args = ap.parse_args()
    p = write_aggregate_xpatt_md(args.trial_root, out_path=args.out, digits=args.digits)
    print(p)


if __name__ == "__main__":
    main()
