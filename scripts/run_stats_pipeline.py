"""
Run the full Python stats pipeline in order:

  1) motivbelief.stats_avg → participant-average GLM outputs
  2) motivbelief.make_stats_avg_summary → aggregate markdown (stats_tables.md)
  3) motivbelief.stats_xpatt → trial-level xpatt outputs
  4) motivbelief.make_stats_xpatt_summary → aggregate xpatt markdown
  5) motivbelief.make_effectsize_tables → Cohen's d tables under effectsizes/
  6) motivbelief.stats.stats_hmeta → meta-d′ beta0/beta1 coh regressions + AVG-style incentive
     stats, then motivbelief.stats.make_stats_hmeta_summary → aggregate markdown
     (needs results/hmeta_d/)

Defaults mirror the standalone modules (`results/stats/...`).

Usage:
  python scripts/run_stats_pipeline.py
  python scripts/run_stats_pipeline.py --repo-root . --avg-root results/stats/average
  python scripts/run_stats_pipeline.py --skip-hmeta
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_SRC = _REPO / "src"


def _env_with_src() -> dict:
    env = os.environ.copy()
    prev = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(_SRC) + (os.pathsep + prev if prev else "")
    return env


def _run_module(
    repo: Path, module: str, extra: list[str], *, with_repo_root: bool = True
) -> None:
    if with_repo_root:
        cmd = [sys.executable, "-m", module, "--repo-root", str(repo)] + extra
    else:
        cmd = [sys.executable, "-m", module] + extra
    print("+", " ".join(cmd), flush=True)
    subprocess.check_call(cmd, cwd=str(repo), env=_env_with_src())


def run_stats_pipeline(
    repo_root: Path,
    *,
    avg_root_rel: Path,
    trial_root_rel: Path,
    effects_root_rel: Path,
    hmeta_root_rel: Path,
    skip_hmeta: bool = False,
) -> None:
    repo = repo_root.resolve()
    avg_root = (repo / avg_root_rel).resolve()
    trial_root = (repo / trial_root_rel).resolve()
    effects_root = (repo / effects_root_rel).resolve()
    hmeta_root = (repo / hmeta_root_rel).resolve()

    # 1–2: average stats + summary doc
    _run_module(repo, "motivbelief.stats.stats_avg", ["--out-root", str(avg_root)])
    _run_module(
        repo,
        "motivbelief.stats.make_stats_avg_summary",
        ["--out-root", str(avg_root)],
        with_repo_root=False,
    )

    # 3–4: trial xpatt + aggregate xpatt markdown
    _run_module(repo, "motivbelief.stats.stats_xpatt", ["--out-root", str(trial_root)])
    _run_module(
        repo,
        "motivbelief.stats.make_stats_xpatt_summary",
        ["--trial-root", str(trial_root)],
        with_repo_root=False,
    )

    # 5: effect sizes (paths relative to repo, same as make_effectsize_tables CLI)
    _run_module(
        repo,
        "motivbelief.stats.make_effectsize_tables",
        [
            "--avg-root",
            str(avg_root_rel).replace("\\", "/"),
            "--trial-root",
            str(trial_root_rel).replace("\\", "/"),
            "--out-root",
            str(effects_root_rel).replace("\\", "/"),
        ],
    )

    # 6: meta-d′ stats (skippable; also no-ops if fits missing) + aggregate summary
    if not skip_hmeta:
        _run_module(repo, "motivbelief.stats.stats_hmeta", ["--out-root", str(hmeta_root)])
        _run_module(
            repo,
            "motivbelief.stats.make_stats_hmeta_summary",
            ["--out-root", str(hmeta_root)],
            with_repo_root=False,
        )

    done = f"Done. Outputs: {avg_root}, {trial_root}, {effects_root}"
    if not skip_hmeta:
        done += f", {hmeta_root}"
    print(done, flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Run stats_avg → summaries → stats_xpatt → effect sizes → stats_hmeta."
    )
    ap.add_argument("--repo-root", type=Path, default=Path("."), help="Project root (default: cwd)")
    ap.add_argument(
        "--avg-root",
        type=Path,
        default=Path("results/stats/average"),
        help="Output folder for stats_avg (relative to repo unless absolute)",
    )
    ap.add_argument(
        "--trial-root",
        type=Path,
        default=Path("results/stats/trial"),
        help="Output folder for stats_xpatt (relative to repo unless absolute)",
    )
    ap.add_argument(
        "--effects-root",
        type=Path,
        default=Path("results/stats/effectsizes"),
        help="Output folder for make_effectsize_tables (relative to repo unless absolute)",
    )
    ap.add_argument(
        "--hmeta-root",
        type=Path,
        default=Path("results/stats/hmeta"),
        help="Output folder for stats_hmeta (relative to repo unless absolute)",
    )
    ap.add_argument(
        "--skip-hmeta",
        action="store_true",
        help="Skip meta-d′ stats (step 6)",
    )
    args = ap.parse_args()
    run_stats_pipeline(
        args.repo_root,
        avg_root_rel=args.avg_root,
        trial_root_rel=args.trial_root,
        effects_root_rel=args.effects_root,
        hmeta_root_rel=args.hmeta_root,
        skip_hmeta=args.skip_hmeta,
    )


if __name__ == "__main__":
    main()
