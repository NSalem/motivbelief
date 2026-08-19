#!/usr/bin/env python3
"""Fit Bayesian individual meta-d′ (CRAN hmetad).

Thin wrapper around ``scripts/r/fit_hmeta_d.R`` (participant × choiceType;
Free / Observed / Forced / Replayed; incentive × coh3).

Examples:
  python scripts/fit_hmeta_d.py --dataset exp1a
  python scripts/fit_hmeta_d.py --all
  python scripts/fit_hmeta_d.py --dataset exp1a --max-subjects 2
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_R_SCRIPT = _REPO / "scripts" / "r" / "fit_hmeta_d.R"


def _find_rscript() -> str:
    env = os.environ.get("CONDA_PREFIX")
    if env:
        cand = Path(env) / "bin" / "Rscript"
        if cand.is_file():
            return str(cand)
    # Common motivbelief env path
    for cand in (
        Path("/root/anaconda3/envs/motivbelief/bin/Rscript"),
        Path.home() / "anaconda3/envs/motivbelief/bin/Rscript",
    ):
        if cand.is_file():
            return str(cand)
    which = shutil.which("Rscript")
    if which:
        return which
    raise FileNotFoundError(
        "Rscript not found. Activate the motivbelief conda env or put Rscript on PATH."
    )


def main(argv: list[str] | None = None) -> None:
    # Forward unknown args to R; only peel --help for a short Python banner.
    ap = argparse.ArgumentParser(
        description=(
            "Bayesian individual meta-d' via hmetad (wraps scripts/r/fit_hmeta_d.R). "
            "All flags are forwarded to the R script."
        ),
        add_help=False,
    )
    ap.add_argument("-h", "--help", action="store_true")
    args, rest = ap.parse_known_args(argv)

    rscript = _find_rscript()
    cmd = [rscript, str(_R_SCRIPT), *rest]
    if args.help and not rest:
        cmd.append("--help")
    print(" ".join(cmd), flush=True)
    raise SystemExit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
