"""
Aggregate meta-d′ β0/β1 incentive-stats CSVs (``results/stats/hmeta/``) into
``stats_tables_hmeta.md``, using the same within/between-group and paired
incentive-comparison table format as
:mod:`motivbelief.stats.make_stats_avg_summary` (accuracy/belief/calibration/...).

Usage:
  python -m motivbelief.stats.make_stats_hmeta_summary
  python -m motivbelief.stats.make_stats_hmeta_summary --out-root results/stats/hmeta
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

from motivbelief.stats.make_stats_avg_summary import (
    build_ttests_table,
    build_within_table,
    discover_stem_paths,
)

RESPVARS: List[str] = ["beta0", "beta1"]
RESPVAR_LABELS: Dict[str, str] = {
    "beta0": "β0 (meta-d′ level)",
    "beta1": "β1 (coh slope)",
}


def _bootstrap_path() -> None:
    import sys

    repo_src = Path(__file__).resolve().parents[2] / "src"
    s = str(repo_src)
    if s not in sys.path:
        sys.path.insert(0, s)


def main() -> None:
    if __package__ in (None, ""):
        _bootstrap_path()
    ap = argparse.ArgumentParser(
        description="Aggregate meta-d′ beta0/beta1 within/between/paired-incentive tables (stats_hmeta output)."
    )
    ap.add_argument("--out-root", type=Path, default=Path("results/stats/hmeta"))
    ap.add_argument("--output-md", type=Path, default=None)
    args = ap.parse_args()
    out_root = args.out_root.resolve()
    output_md = args.output_md or (out_root / "stats_tables_hmeta.md")
    if not out_root.is_dir():
        raise SystemExit(f"OUT_ROOT does not exist: {out_root}")

    stem_paths = discover_stem_paths(out_root)
    if not stem_paths:
        raise SystemExit(f"No summary CSVs found under: {out_root}")

    lines: List[str] = ["# Meta-d′ (β0 / β1) aggregate stats summary", ""]
    for stem_path in stem_paths:
        stem = stem_path.name
        lines.append(f"## Dataset: {stem}")
        lines.append("")
        lines.append("### Within- and between-group effects")
        lines.append("")
        lines.append(build_within_table(stem, out_root, respvars=RESPVARS, respvar_labels=RESPVAR_LABELS))
        lines.append("---")
        lines.append("")
        lines.append("### Paired t-tests between incentive conditions")
        lines.append("")
        lines.append(build_ttests_table(stem, out_root, respvars=RESPVARS, respvar_labels=RESPVAR_LABELS))
        lines.append("")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {output_md}")


if __name__ == "__main__":
    main()
