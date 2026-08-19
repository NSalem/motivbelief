"""
Meta-d′ / M-ratio figures from ``results/hmeta_d/<dataset>/``.

Default fits are **Bayesian individual** (``Rscript scripts/r/fit_hmeta_d.R``,
``fit_mode=bayes_individual``; Free / Observed / Forced / Replayed):
- curves from ``cell_mratio_summary.csv`` (meta-d′, *M*-ratio)
- type-2 criteria from ``subject_summary.csv`` (``metac2*``, averaged over S1/S2)
- incentive effects from ``subject_effects.csv`` (violins)

Layouts (condition = rows, dataset = columns):
- by experiment: Exp 1a / 1b / 2 / 3 — top Free|Replayed, bottom Observed|Forced
  (condition name drawn inside each panel; shared y-axis)
- data vs models: pooled data (1a+2) / sim act / intent / confirm — Free / Observed rows

Each layout writes four figures: meta-d′, *M*-ratio, type-2 criteria, incentive effects.
"""

from __future__ import annotations

import argparse
import json
import re
import warnings
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import ttest_1samp

from motivbelief.plotting.artists import kde_violin
from motivbelief.plotting.paths import fig_dir
from motivbelief.plotting.style import (
    CMAP_EXP1B,
    INC_LABELS,
    INC_LEVELS,
    INC_LINE_COLOR,
    save_fig,
)

BY_EXP: Tuple[Tuple[str, str], ...] = (
    ("exp1a", "Exp 1a"),
    ("exp1b", "Exp 1b"),
    ("exp2", "Exp 2"),
    ("exp3", "Exp 3"),
)
DATA_VS_MODELS: Tuple[Tuple[str, str], ...] = (
    ("merged", "Data (1a+2)"),  # virtual: pools exp1a+exp2 fit outputs (not a separate fit)
    ("sim_act", "Sim act"),
    ("sim_intent", "Sim intent"),
    ("sim_confirm", "Sim confirm"),
)

# Per-experiment agency pairing (same as psyfun / behav): top Free|Replayed, bottom Observed|Forced
BY_EXP_TOP_CONDITION = {
    "exp1a": "Free",
    "exp1b": "Free",
    "exp2": "Free",
    "exp3": "Replayed",
}
BY_EXP_BOTTOM_CONDITION = {
    "exp1a": "Observed",
    "exp1b": "Observed",
    "exp2": "Observed",
    "exp3": "Forced",
}

# Free merge for data-vs-models (same cohort as BMC / param violins)
MERGE_FIT_SOURCES: Tuple[str, ...] = ("exp1a", "exp2")

EFFECT_SPECS: Tuple[Tuple[str, str, Tuple[float, float, float]], ...] = (
    ("mu_incentive", r"$\log M$", (0.2, 0.45, 0.75)),
    ("mu_incentive_coh3", r"$\times$coh", (0.85, 0.45, 0.15)),
    ("type2_incentive", "type-2", (0.45, 0.45, 0.45)),
)

COH3_TICKS = (-1.0, 0.0, 1.0)
COH3_LABELS = {-1.0: "low", 0.0: "mid", 1.0: "high"}

FONT_SIZE = 10.0
SPINE_LW = 0.5
PANEL_W = PANEL_H = 1.75  # square curve / type-2 panels
# Effects violins: narrower columns, taller panels
EFFECTS_PANEL_W, EFFECTS_PANEL_H = 1.25, 2.15
RNG = np.random.default_rng(42)

_METAC2_PARAM = re.compile(
    r"^metac2(zero|one)(\d+)diff_(Intercept|incentive0|incentive1)$"
)


def hmeta_root(repo: Path) -> Path:
    return repo.resolve() / "results" / "hmeta_d"


def dataset_dir(repo: Path, dataset: str) -> Path:
    return hmeta_root(repo) / dataset


