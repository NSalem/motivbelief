"""Analysis specs for optional non-free (Observed/Forced/Replayed) simulations.

Mirrors ``stats_avg.build_analysis_specs`` sim entries, but scoped to each
condition's own fitted model
(``scripts/_optional/simulate_belief_models_nonfree_fitted.py``). Used only by
``scripts/_optional/run_stats_pipeline_fitted_nonfree.py`` and
``scripts/_optional/plot_falsif_xpatt_nonfree.py``.

Also builds a Merged pool (Observed+Forced+Replayed) under the existing
``Non-Free`` group label.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, Optional

import numpy as np
import pandas as pd

from motivbelief.stats.stats_avg import read_data

# act↔+1, intent↔-1, confirm↔0 (see analysis_free.REPLAYED_MISMATCH_COEFS).
NONFREE_CONDITIONS = ("Observed", "Forced", "Replayed")
NONFREE_MODELS = ("act", "intent", "confirm")

MERGED_GROUP = "Non-Free"

# Pooled real data: exp1a+exp2+exp3 by recorded choiceType (exp1b excluded).
REAL_DATA_STEM = "exp1a_exp2_exp3_bycondition"
REAL_DATA_MERGED_STEM = "exp1a_exp2_exp3_merged"


def sim_stem(condition: str, model: str) -> str:
    """Stem for sims_fitted_<condition>_<model>.csv."""
    return f"sim_{condition.lower()}_{model}"


def merged_sim_stem(model: str) -> str:
    """Stem for one model's pooled Observed+Forced+Replayed sim."""
    return f"sim_merged_{model}"


def _real_data_bycondition(repo_root: Path) -> pd.DataFrame:
    data = repo_root / "data"
    return pd.concat(
        [
            read_data(data / "data_exp1a.csv", "Exp1a"),
            read_data(data / "data_exp2.csv", "Exp2"),
            read_data(data / "data_exp3.csv", "Exp3"),
        ],
        ignore_index=True,
    )


def _real_data_merged(repo_root: Path) -> pd.DataFrame:
    df = _real_data_bycondition(repo_root).copy()
    df["choiceType"] = np.where(
        df["choiceType"].astype(str).isin(NONFREE_CONDITIONS),
        MERGED_GROUP,
        df["choiceType"],
    )
    return df


def _sim_path(sims_dir: Path, condition: str, model: str) -> Path:
    return sims_dir / f"sims_fitted_{condition.lower()}_{model}.csv"


def _load_sim(sims_dir: Path, condition: str, model: str) -> pd.DataFrame:
    tag = f"Sims {condition[:3]} {model.title()}"
    return read_data(_sim_path(sims_dir, condition, model), tag)


def _load_sim_merged(sims_dir: Path, model: str) -> pd.DataFrame:
    """Pool one model's per-condition sims into MERGED_GROUP."""
    parts = [_load_sim(sims_dir, c, model) for c in NONFREE_CONDITIONS]
    df = pd.concat(parts, ignore_index=True)
    df["choiceType"] = MERGED_GROUP
    return df


def build_nonfree_analysis_specs(
    repo_root: Path | str,
    sims_dir: Path | str | None = None,
) -> Dict[str, Dict[str, Callable]]:
    """Specs in the same ``{"build": callable}`` shape as ``stats_avg.build_analysis_specs``."""
    repo_root = Path(repo_root)
    sims_dir = Path(sims_dir) if sims_dir is not None else repo_root / "results" / "sims"

    specs: Dict[str, Dict[str, Callable]] = {
        REAL_DATA_STEM: {"build": lambda: _real_data_bycondition(repo_root)},
        REAL_DATA_MERGED_STEM: {"build": lambda: _real_data_merged(repo_root)},
    }
    for condition in NONFREE_CONDITIONS:
        for model in NONFREE_MODELS:
            specs[sim_stem(condition, model)] = {
                "build": (lambda c=condition, m=model: _load_sim(sims_dir, c, m)),
            }
    for model in NONFREE_MODELS:
        specs[merged_sim_stem(model)] = {
            "build": (lambda m=model: _load_sim_merged(sims_dir, m)),
        }
    return specs