def _load_json(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def load_meta(repo: Path, dataset: str) -> dict:
    if dataset == "merged":
        for k in MERGE_FIT_SOURCES:
            meta = load_meta(repo, k)
            if meta:
                return meta
        return {}
    path = dataset_dir(repo, dataset) / "meta.json"
    if path.is_file():
        return _load_json(path)
    return {}


def load_subject_effects(repo: Path, dataset: str) -> Optional[pd.DataFrame]:
    if dataset == "merged":
        parts = [load_subject_effects(repo, k) for k in MERGE_FIT_SOURCES]
        parts = [p for p in parts if p is not None]
        if not parts:
            return None
        return pd.concat(parts, ignore_index=True)
    path = dataset_dir(repo, dataset) / "subject_effects.csv"
    if not path.is_file() or path.stat().st_size < 80:
        return None
    df = pd.read_csv(path)
    return None if df.empty else df


def _pool_cell_summaries(parts: List[pd.DataFrame]) -> Optional[pd.DataFrame]:
    """N-weighted mean of group cell summaries across experiments."""
    if not parts:
        return None
    allc = pd.concat(parts, ignore_index=True)
    rows = []
    keys = ["incentive", "coh3", ".variable"]
    if "choiceType" in allc.columns:
        keys = ["choiceType"] + keys
    for _, g in allc.groupby(keys, sort=False):
        w = g["n"].to_numpy(dtype=float) if "n" in g.columns else np.ones(len(g))
        m = g["mean"].to_numpy(dtype=float) if "mean" in g.columns else g["q50"].to_numpy(dtype=float)
        ok = np.isfinite(w) & np.isfinite(m) & (w > 0)
        if not np.any(ok):
            continue
        w, m = w[ok], m[ok]
        n = float(np.sum(w))
        mean = float(np.average(m, weights=w))
        if "sem" in g.columns and np.all(np.isfinite(g["sem"].to_numpy(dtype=float)[ok])):
            sems = g["sem"].to_numpy(dtype=float)[ok]
            sem = float(np.sqrt(np.sum((w / n) ** 2 * sems**2)))
        else:
            sem = float("nan")
        row = {k: g.iloc[0][k] for k in keys}
        row.update(
            {
                "mean": mean,
                "sem": sem,
                "n": n,
                "q50": mean,
                "q2.5": mean - 1.96 * sem if np.isfinite(sem) else mean,
                "q97.5": mean + 1.96 * sem if np.isfinite(sem) else mean,
            }
        )
        rows.append(row)
    return pd.DataFrame(rows) if rows else None


def load_cell_summary(repo: Path, dataset: str) -> Optional[pd.DataFrame]:
    if dataset == "merged":
        parts = []
        for k in MERGE_FIT_SOURCES:
            p = load_cell_summary(repo, k)
            if p is not None:
                parts.append(p)
        return _pool_cell_summaries(parts)
    path = dataset_dir(repo, dataset) / "cell_mratio_summary.csv"
    if not path.is_file() or path.stat().st_size < 80:
        return None
    df = pd.read_csv(path)
    if df.empty or "coh3" not in df.columns or "incentive" not in df.columns:
        return None
    return df


def load_subject_summary(repo: Path, dataset: str) -> Optional[pd.DataFrame]:
    if dataset == "merged":
        parts = [load_subject_summary(repo, k) for k in MERGE_FIT_SOURCES]
        parts = [p for p in parts if p is not None]
        if not parts:
            return None
        return pd.concat(parts, ignore_index=True)
    path = dataset_dir(repo, dataset) / "subject_summary.csv"
    if not path.is_file() or path.stat().st_size < 80:
        return None
    df = pd.read_csv(path)
    return None if df.empty or "param" not in df.columns else df


def load_preparation(repo: Path, dataset: str) -> dict:
    if dataset == "merged":
        for k in MERGE_FIT_SOURCES:
            try:
                return load_preparation(repo, k)
            except FileNotFoundError:
                continue
        raise FileNotFoundError(
            f"No preparation.json under {hmeta_root(repo)} for {MERGE_FIT_SOURCES}"
        )
    path = dataset_dir(repo, dataset) / "preparation.json"
    if path.is_file():
        return _load_json(path)
    meta_path = dataset_dir(repo, dataset) / "meta.json"
    if meta_path.is_file():
        meta = _load_json(meta_path)
        prep = meta.get("preparation")
        if isinstance(prep, dict):
            return prep
    raise FileNotFoundError(path)


def available_datasets(repo: Path, wanted: Sequence[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Keep columns with modern coh3 cell summaries or incentive subject_effects.

    The virtual ``merged`` key is available when any of ``MERGE_FIT_SOURCES`` has fits.
    Legacy hierarchical dirs (no coh3 / no mu_incentive) are skipped quietly.
    """
    out: List[Tuple[str, str]] = []
    for key, title in wanted:
        if key == "merged":
            if any(
                load_subject_effects(repo, k) is not None or load_cell_summary(repo, k) is not None
                for k in MERGE_FIT_SOURCES
            ):
                out.append((key, title))
            else:
                warnings.warn(
                    "hmeta_d: no exp1a/exp2 fits to pool for virtual 'merged'; skipping"
                )
            continue
        se = load_subject_effects(repo, key)
        cell = load_cell_summary(repo, key)
        ok = False
        if cell is not None and ".variable" in cell.columns:
            ok = True
        if se is not None and any(c in se.columns for c, _, _ in EFFECT_SPECS):
            ok = True
        if ok:
            out.append((key, title))
    return out


def _choice_types_present(repo: Path, columns: Sequence[Tuple[str, str]]) -> List[str]:
    """Union of choiceType levels across available datasets (preferred order)."""
    found: set[str] = set()
    for key, _ in columns:
        for loader in (load_subject_effects, load_cell_summary, load_subject_summary):
            df = loader(repo, key)
            if df is not None and "choiceType" in df.columns:
                found.update(str(x) for x in df["choiceType"].dropna().unique())
                break
        else:
            prep = None
            try:
                prep = load_preparation(repo, key)
            except FileNotFoundError:
                pass
            if prep and prep.get("choice_types"):
                found.update(str(x) for x in prep["choice_types"])
            elif (
                load_subject_effects(repo, key) is not None
                or load_cell_summary(repo, key) is not None
                or load_subject_summary(repo, key) is not None
            ):
                found.add("Free")
    if not found:
        return ["Free"]
    preferred = ("Free", "Observed", "Forced", "Replayed")
    ordered = [c for c in preferred if c in found]
    ordered.extend(sorted(found - set(ordered)))
    return ordered


def _filter_choice_type(df: Optional[pd.DataFrame], choice_type: str) -> Optional[pd.DataFrame]:
    if df is None:
        return None
    if "choiceType" not in df.columns:
        return df if choice_type == "Free" else None
    out = df[df["choiceType"].astype(str) == str(choice_type)]
    return None if out.empty else out


def _incentive_key(inc: float | str | int) -> float:
    return float(inc)


def _format_inc_level(inc: float) -> str:
    v = float(inc)
    if float(v).is_integer():
        return str(int(v))
    return f"{v:g}"


def _incentive_levels(prep: dict, cell: Optional[pd.DataFrame] = None) -> List[float]:
    coding = prep.get("incentive_coding", {}) or {}
    levels = coding.get("raw_levels") or coding.get("levels")
    out: List[float] = []
    if levels:
        out = sorted({_incentive_key(x) for x in levels})
    if not out and cell is not None and "incentive" in cell.columns:
        out = sorted({_incentive_key(x) for x in cell["incentive"].unique()})
    if not out:
        out = [-1.0, 0.0, 1.0]
    return out


def _inc_color(inc: float | str, *, inc_levels: Optional[Sequence[float]] = None) -> str:
    """Incentive line color. Exp 1b's 0.1 uses darker green; level 1 / +1 share INC_LINE_COLOR[+1]."""
    del inc_levels  # levels unused for coloring (kept for call-site compatibility)
    try:
        v = _incentive_key(inc)
    except (TypeError, ValueError):
        return INC_LINE_COLOR.get(0.0, "#606060")
    if np.isclose(v, 0.1, atol=1e-6):
        return matplotlib_colors_to_hex(CMAP_EXP1B[0])
    for k, col in INC_LINE_COLOR.items():
        if np.isclose(v, k, atol=1e-6):
            return col
    return INC_LINE_COLOR.get(0.0, "#606060")


def matplotlib_colors_to_hex(rgb: Sequence[float]) -> str:
    r, g, b = (float(x) for x in rgb[:3])
    return f"#{int(round(r * 255)):02x}{int(round(g * 255)):02x}{int(round(b * 255)):02x}"


def _inc_label(inc: float | str, *, inc_levels: Optional[Sequence[float]] = None) -> str:
    del inc_levels
    try:
        v = _incentive_key(inc)
    except (TypeError, ValueError):
        return f"inc {inc}"
    if np.isclose(v, 0.1, atol=1e-6):
        return "inc 0.1"
    for k, lab in INC_LABELS.items():
        if np.isclose(v, k, atol=1e-6):
            return lab
    return f"inc {_format_inc_level(v)}"


def _p_to_stars(p: float) -> str:
    if not np.isfinite(p):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return ""


def _condition_for_panel(dataset: str, row_i: int, *, agency_rows: bool) -> Optional[str]:
    """choiceType for a grid cell; agency_rows uses Free/Replayed | Observed/Forced pairing."""
    if agency_rows:
        mapping = BY_EXP_TOP_CONDITION if row_i == 0 else BY_EXP_BOTTOM_CONDITION
        return mapping.get(dataset)
    return None


def _grid_row_specs(
    repo: Path,
    cols: Sequence[Tuple[str, str]],
    *,
    agency_rows: bool,
) -> List[str]:
    """Row labels (for bookkeeping). Agency layout is always two rows."""
    if agency_rows:
        return ["top", "bottom"]
    return _choice_types_present(repo, cols)


def _panel_condition_label(ax: plt.Axes, text: str) -> None:
    ax.text(
        0.04,
        0.96,
        text,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=FONT_SIZE - 1,
        color="0.2",
    )


def _apply_yticks(ax: plt.Axes, *, labelleft: bool = True) -> None:
    ax.yaxis.set_major_locator(plt.MaxNLocator(nbins=4, prune=None))
    ax.tick_params(axis="y", which="both", left=True, labelleft=labelleft)


def _finalize_shared_ylim(
    axes: np.ndarray,
    all_ys: List[float],
    *,
    pad_frac: float = 0.08,
    headroom: float = 0.0,
) -> None:
    if all_ys:
        lo, hi = _ylim_from_vals(all_ys, pad_frac=pad_frac)
        if headroom > 0:
            hi = hi + headroom * (hi - lo if hi > lo else 1.0)
    else:
        lo = hi = None
    for i in range(axes.shape[0]):
        for j in range(axes.shape[1]):
            ax = axes[i, j]
            if lo is not None:
                ax.set_ylim(lo, hi)
            _apply_yticks(ax, labelleft=(j == 0))


def _setup_rc() -> None:
    plt.rcParams.update(
        {
            "font.size": FONT_SIZE,
            "axes.titlesize": FONT_SIZE,
            "axes.labelsize": FONT_SIZE,
            "xtick.labelsize": FONT_SIZE - 1,
            "ytick.labelsize": FONT_SIZE - 1,
            "axes.linewidth": SPINE_LW,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def _blank(ax: plt.Axes, msg: str = "no data", *, clear_ticks: bool = True) -> None:
    ax.text(0.5, 0.5, msg, ha="center", va="center", transform=ax.transAxes, color="0.5")
    if clear_ticks:
        ax.set_xticks([])
        ax.set_yticks([])
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def _ylim_from_vals(all_vals: Iterable[float], *, pad_frac: float = 0.08) -> Tuple[float, float]:
    vals = [float(v) for v in all_vals if np.isfinite(v)]
    if not vals:
        return (-1.0, 1.0)
    lo, hi = min(vals), max(vals)
    pad = pad_frac * (hi - lo) if hi > lo else 0.5
    return lo - pad, hi + pad


def _style_panel(ax: plt.Axes, *, square: bool = False) -> None:
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    if square:
        ax.set_box_aspect(1)


# ---- cell curve panels (meta-d′ / M) --------------------------------------


def _draw_curve_panel(
    ax: plt.Axes,
    cell: Optional[pd.DataFrame],
    *,
    variable: str,
    prep: Optional[dict],
    show_legend: bool = False,
    condition_label: Optional[str] = None,
) -> List[float]:
    """Plot variable vs coh3 by incentive. Returns y values used (for shared ylim)."""
    if cell is None or cell.empty or prep is None:
        _blank(ax, clear_ticks=False)
        if condition_label:
            _panel_condition_label(ax, condition_label)
        ax.set_box_aspect(1)
        return []
    pred = cell.copy()
    pred["_inc"] = pred["incentive"].map(_incentive_key)
    sub = pred[pred[".variable"] == variable]
    if sub.empty:
        _blank(ax, clear_ticks=False)
        if condition_label:
            _panel_condition_label(ax, condition_label)
        ax.set_box_aspect(1)
        return []
    inc_levels = _incentive_levels(prep, pred)
    ys: List[float] = []
    for inc in inc_levels:
        s = sub[np.isclose(sub["_inc"].to_numpy(dtype=float), float(inc))].sort_values("coh3")
        if s.empty:
            continue
        color = _inc_color(inc, inc_levels=inc_levels)
        x = s["coh3"].to_numpy(dtype=float)
        y = s["mean"].to_numpy(dtype=float) if "mean" in s.columns else s["q50"].to_numpy(dtype=float)
        if "sem" in s.columns:
            err = 1.96 * s["sem"].to_numpy(dtype=float)
        else:
            err = np.full_like(y, np.nan)
        ax.errorbar(
            x,
            y,
            yerr=err,
            color=color,
            lw=1.2,
            marker="o",
            markersize=3.5,
            capsize=2.5,
            elinewidth=1.0,
            label=_inc_label(inc, inc_levels=inc_levels) if show_legend else None,
        )
        ys.extend(y[np.isfinite(y)].tolist())
        lo = y - err
        hi = y + err
        ys.extend(lo[np.isfinite(lo)].tolist())
        ys.extend(hi[np.isfinite(hi)].tolist())
    if variable == "M":
        ax.axhline(1.0, color="0.75", lw=0.6, ls=":")
    ax.set_xticks(list(COH3_TICKS))
    ax.set_xticklabels([COH3_LABELS[t] for t in COH3_TICKS])
    if condition_label:
        _panel_condition_label(ax, condition_label)
    _style_panel(ax, square=True)
    return ys


# ---- type-2 criteria (avg S1 / S2) ----------------------------------------


def _type2_incentive_table(summary: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Long table of type-2 criterion spacings by incentive.

    Bayesian hmetad uses treatment contrasts vs the first incentive factor level:
      spacing(ref) = Intercept
      spacing(level_k) = Intercept + incentive{level_k}
    For standard −1/0/+1 coding, non-ref levels are named incentive0 / incentive1.
    """
    df = summary.copy()
    if "choiceType" not in df.columns:
        df["choiceType"] = "Free"
    rows: List[dict] = []
    for (pid, ctype), g in df.groupby(["participant", "choiceType"], sort=False):
        by_param = {
            str(r.param): float(r.mean)
            for r in g.itertuples()
            if np.isfinite(r.mean)
        }
        parsed: Dict[Tuple[str, int], Dict[str, float]] = {}
        for param, val in by_param.items():
            m = _METAC2_PARAM.match(param)
            if not m:
                continue
            side, k_s, term = m.group(1), int(m.group(2)), m.group(3)
            parsed.setdefault((side, k_s), {})[term] = val
        for (side, k), terms in parsed.items():
            if "Intercept" not in terms:
                continue
            base = terms["Intercept"]
            # Prefer explicit −1/0/+1 reconstruction; else Intercept-only (ref level unknown)
            has_std = "incentive0" in terms or "incentive1" in terms
            if has_std:
                levels = {
                    -1.0: base,
                    0.0: base + terms.get("incentive0", np.nan),
                    1.0: base + terms.get("incentive1", np.nan),
                }
            else:
                levels = {-1.0: base}
            for inc, spacing in levels.items():
                if not np.isfinite(spacing):
                    continue
                rows.append(
                    {
                        "participant": str(pid),
                        "choiceType": str(ctype),
                        "side": side,
                        "rank": int(k),
                        "incentive": float(inc),
                        "spacing": float(spacing),
                    }
                )
    return pd.DataFrame(rows) if rows else None


def _type2_avg_sides(long: pd.DataFrame) -> pd.DataFrame:
    """Average S1 (zero) and S2 (one) spacings within participant × rank × incentive."""
    return (
        long.groupby(["participant", "choiceType", "rank", "incentive"], as_index=False)["spacing"]
        .mean()
    )


def _draw_type2_panel(
    ax: plt.Axes,
    long_avg: Optional[pd.DataFrame],
    *,
    show_legend: bool = False,
    condition_label: Optional[str] = None,
) -> List[float]:
    if long_avg is None or long_avg.empty:
        _blank(ax, clear_ticks=False)
        if condition_label:
            _panel_condition_label(ax, condition_label)
        ax.set_box_aspect(1)
        return []
    ranks = sorted(int(r) for r in long_avg["rank"].unique())
    inc_levels = sorted({float(x) for x in long_avg["incentive"].unique()})
    ys: List[float] = []
    for inc in inc_levels:
        s = (
            long_avg[np.isclose(long_avg["incentive"], float(inc))]
            .groupby("rank")["spacing"]
            .agg(["mean", "sem"])
            .reindex(ranks)
        )
        if s["mean"].isna().all():
            continue
        y = s["mean"].to_numpy(dtype=float)
        sem = s["sem"].to_numpy(dtype=float)
        x = np.asarray(ranks, dtype=float)
        color = _inc_color(inc, inc_levels=inc_levels)
        lo = y - sem
        hi = y + sem
        ax.fill_between(x, lo, hi, color=color, alpha=0.18, lw=0)
        ax.plot(
            x,
            y,
            color=color,
            lw=1.2,
            marker="o",
            markersize=3.5,
            label=_inc_label(inc, inc_levels=inc_levels) if show_legend else None,
        )
        ys.extend(y[np.isfinite(y)].tolist())
        ys.extend(lo[np.isfinite(lo)].tolist())
        ys.extend(hi[np.isfinite(hi)].tolist())
    ax.set_xticks(ranks)
    if condition_label:
        _panel_condition_label(ax, condition_label)
    _style_panel(ax, square=True)
    return ys


# ---- incentive-effect violins ---------------------------------------------


def extract_incentive_effects_indiv(effects: pd.DataFrame) -> Dict[str, np.ndarray]:
    out: Dict[str, np.ndarray] = {}
    for key, _, _ in EFFECT_SPECS:
        if key in effects.columns:
            v = effects[key].to_numpy(dtype=float)
            v = v[np.isfinite(v)]
            if v.size:
                out[key] = v
    return out


def _is_mu_incentive_main(col: str) -> bool:
    s = str(col)
    return (
        s.startswith("b_incentive")
        and ":" not in s
        and not s.startswith("b_metac2")
        and not s.startswith("b_dprime_")
    )


def _is_mu_incentive_coh3(col: str) -> bool:
    s = str(col)
    return s.startswith("b_incentive") and ":coh3" in s and not s.startswith("b_metac2")


def _is_type2_incentive(col: str) -> bool:
    s = str(col)
    return s.startswith("b_metac2") and "incentive" in s and ":coh3" not in s


def extract_incentive_effects_legacy_draws(wide: pd.DataFrame) -> Dict[str, np.ndarray]:
    out: Dict[str, np.ndarray] = {}
    mu_inc = [c for c in wide.columns if _is_mu_incentive_main(c)]
    mu_ix = [c for c in wide.columns if _is_mu_incentive_coh3(c)]
    t2 = [c for c in wide.columns if _is_type2_incentive(c)]
    if mu_inc:
        out["mu_incentive"] = wide[mu_inc].to_numpy(dtype=float).mean(axis=1)
    if mu_ix:
        out["mu_incentive_coh3"] = wide[mu_ix].to_numpy(dtype=float).mean(axis=1)
    if t2:
        out["type2_incentive"] = wide[t2].to_numpy(dtype=float).mean(axis=1)
    return out


def load_draws_wide(repo: Path, dataset: str) -> pd.DataFrame:
    path = dataset_dir(repo, dataset) / "draws_population.csv"
    if not path.is_file():
        raise FileNotFoundError(path)
    long = pd.read_csv(path)
    if long.empty:
        raise FileNotFoundError(f"{path} is empty")
    long = long[long["variable"].astype(str).str.startswith("b_")].copy()
    wide = long.pivot_table(
        index=".draw", columns="variable", values="value", aggfunc="first"
    )
    return wide.reset_index(drop=True)


def effects_for_dataset(
    repo: Path,
    dataset: str,
    *,
    choice_type: str = "Free",
) -> Dict[str, np.ndarray]:
    se = _filter_choice_type(load_subject_effects(repo, dataset), choice_type)
    if se is not None:
        return extract_incentive_effects_indiv(se)
    if choice_type != "Free":
        return {}
    try:
        wide = load_draws_wide(repo, dataset)
        return extract_incentive_effects_legacy_draws(wide)
    except FileNotFoundError:
        return {}


def _draw_effect_violin(
    ax: plt.Axes,
    vals: np.ndarray,
    x: float,
    color: Tuple[float, float, float],
    *,
    width: float = 0.35,
) -> None:
    vals = np.asarray(vals, dtype=float)
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return
    kde_violin(ax, vals, x, color, width=width, alpha=0.35)
    jitter = 0.12 * (RNG.random(vals.size) - 0.5)
    ax.plot(
        x + jitter,
        vals,
        "o",
        markerfacecolor=color,
        markeredgecolor="white",
        markersize=4.5,
        linestyle="None",
        zorder=3,
        alpha=0.85,
    )
    mu = float(np.mean(vals))
    se = float(np.std(vals, ddof=1) / np.sqrt(vals.size)) if vals.size > 1 else 0.0
    ax.errorbar(x, mu, yerr=se, fmt="none", ecolor="k", linewidth=2.5, capsize=5, zorder=4)


def _draw_effects_panel(
    ax: plt.Axes,
    effects: Dict[str, np.ndarray],
    *,
    show_xlabel: bool,
    condition_label: Optional[str] = None,
) -> Tuple[List[float], List[Tuple[float, float, str]]]:
    xs = np.arange(1, len(EFFECT_SPECS) + 1, dtype=float)
    ys: List[float] = []
    annotations: List[Tuple[float, float, str]] = []
    any_data = bool(effects) and any(
        np.asarray(effects.get(k, []), dtype=float).size > 0 for k, _, _ in EFFECT_SPECS
    )
    if not any_data:
        _blank(ax, clear_ticks=False)
    else:
        for i, (key, _label, color) in enumerate(EFFECT_SPECS):
            vals = np.asarray(effects.get(key, np.array([])), dtype=float)
            vals = vals[np.isfinite(vals)]
            x = float(xs[i])
            _draw_effect_violin(ax, vals, x, color)
            ys.extend(vals.tolist())
            if vals.size > 1:
                res = ttest_1samp(vals, popmean=0.0)
                stars = _p_to_stars(float(res.pvalue))
                if stars:
                    annotations.append((x, float(np.max(vals)), stars))
        ax.axhline(0.0, color="k", linestyle="--", linewidth=1, alpha=0.55, zorder=1)
    ax.set_xlim(0.5, len(EFFECT_SPECS) + 0.5)
    ax.set_xticks(xs)
    ax.set_xticklabels([s[1] for s in EFFECT_SPECS] if show_xlabel else [""] * len(EFFECT_SPECS))
    if condition_label:
        _panel_condition_label(ax, condition_label)
    _style_panel(ax)
    return ys, annotations


def _place_effect_stars(
    ax: plt.Axes,
    annotations: List[Tuple[float, float, str]],
    ylim: Tuple[float, float],
) -> None:
    lo, hi = ylim
    span = hi - lo if hi > lo else 1.0
    for x, local_max, stars in annotations:
        y = min(hi - 0.02 * span, local_max + 0.04 * span)
        ax.text(
            x,
            y,
            stars,
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
            clip_on=False,
            zorder=5,
        )


# ---- grid builders --------------------------------------------------------


def _panel_choice_type(
    dataset: str,
    row_i: int,
    rows: Sequence[str],
    *,
    agency_rows: bool,
) -> str:
    if agency_rows:
        ctype = _condition_for_panel(dataset, row_i, agency_rows=True)
        return ctype or rows[row_i]
    return str(rows[row_i])


def plot_hmeta_curve_grid(
    repo: Path,
    columns: Sequence[Tuple[str, str]],
    *,
    variable: str,
    ylabel: str,
    stem: str,
    agency_rows: bool = False,
    out: Optional[Path] = None,
    dpi: int = 150,
) -> Path:
    """Condition × dataset grid for meta-d′ or M-ratio vs coh3."""
    _setup_rc()
    cols = available_datasets(repo, columns)
    if not cols:
        raise FileNotFoundError(
            f"No usable hmeta_d outputs under {hmeta_root(repo)} for {[c for c, _ in columns]}"
        )
    rows = _grid_row_specs(repo, cols, agency_rows=agency_rows)
    n_r, n_c = len(rows), len(cols)
    fig, axes = plt.subplots(
        n_r,
        n_c,
        figsize=(PANEL_W * n_c, PANEL_H * n_r),
        squeeze=False,
        sharex="col",
        sharey=True,
    )
    all_ys: List[float] = []
    legend_handles = []
    legend_labels = []
    seen_labels: set[str] = set()

    for j, (key, _) in enumerate(cols):
        try:
            prep = load_preparation(repo, key)
        except FileNotFoundError:
            prep = None
        cell_all = load_cell_summary(repo, key)
        for i in range(n_r):
            ax = axes[i, j]
            ctype = _panel_choice_type(key, i, rows, agency_rows=agency_rows)
            cell = _filter_choice_type(cell_all, ctype)
            ys = _draw_curve_panel(
                ax,
                cell,
                variable=variable,
                prep=prep,
                show_legend=(i == 0),
                condition_label=ctype,
            )
            all_ys.extend(ys)
            if i == 0:
                for h, lab in zip(*ax.get_legend_handles_labels()):
                    if lab and lab not in seen_labels:
                        seen_labels.add(lab)
                        legend_handles.append(h)
                        legend_labels.append(lab)

    for j, (_, title) in enumerate(cols):
        axes[0, j].set_title(title)
    for i in range(n_r):
        axes[i, 0].set_ylabel(ylabel)
    for j in range(n_c):
        axes[-1, j].set_xlabel("coherence")

    _finalize_shared_ylim(axes, all_ys)
    if legend_handles:
        axes[0, -1].legend(
            legend_handles,
            legend_labels,
            loc="best",
            fontsize=FONT_SIZE - 2,
            frameon=False,
            handlelength=1.2,
        )
    fig.tight_layout()
    if out is None:
        out = fig_dir(repo) / f"{stem}.png"
    return save_fig(fig, out, dpi=dpi)


def plot_hmeta_type2_grid(
    repo: Path,
    columns: Sequence[Tuple[str, str]],
    *,
    stem: str,
    agency_rows: bool = False,
    out: Optional[Path] = None,
    dpi: int = 150,
) -> Path:
    """Condition × dataset grid: type-2 spacings vs rank (S1/S2 averaged)."""
    _setup_rc()
    cols = available_datasets(repo, columns)
    if not cols:
        raise FileNotFoundError(
            f"No usable hmeta_d outputs under {hmeta_root(repo)} for {[c for c, _ in columns]}"
        )
    rows = _grid_row_specs(repo, cols, agency_rows=agency_rows)
    n_r, n_c = len(rows), len(cols)
    fig, axes = plt.subplots(
        n_r,
        n_c,
        figsize=(PANEL_W * n_c, PANEL_H * n_r),
        squeeze=False,
        sharex="col",
        sharey=True,
    )
    all_ys: List[float] = []
    legend_handles = None
    legend_labels = None

    for j, (key, _) in enumerate(cols):
        summary = load_subject_summary(repo, key)
        long = _type2_incentive_table(summary) if summary is not None else None
        long_avg = _type2_avg_sides(long) if long is not None else None
        for i in range(n_r):
            ax = axes[i, j]
            ctype = _panel_choice_type(key, i, rows, agency_rows=agency_rows)
            if long_avg is None:
                sub = None
            else:
                sub = long_avg[long_avg["choiceType"].astype(str) == str(ctype)]
                if sub.empty:
                    sub = None
            ys = _draw_type2_panel(
                ax, sub, show_legend=(i == 0 and j == 0), condition_label=ctype
            )
            all_ys.extend(ys)
            if i == 0 and j == 0:
                h, lab = ax.get_legend_handles_labels()
                if h:
                    legend_handles, legend_labels = h, lab

    for j, (_, title) in enumerate(cols):
        axes[0, j].set_title(title)
    for i in range(n_r):
        axes[i, 0].set_ylabel("type-2 spacing")
    for j in range(n_c):
        axes[-1, j].set_xlabel("criterion rank")

    _finalize_shared_ylim(axes, all_ys)
    if legend_handles:
        axes[0, -1].legend(
            legend_handles,
            legend_labels,
            loc="best",
            fontsize=FONT_SIZE - 2,
            frameon=False,
            handlelength=1.2,
        )
    fig.tight_layout()
    if out is None:
        out = fig_dir(repo) / f"{stem}.png"
    return save_fig(fig, out, dpi=dpi)


def plot_hmeta_effects_grid(
    repo: Path,
    columns: Sequence[Tuple[str, str]],
    *,
    stem: str,
    agency_rows: bool = False,
    out: Optional[Path] = None,
    dpi: int = 150,
) -> Path:
    """Condition × dataset grid: 3 incentive-effect violins per panel."""
    _setup_rc()
    cols = available_datasets(repo, columns)
    if not cols:
        raise FileNotFoundError(
            f"No usable hmeta_d outputs under {hmeta_root(repo)} for {[c for c, _ in columns]}"
        )
    rows = _grid_row_specs(repo, cols, agency_rows=agency_rows)
    n_r, n_c = len(rows), len(cols)
    fig, axes = plt.subplots(
        n_r,
        n_c,
        figsize=(EFFECTS_PANEL_W * n_c, EFFECTS_PANEL_H * n_r),
        squeeze=False,
        sharey=True,
    )
    all_ys: List[float] = []
    star_map: Dict[Tuple[int, int], List[Tuple[float, float, str]]] = {}

    for j, (key, _) in enumerate(cols):
        for i in range(n_r):
            ax = axes[i, j]
            ctype = _panel_choice_type(key, i, rows, agency_rows=agency_rows)
            effects = effects_for_dataset(repo, key, choice_type=ctype)
            ys, ann = _draw_effects_panel(
                ax, effects, show_xlabel=(i == n_r - 1), condition_label=ctype
            )
            all_ys.extend(ys)
            if ann:
                star_map[(i, j)] = ann

    for j, (_, title) in enumerate(cols):
        axes[0, j].set_title(title)
    for i in range(n_r):
        axes[i, 0].set_ylabel("incentive effect")

    _finalize_shared_ylim(axes, all_ys, pad_frac=0.10, headroom=0.12)
    for (i, j), ann in star_map.items():
        ylim = axes[i, j].get_ylim()
        _place_effect_stars(axes[i, j], ann, (float(ylim[0]), float(ylim[1])))
    fig.tight_layout()
    if out is None:
        out = fig_dir(repo) / f"{stem}.png"
    return save_fig(fig, out, dpi=dpi)


def _layout_stem(kind: str, columns: Sequence[Tuple[str, str]]) -> str:
    layout = (
        "by_experiment"
        if list(columns) == list(BY_EXP)
        else "data_vs_models"
    )
    return f"fig_hmeta_{kind}_{layout}"


def plot_hmeta_layout(repo: Path, columns: Sequence[Tuple[str, str]], *, dpi: int = 150) -> List[Path]:
    """Write the four condition×dataset figures for one column layout."""
    cols = available_datasets(repo, columns)
    if not cols:
        warnings.warn(
            f"hmeta_d: no usable datasets for layout {[c for c, _ in columns]}; skipping"
        )
        return []
    agency_rows = list(columns) == list(BY_EXP)
    outs: List[Path] = []
    outs.append(
        plot_hmeta_curve_grid(
            repo,
            cols,
            variable="meta_d",
            ylabel=r"meta-$d'$",
            stem=_layout_stem("metad", columns),
            agency_rows=agency_rows,
            dpi=dpi,
        )
    )
    outs.append(
        plot_hmeta_curve_grid(
            repo,
            cols,
            variable="M",
            ylabel=r"$M$-ratio",
            stem=_layout_stem("mratio", columns),
            agency_rows=agency_rows,
            dpi=dpi,
        )
    )
    outs.append(
        plot_hmeta_type2_grid(
            repo,
            cols,
            stem=_layout_stem("type2", columns),
            agency_rows=agency_rows,
            dpi=dpi,
        )
    )
    outs.append(
        plot_hmeta_effects_grid(
            repo,
            cols,
            stem=_layout_stem("effects", columns),
            agency_rows=agency_rows,
            dpi=dpi,
        )
    )
    return outs


def plot_hmeta_by_experiment(repo: Path, *, dpi: int = 150) -> List[Path]:
    return plot_hmeta_layout(repo, BY_EXP, dpi=dpi)


def plot_hmeta_data_vs_models(repo: Path, *, dpi: int = 150) -> List[Path]:
    return plot_hmeta_layout(repo, DATA_VS_MODELS, dpi=dpi)


def plot_hmeta_figures(repo: Path, *, dpi: int = 150) -> List[Path]:
    outs: List[Path] = []
    outs.extend(plot_hmeta_by_experiment(repo, dpi=dpi))
    outs.extend(plot_hmeta_data_vs_models(repo, dpi=dpi))
    return outs


# Back-compat aliases used by older notebooks / CLIs
def plot_hmeta_effects(repo: Path, columns: Sequence[Tuple[str, str]], **kwargs) -> Path:
    return plot_hmeta_effects_grid(
        repo, columns, stem=_layout_stem("effects", columns), **kwargs
    )


def plot_hmeta_curves(repo: Path, columns: Sequence[Tuple[str, str]], **kwargs) -> Path:
    # Prefer meta-d′ when callers still request a single "curves" figure
    return plot_hmeta_curve_grid(
        repo,
        columns,
        variable="meta_d",
        ylabel=r"meta-$d'$",
        stem=_layout_stem("metad", columns),
        **{k: v for k, v in kwargs.items() if k in ("out", "dpi")},
    )


def plot_hmeta_type2_criteria(
    repo: Path,
    dataset: str = "exp1a",
    *,
    title: Optional[str] = None,
    out: Optional[Path] = None,
    dpi: int = 150,
) -> Path:
    """Deprecated single-dataset criteria figure → type-2 grid with one column."""
    cols = ((dataset, title or dataset),)
    return plot_hmeta_type2_grid(
        repo,
        cols,
        stem=f"fig_hmeta_type2_criteria_{dataset}",
        out=out,
        dpi=dpi,
    )


def main(argv: Optional[Sequence[str]] = None) -> None:
    ap = argparse.ArgumentParser(
        description="Plot hmetad meta-d′ results (condition × dataset grids)."
    )
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument(
        "--layout",
        choices=("by_experiment", "data_vs_models", "all"),
        default="all",
    )
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    if args.layout == "by_experiment":
        outs = plot_hmeta_by_experiment(repo, dpi=args.dpi)
    elif args.layout == "data_vs_models":
        outs = plot_hmeta_data_vs_models(repo, dpi=args.dpi)
    else:
        outs = plot_hmeta_figures(repo, dpi=args.dpi)
    for p in outs:
        print(p)


if __name__ == "__main__":
    main()
