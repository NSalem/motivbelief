"""
Confidence vs accuracy calibration figures.

Two paper-core layouts (mirroring X-pattern figures):
- by experiment: 2×4 data-only columns Exp 1a/1b/2/3
- data vs models: 2×4 merged data + act/intent/confirm sims

Each panel: coherence-cell means ± SEM (unconnected), overlaid with a smooth
curve and subject-bootstrap 95% CI bands.

Default smoother (``interp``): smooth interpolation (PCHIP) through coh-cell
grand means — passes through the plotted average points — with subject-bootstrap
95% CI. Alternatives: ``subject_interp``, ``llo``, ``subject_llo``, ``ksr``.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator

from motivbelief.modeling.io import COH_LEVELS, load_exp_df, load_merged_human_trials, load_sim_trials
from motivbelief.plotting.paths import fig_dir
from motivbelief.plotting.series_panel import Series, draw_lines, draw_points, style_belief_axis
from motivbelief.plotting.style import (
    CMAP_EXP1B,
    INC_LABELS,
    INC_LEVELS,
    INC_LINE_COLOR,
    save_fig,
)

# (exp, top-row group, bottom-row group, column title)
_BY_EXP: List[Tuple[str, str, str, str]] = [
    ("exp1a", "Free", "Observed", "Exp 1a"),
    ("exp1b", "Free", "Observed", "Exp 1b"),
    ("exp2", "Free", "Observed", "Exp 2"),
    ("exp3", "Replayed", "Forced", "Exp 3"),
]

DEFAULT_N_BOOT = 500
DEFAULT_N_GRID = 60
# Used only when smooth="ksr"
DEFAULT_BANDWIDTH = 0.08
DEFAULT_SMOOTH = "interp"  # "interp" | "subject_interp" | "llo" | "subject_llo" | "ksr"
# Min subjects with a finite curve value at a grid point to plot mean/CI.
MIN_CURVE_N = 5
# Probability clip for logits (acc in [0,1], conf on 0–100 scale → /100).
LOGIT_EPS = 1e-4
# Plot both accuracy and belief on 0–100 (%) with shared limits.
AXIS_LIM = (40.0, 100.0)
X_PROP_LIM = (AXIS_LIM[0] / 100.0, AXIS_LIM[1] / 100.0)
# Square panels in a 4×2 grid (extra height for legend / titles).
_PANEL = 2.0
FIGSIZE_2X4 = (4 * _PANEL, 2 * _PANEL + 0.85)  # (8.0, 4.85)
FONT_SIZE = 11.0
LEGEND_FONT_SIZE = 10.0
TITLE_FONT_SIZE = 11.0


def _setup_fonts() -> None:
    plt.rcParams.update(
        {
            "font.size": FONT_SIZE,
            "axes.labelsize": FONT_SIZE,
            "axes.titlesize": TITLE_FONT_SIZE,
            "xtick.labelsize": FONT_SIZE - 1,
            "ytick.labelsize": FONT_SIZE - 1,
            "legend.fontsize": LEGEND_FONT_SIZE,
        }
    )


def _new_calib_figure() -> Tuple[plt.Figure, np.ndarray]:
    """2×4 shared axes with tight row spacing for square panels.

    x is shared within each row and y within each column (all panels still
    get the same explicit limits via ``style_belief_axis``).
    """
    fig, axes = plt.subplots(
        2,
        4,
        figsize=FIGSIZE_2X4,
        sharex="row",
        sharey="col",
        layout="constrained",
    )
    engine = fig.get_layout_engine()
    if engine is not None:
        engine.set(h_pad=0.0, w_pad=0.02, hspace=-0.05, wspace=0.04)
    return fig, axes


def _sem(x: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    if len(x) < 2:
        return float("nan")
    return float(np.std(x, ddof=1) / np.sqrt(len(x)))


def _inc_style_maps(inc_levels: Sequence[float]) -> Tuple[Dict[float, str], Dict[float, str]]:
    """Line colors and legend labels for the incentive set in a panel."""
    levels = [float(x) for x in sorted(np.unique(np.asarray(inc_levels, dtype=float)))]
    if len(levels) == 3 and np.allclose(levels, [-1.0, 0.0, 1.0]):
        colors = {inc: INC_LINE_COLOR[inc] for inc in levels}
        labels = {inc: INC_LABELS[inc] for inc in levels}
        return colors, labels
    if len(levels) == 2:
        colors = {
            levels[0]: mcolors.to_hex(CMAP_EXP1B[0]),
            levels[1]: mcolors.to_hex(CMAP_EXP1B[1]),
        }
        labels = {inc: f"inc {inc:g}" for inc in levels}
        return colors, labels
    palette = [INC_LINE_COLOR[k] for k in INC_LEVELS]
    colors = {inc: palette[i % len(palette)] for i, inc in enumerate(levels)}
    labels = {inc: f"inc {inc:g}" for inc in levels}
    return colors, labels


def _subject_calib_cells(
    df: pd.DataFrame,
    *,
    allowed_incentives: Sequence[float] | None = INC_LEVELS,
) -> pd.DataFrame:
    """
    Per subject × coh × incentive: accuracy and mean confidence (pool correct/error).
    """
    d = df.copy()
    if "coh" not in d.columns:
        d["coh"] = np.abs(d["stim"].astype(float))
    else:
        d["coh"] = np.abs(d["coh"].astype(float))
    d["incentive"] = d["incentive"].astype(float)
    d["correct"] = d["correct"].astype(int)
    d = d[d["coh"].isin(COH_LEVELS)]
    if allowed_incentives is not None:
        d = d[d["incentive"].isin(list(allowed_incentives))]
    if d.empty:
        return pd.DataFrame()

    rows = []
    for (pid, coh, inc), g in d.groupby(["participant", "coh", "incentive"]):
        rows.append(
            {
                "participant": pid,
                "coh": float(coh),
                "incentive": float(inc),
                "acc": float(g["correct"].mean()),
                "conf": float(g["conf"].mean()),
            }
        )
    return pd.DataFrame(rows)


def _group_calib_agg(cells: pd.DataFrame) -> pd.DataFrame:
    """Grand mean ± SEM of (acc, conf) per coh × incentive."""
    if cells.empty:
        return pd.DataFrame()
    rows = []
    for (coh, inc), g in cells.groupby(["coh", "incentive"]):
        acc = g["acc"].to_numpy(dtype=float)
        conf = g["conf"].to_numpy(dtype=float)
        rows.append(
            {
                "coh": float(coh),
                "incentive": float(inc),
                "acc_mean": float(np.nanmean(acc)),
                "acc_sem": _sem(acc),
                "conf_mean": float(np.nanmean(conf)),
                "conf_sem": _sem(conf),
            }
        )
    return pd.DataFrame(rows)


def _calib_point_series(
    agg: pd.DataFrame,
    *,
    colors: Dict[float, str],
    labels: Dict[float, str],
) -> List[Series]:
    """Unconnected coh-cell means ± SEM (no lines). Accuracy in %."""
    points: List[Series] = []
    if agg.empty:
        return points
    for inc in sorted(colors.keys()):
        sub = agg[np.isclose(agg["incentive"].astype(float), float(inc))].copy()
        if sub.empty:
            continue
        sub = sub.sort_values("acc_mean")
        color = colors[float(inc)]
        points.append(
            Series(
                100.0 * sub["acc_mean"].to_numpy(dtype=float),
                sub["conf_mean"].to_numpy(dtype=float),
                xerr=100.0 * sub["acc_sem"].to_numpy(dtype=float),
                yerr=sub["conf_sem"].to_numpy(dtype=float),
                color=color,
                marker="o",
                markersize=4.5,
                zorder=5,
                label=labels[float(inc)],
            )
        )
    return points


def _silverman_bandwidth(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 2:
        return 0.08
    sd = float(np.std(x, ddof=1))
    iqr = float(np.subtract(*np.percentile(x, [75, 25])))
    scale = min(sd, iqr / 1.34) if iqr > 0 else sd
    if scale <= 0:
        return 0.08
    h = 1.06 * scale * n ** (-0.2)
    return float(np.clip(h, 0.03, 0.15))


def _ksr_nadaraya_watson(
    x: np.ndarray,
    y: np.ndarray,
    x_grid: np.ndarray,
    *,
    bandwidth: float,
) -> np.ndarray:
    """Gaussian-kernel smoother E[y|x] (Nadaraya–Watson)."""
    mask = np.isfinite(x) & np.isfinite(y)
    x = np.asarray(x[mask], dtype=np.float64)
    y = np.asarray(y[mask], dtype=np.float64)
    if len(x) == 0:
        return np.full(len(x_grid), np.nan)
    x_col = x[:, None]
    xg = np.asarray(x_grid, dtype=np.float64)[None, :]
    h = float(bandwidth)
    w = np.exp(-0.5 * ((x_col - xg) / h) ** 2)
    den = w.sum(axis=0)
    num = (w * y[:, None]).sum(axis=0)
    out = num / np.maximum(den, 1e-12)
    out[den < 1e-6 * len(x)] = np.nan
    return out


def _coh_knots(cells: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """Mean (acc, conf) per coherence, sorted by accuracy (unique x)."""
    if cells.empty:
        return np.array([]), np.array([])
    rows = []
    for _, g in cells.groupby("coh"):
        acc = g["acc"].to_numpy(dtype=float)
        conf = g["conf"].to_numpy(dtype=float)
        ok = np.isfinite(acc) & np.isfinite(conf)
        if not np.any(ok):
            continue
        rows.append((float(np.mean(acc[ok])), float(np.mean(conf[ok]))))
    if not rows:
        return np.array([]), np.array([])
    xs = np.asarray([r[0] for r in rows], dtype=float)
    ys = np.asarray([r[1] for r in rows], dtype=float)
    order = np.argsort(xs)
    xs, ys = xs[order], ys[order]
    # Collapse duplicate accuracies (rare) by averaging y.
    uniq_x: List[float] = []
    uniq_y: List[float] = []
    for x, y in zip(xs, ys):
        if uniq_x and np.isclose(x, uniq_x[-1]):
            uniq_y[-1] = 0.5 * (uniq_y[-1] + y)
        else:
            uniq_x.append(float(x))
            uniq_y.append(float(y))
    return np.asarray(uniq_x), np.asarray(uniq_y)


def _unique_sorted_knots(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Sort by x and average y at duplicate x."""
    mask = np.isfinite(x) & np.isfinite(y)
    x = np.asarray(x[mask], dtype=float)
    y = np.asarray(y[mask], dtype=float)
    if len(x) == 0:
        return x, y
    order = np.argsort(x)
    x, y = x[order], y[order]
    uniq_x: List[float] = []
    uniq_y: List[float] = []
    for xi, yi in zip(x, y):
        if uniq_x and np.isclose(xi, uniq_x[-1]):
            uniq_y[-1] = 0.5 * (uniq_y[-1] + yi)
        else:
            uniq_x.append(float(xi))
            uniq_y.append(float(yi))
    return np.asarray(uniq_x), np.asarray(uniq_y)


def _interp_through_knots(
    x_knot: np.ndarray,
    y_knot: np.ndarray,
    x_grid: np.ndarray,
    *,
    kind: str = "linear",
) -> np.ndarray:
    """
    Interpolate through knots onto ``x_grid`` (no extrapolation).

    ``kind="linear"`` or ``kind="pchip"`` (≥3 knots; else linear).
    """
    out = np.full(len(x_grid), np.nan)
    x_knot, y_knot = _unique_sorted_knots(x_knot, y_knot)
    if len(x_knot) < 2:
        return out
    inside = (x_grid >= x_knot[0]) & (x_grid <= x_knot[-1])
    if not np.any(inside):
        return out
    if kind == "pchip" and len(x_knot) >= 3:
        out[inside] = PchipInterpolator(x_knot, y_knot)(x_grid[inside])
    else:
        out[inside] = np.interp(x_grid[inside], x_knot, y_knot)
    return out


def _logit(p: np.ndarray, *, eps: float = LOGIT_EPS) -> np.ndarray:
    p = np.clip(np.asarray(p, dtype=float), eps, 1.0 - eps)
    return np.log(p) - np.log(1.0 - p)


def _inv_logit(z: np.ndarray) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    # stable sigmoid
    out = np.empty_like(z, dtype=float)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out


def _conf_to_p(conf: np.ndarray) -> np.ndarray:
    """Map confidence reports (0–100) to probabilities."""
    c = np.asarray(conf, dtype=float)
    return c / 100.0


def _p_to_conf(p: np.ndarray) -> np.ndarray:
    return 100.0 * np.asarray(p, dtype=float)


def _fit_llo(acc: np.ndarray, conf: np.ndarray) -> Tuple[float, float] | None:
    """
    OLS fit of logit(conf/100) = a + b * logit(acc).

    Returns ``(a, b)`` or None if fewer than 2 usable points.
    """
    acc = np.asarray(acc, dtype=float)
    conf = np.asarray(conf, dtype=float)
    ok = np.isfinite(acc) & np.isfinite(conf)
    acc, conf = acc[ok], conf[ok]
    if len(acc) < 2:
        return None
    x = _logit(acc)
    y = _logit(_conf_to_p(conf))
    # Need some spread in x for a slope
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        return None
    if np.allclose(x, x[0]):
        return None
    b, a = np.polyfit(x, y, 1)  # y ≈ b*x + a
    return float(a), float(b)


def _eval_llo(
    a: float,
    b: float,
    x_grid: np.ndarray,
    *,
    acc_min: float | None = None,
    acc_max: float | None = None,
) -> np.ndarray:
    """
    Evaluate LLO on ``x_grid``.

    By default evaluates on the full grid (parametric extrapolation). If
    ``acc_min``/``acc_max`` are set, values outside that range are NaN.
    """
    x_grid = np.asarray(x_grid, dtype=float)
    z = a + b * _logit(x_grid)
    out = _p_to_conf(_inv_logit(z))
    if acc_min is not None or acc_max is not None:
        lo = -np.inf if acc_min is None else float(acc_min)
        hi = np.inf if acc_max is None else float(acc_max)
        out = np.where((x_grid >= lo) & (x_grid <= hi), out, np.nan)
    return out


def _llo_on_cells(cells: pd.DataFrame, x_grid: np.ndarray) -> np.ndarray:
    """Fit one LLO to coh-cell grand means; evaluate on ``x_grid`` (caller sets span)."""
    xk, yk = _coh_knots(cells)
    fit = _fit_llo(xk, yk)
    if fit is None:
        return np.full(len(x_grid), np.nan)
    return _eval_llo(*fit, x_grid)


def _llo_group_bootstrap_ci(
    cells: pd.DataFrame,
    *,
    x_grid: np.ndarray,
    n_boot: int = DEFAULT_N_BOOT,
    seed: int = 0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Group-level LLO (fit to coh grand means) + subject-bootstrap 95% CI.

    Each bootstrap draw: resample subjects → recompute coh means → refit LLO.
    """
    nan = np.full(len(x_grid), np.nan)
    d = cells.dropna(subset=["acc", "conf", "participant", "coh"])
    if d.empty:
        return nan, nan, nan

    mean = _llo_on_cells(d, x_grid)
    pids = d["participant"].astype(str).unique()
    if len(pids) < 2 or n_boot < 1:
        return mean, mean.copy(), mean.copy()

    by_pid = {pid: g for pid, g in d.groupby(d["participant"].astype(str))}
    pid_list = list(by_pid.keys())
    rng = np.random.default_rng(seed)
    boots = np.full((n_boot, len(x_grid)), np.nan)
    for b in range(n_boot):
        draw = rng.choice(pid_list, size=len(pid_list), replace=True)
        boot_df = pd.concat([by_pid[p] for p in draw], ignore_index=True)
        boots[b] = _llo_on_cells(boot_df, x_grid)

    lo = np.full(len(x_grid), np.nan)
    hi = np.full(len(x_grid), np.nan)
    for j in range(len(x_grid)):
        finite = boots[:, j]
        finite = finite[np.isfinite(finite)]
        if len(finite) == 0:
            continue
        lo[j] = float(np.percentile(finite, 2.5))
        hi[j] = float(np.percentile(finite, 97.5))
    return mean, lo, hi


def _subject_llo_curves(cells: pd.DataFrame, x_grid: np.ndarray) -> np.ndarray:
    """One LLO curve per participant on the full shared ``x_grid``."""
    d = cells.dropna(subset=["acc", "conf", "participant"])
    if d.empty:
        return np.empty((0, len(x_grid)))
    curves = []
    for _, g in d.groupby(d["participant"].astype(str)):
        acc = g["acc"].to_numpy(dtype=float)
        conf = g["conf"].to_numpy(dtype=float)
        fit = _fit_llo(acc, conf)
        if fit is None:
            curves.append(np.full(len(x_grid), np.nan))
            continue
        a, b = fit
        curves.append(_eval_llo(a, b, x_grid))
    return np.vstack(curves) if curves else np.empty((0, len(x_grid)))


def _subject_interp_curves(cells: pd.DataFrame, x_grid: np.ndarray) -> np.ndarray:
    """
    One linear-interp curve per participant (rows × len(x_grid)).

    Knots are that participant's coh cells (acc, conf). NaN outside each
    subject's accuracy range or if fewer than 2 finite cells.
    """
    d = cells.dropna(subset=["acc", "conf", "participant"])
    if d.empty:
        return np.empty((0, len(x_grid)))
    curves = []
    for _, g in d.groupby(d["participant"].astype(str)):
        xk, yk = _unique_sorted_knots(
            g["acc"].to_numpy(dtype=float),
            g["conf"].to_numpy(dtype=float),
        )
        curves.append(_interp_through_knots(xk, yk, x_grid, kind="linear"))
    return np.vstack(curves) if curves else np.empty((0, len(x_grid)))


def subject_calib_curves(
    cells: pd.DataFrame,
    *,
    x_grid: np.ndarray | Sequence[float] | None = None,
    method: str = "llo",
) -> pd.DataFrame:
    """
    Per-participant confidence–accuracy curves (long format).

    Expects subject × coh × incentive cells with columns
    ``participant``, ``incentive``, ``acc``, ``conf``.

    ``method="llo"`` (default): ``logit(conf/100) = a + b * logit(acc)``.
    ``method="linear"``: linear interpolation through coh cells.

    Returns ``participant``, ``incentive``, ``acc``, ``conf`` on a shared
    accuracy grid (default: proportion range matching ``AXIS_LIM``). For ``llo``,
    curves are evaluated on the full grid (extrapolated from fitted ``a``, ``b``).
    For ``linear``, ``conf`` is NaN outside that subject's accuracy range.
    ``llo`` also returns ``a``, ``b`` (repeated on each grid row).
    """
    cols = ["participant", "incentive", "acc", "conf"]
    method = method.lower()
    if method == "llo":
        cols = cols + ["a", "b"]
    if cells.empty:
        return pd.DataFrame(columns=cols)

    grid = (
        np.linspace(X_PROP_LIM[0], X_PROP_LIM[1], DEFAULT_N_GRID)
        if x_grid is None
        else np.asarray(x_grid, dtype=float)
    )
    d = cells.dropna(subset=["acc", "conf", "participant", "incentive"]).copy()
    rows: List[dict] = []
    for (pid, inc), g in d.groupby([d["participant"].astype(str), "incentive"]):
        acc = g["acc"].to_numpy(dtype=float)
        conf_pts = g["conf"].to_numpy(dtype=float)
        if method == "llo":
            fit = _fit_llo(acc, conf_pts)
            if fit is None:
                conf = np.full(len(grid), np.nan)
                a_fit = b_fit = np.nan
            else:
                a_fit, b_fit = fit
                conf = _eval_llo(a_fit, b_fit, grid)
            for x, c in zip(grid, conf):
                rows.append(
                    {
                        "participant": pid,
                        "incentive": float(inc),
                        "acc": float(x),
                        "conf": float(c) if np.isfinite(c) else np.nan,
                        "a": float(a_fit) if np.isfinite(a_fit) else np.nan,
                        "b": float(b_fit) if np.isfinite(b_fit) else np.nan,
                    }
                )
        elif method == "linear":
            xk, yk = _unique_sorted_knots(acc, conf_pts)
            conf = _interp_through_knots(xk, yk, grid, kind="linear")
            for x, c in zip(grid, conf):
                rows.append(
                    {
                        "participant": pid,
                        "incentive": float(inc),
                        "acc": float(x),
                        "conf": float(c) if np.isfinite(c) else np.nan,
                    }
                )
        else:
            raise ValueError(f"Unknown method={method!r}; use 'llo' or 'linear'")
    return pd.DataFrame(rows)


def _mean_ci_from_subject_curves(
    curves: np.ndarray,
    *,
    n_boot: int,
    seed: int,
    min_n: int = MIN_CURVE_N,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Mean of subject curves + subject-bootstrap 95% CI of that mean."""
    n_grid = curves.shape[1] if curves.ndim == 2 else len(curves)
    nan = np.full(n_grid, np.nan)
    if curves.size == 0 or curves.shape[0] == 0:
        return nan, nan, nan

    n_subj = curves.shape[0]
    counts = np.sum(np.isfinite(curves), axis=0)
    mean = np.full(n_grid, np.nan)
    ok = counts >= min_n
    if np.any(ok):
        with np.errstate(all="ignore"):
            mean[ok] = np.nanmean(curves[:, ok], axis=0)

    if n_subj < 2 or n_boot < 1:
        return mean, mean.copy(), mean.copy()

    rng = np.random.default_rng(seed)
    boots = np.full((n_boot, n_grid), np.nan)
    for b in range(n_boot):
        idx = rng.integers(0, n_subj, size=n_subj)
        sample = curves[idx]
        c = np.sum(np.isfinite(sample), axis=0)
        m = np.full(n_grid, np.nan)
        use = c >= min_n
        if np.any(use):
            with np.errstate(all="ignore"):
                m[use] = np.nanmean(sample[:, use], axis=0)
        boots[b] = m

    lo = np.full(n_grid, np.nan)
    hi = np.full(n_grid, np.nan)
    for j in range(n_grid):
        if not ok[j]:
            continue
        finite = boots[:, j]
        finite = finite[np.isfinite(finite)]
        if len(finite) == 0:
            continue
        lo[j] = float(np.percentile(finite, 2.5))
        hi[j] = float(np.percentile(finite, 97.5))
    return mean, lo, hi


def _smooth_bootstrap_ci(
    cells: pd.DataFrame,
    *,
    x_grid: np.ndarray,
    smooth: str = DEFAULT_SMOOTH,
    bandwidth: float | None = DEFAULT_BANDWIDTH,
    n_boot: int = DEFAULT_N_BOOT,
    seed: int = 0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Subject-bootstrap 95% CI for a smooth conf|acc curve.

    ``llo``: LLO fit to coh grand means + subject bootstrap (default).
    ``subject_llo``: per-subject LLO → mean across subjects.
    ``subject_interp``: per-subject linear interp → mean.
    ``interp``: PCHIP through coh-cell grand means.
    ``ksr``: pooled Nadaraya–Watson on subject cells.
    """
    nan = np.full(len(x_grid), np.nan)
    if cells.empty:
        return nan, nan, nan

    d = cells.dropna(subset=["acc", "conf", "participant", "coh"]).copy()
    if d.empty:
        return nan, nan, nan

    smooth = smooth.lower()
    if smooth == "llo":
        return _llo_group_bootstrap_ci(d, x_grid=x_grid, n_boot=n_boot, seed=seed)
    if smooth in ("subject_llo", "llo_subject"):
        curves = _subject_llo_curves(d, x_grid)
        return _mean_ci_from_subject_curves(curves, n_boot=n_boot, seed=seed)
    if smooth == "subject_interp":
        curves = _subject_interp_curves(d, x_grid)
        return _mean_ci_from_subject_curves(curves, n_boot=n_boot, seed=seed)

    if smooth == "interp":
        xk, yk = _coh_knots(d)
        mean = _interp_through_knots(xk, yk, x_grid, kind="pchip")
    elif smooth == "ksr":
        x_all = d["acc"].to_numpy(dtype=float)
        y_all = d["conf"].to_numpy(dtype=float)
        h = _silverman_bandwidth(x_all) if bandwidth is None else float(bandwidth)
        mean = _ksr_nadaraya_watson(x_all, y_all, x_grid, bandwidth=h)
    else:
        raise ValueError(
            f"Unknown smooth={smooth!r}; use 'llo', 'subject_llo', "
            f"'subject_interp', 'interp', or 'ksr'"
        )

    pids = d["participant"].astype(str).unique()
    if len(pids) < 2 or n_boot < 1:
        return mean, mean.copy(), mean.copy()

    by_pid = {pid: g for pid, g in d.groupby(d["participant"].astype(str))}
    pid_list = list(by_pid.keys())
    rng = np.random.default_rng(seed)
    boots = np.full((n_boot, len(x_grid)), np.nan)
    for b in range(n_boot):
        draw = rng.choice(pid_list, size=len(pid_list), replace=True)
        boot_df = pd.concat([by_pid[p] for p in draw], ignore_index=True)
        if smooth == "interp":
            xk, yk = _coh_knots(boot_df)
            boots[b] = _interp_through_knots(xk, yk, x_grid, kind="pchip")
        else:
            h = (
                _silverman_bandwidth(boot_df["acc"].to_numpy())
                if bandwidth is None
                else float(bandwidth)
            )
            boots[b] = _ksr_nadaraya_watson(
                boot_df["acc"].to_numpy(dtype=float),
                boot_df["conf"].to_numpy(dtype=float),
                x_grid,
                bandwidth=h,
            )

    lo = np.full(len(x_grid), np.nan)
    hi = np.full(len(x_grid), np.nan)
    for j in range(len(x_grid)):
        col = boots[:, j]
        finite = col[np.isfinite(col)]
        if len(finite) == 0:
            continue
        lo[j] = float(np.percentile(finite, 2.5))
        hi[j] = float(np.percentile(finite, 97.5))
    return mean, lo, hi


def _draw_calib_panel(
    ax: plt.Axes,
    cells: pd.DataFrame,
    *,
    title: Optional[str],
    n_boot: int = DEFAULT_N_BOOT,
    seed: int = 0,
    smooth: str = DEFAULT_SMOOTH,
    bandwidth: float | None = DEFAULT_BANDWIDTH,
    draw_smooth: bool = True,
    connect_lines: bool = False,
    show_xlabel: bool = True,
    show_ylabel: bool = True,
    condition_label: Optional[str] = None,
) -> None:
    ax.plot(
        [AXIS_LIM[0], AXIS_LIM[1]],
        [AXIS_LIM[0], AXIS_LIM[1]],
        "--",
        color="0.85",
        lw=1,
        zorder=0,
    )

    if cells.empty:
        ax.set_xlim(*AXIS_LIM)
        ax.set_ylim(*AXIS_LIM)
        style_belief_axis(
            ax,
            ylim=AXIS_LIM,
            ylabel="belief" if show_ylabel else "",
            title=title,
            xlim=AXIS_LIM,
        )
        if show_xlabel:
            ax.set_xlabel("accuracy")
        else:
            ax.set_xlabel("")
        if condition_label:
            ax.text(
                0.05,
                0.95,
                condition_label,
                transform=ax.transAxes,
                va="top",
                ha="left",
                fontsize=FONT_SIZE,
            )
        ax.set_box_aspect(1)
        return

    colors, labels = _inc_style_maps(cells["incentive"].astype(float).unique())
    agg = _group_calib_agg(cells)
    x_grid = np.linspace(X_PROP_LIM[0], X_PROP_LIM[1], DEFAULT_N_GRID)

    if draw_smooth:
        for i, inc in enumerate(sorted(colors.keys())):
            sub = cells[np.isclose(cells["incentive"].astype(float), float(inc))]
            if sub.empty:
                continue
            # Draw smoothers on [first, last] coh-knot accuracy so curves end
            # near the high-coherence point.
            if smooth.lower() in (
                "interp",
                "llo",
                "subject_interp",
                "subject_llo",
                "llo_subject",
            ):
                xk, _yk = _coh_knots(sub)
                if len(xk) < 2:
                    continue
                x_curve = np.linspace(float(xk.min()), float(xk.max()), DEFAULT_N_GRID)
            else:
                x_curve = x_grid
            mean, lo, hi = _smooth_bootstrap_ci(
                sub,
                x_grid=x_curve,
                smooth=smooth,
                bandwidth=bandwidth,
                n_boot=n_boot,
                seed=seed + 17 * (i + 1),
            )
            color = colors[float(inc)]
            ok = np.isfinite(mean) & np.isfinite(lo) & np.isfinite(hi)
            if np.any(ok):
                x_pct = 100.0 * x_curve[ok]
                ax.fill_between(
                    x_pct,
                    lo[ok],
                    hi[ok],
                    color=color,
                    alpha=0.20,
                    linewidth=0,
                    zorder=2,
                )
                ax.plot(
                    x_pct,
                    mean[ok],
                    color=color,
                    linestyle="-",
                    linewidth=1.8,
                    zorder=3,
                )

    points = _calib_point_series(agg, colors=colors, labels=labels)
    if connect_lines:
        # No smoother makes sense here (e.g. accuracy barely varies) — just
        # connect the coh-cell group means with straight lines.
        draw_lines(ax, points, band=False)
    draw_points(ax, points)

    ax.set_xlim(*AXIS_LIM)
    ax.set_ylim(*AXIS_LIM)
    style_belief_axis(
        ax,
        ylim=AXIS_LIM,
        ylabel="belief" if show_ylabel else "",
        title=title,
        xlim=AXIS_LIM,
    )
    if show_xlabel:
        ax.set_xlabel("accuracy")
    else:
        ax.set_xlabel("")
    if condition_label:
        ax.text(
            0.05,
            0.95,
            condition_label,
            transform=ax.transAxes,
            va="top",
            ha="left",
            fontsize=FONT_SIZE,
        )
    ax.set_box_aspect(1)


def _cells_for_stem_group(repo: Path, kind: str, stem: str, group: str) -> pd.DataFrame:
    if kind == "data":
        trials = load_merged_human_trials(repo)
    else:
        trials = load_sim_trials(repo, stem)
    trials = trials[trials["choiceType"].astype(str) == group]
    return _subject_calib_cells(trials, allowed_incentives=INC_LEVELS)


def _cells_for_exp_group(repo: Path, exp: str, group: str) -> pd.DataFrame:
    trials = load_exp_df(exp, data_dir=str(repo / "data"))
    trials = trials[trials["choiceType"].astype(str) == group]
    return _subject_calib_cells(trials, allowed_incentives=None)


def _legend_handles_standard() -> List[plt.Line2D]:
    return [
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color=INC_LINE_COLOR[inc],
            linestyle="-",
            label=INC_LABELS[inc],
        )
        for inc in INC_LEVELS
    ]


def plot_calib_by_experiment(
    repo_root: Path,
    out: Optional[Path] = None,
    dpi: int = 150,
    *,
    n_boot: int = DEFAULT_N_BOOT,
    smooth: str = DEFAULT_SMOOTH,
    bandwidth: float | None = DEFAULT_BANDWIDTH,
) -> Path:
    """
    2×4 calibration (data only): columns Exp 1a/1b/2/3;
    rows Observed-like / Free-like (Exp 3: Forced / Replayed).
    """
    _setup_fonts()
    repo_root = repo_root.resolve()
    fig, axes = _new_calib_figure()

    for col, (exp, g_top, g_bot, title) in enumerate(_BY_EXP):
        for row, group in enumerate((g_top, g_bot)):
            cells = _cells_for_exp_group(repo_root, exp, group)
            # Exp 1b Observed: accuracy barely varies → skip smooth overlays,
            # just connect the coh-cell group means with straight lines.
            is_exp1b_observed = exp == "exp1b" and group == "Observed"
            _draw_calib_panel(
                axes[row, col],
                cells,
                title=title if row == 0 else None,
                n_boot=n_boot,
                seed=1000 * col + 10 * row,
                smooth=smooth,
                bandwidth=bandwidth,
                draw_smooth=not is_exp1b_observed,
                connect_lines=is_exp1b_observed,
                show_xlabel=(row == 1),
                show_ylabel=(col == 0),
                condition_label=group,
            )

    for ax in axes.flat:
        ax.label_outer()

    fig.legend(
        handles=_legend_handles_standard(),
        loc="upper center",
        ncol=3,
        fontsize=LEGEND_FONT_SIZE,
        frameon=False,
    )

    out = out or (fig_dir(repo_root) / "plots_calib_by_experiment.png")
    return save_fig(fig, out, dpi=dpi)


def plot_calib_data_vs_models(
    repo_root: Path,
    out: Optional[Path] = None,
    dpi: int = 150,
    *,
    n_boot: int = DEFAULT_N_BOOT,
    smooth: str = DEFAULT_SMOOTH,
    bandwidth: float | None = DEFAULT_BANDWIDTH,
) -> Path:
    """
    2×4 calibration: rows Free / Non-Free;
    cols Data (1a+2free+3) / sim_act / sim_intent / sim_confirm.
    """
    _setup_fonts()
    repo_root = repo_root.resolve()
    fig, axes = _new_calib_figure()
    col_specs: List[Tuple[str, str, str]] = [
        ("data", "exp1a_exp2free_exp3", "Data (1a+2free+3)"),
        ("sim", "sim_act", "Sim act"),
        ("sim", "sim_intent", "Sim intent"),
        ("sim", "sim_confirm", "Sim confirm"),
    ]
    row_groups = ("Free", "Non-Free")

    for col, (kind, stem, title) in enumerate(col_specs):
        for row, group in enumerate(row_groups):
            cells = _cells_for_stem_group(repo_root, kind, stem, group)
            _draw_calib_panel(
                axes[row, col],
                cells,
                title=title if row == 0 else None,
                n_boot=n_boot,
                seed=2000 + 100 * col + 10 * row,
                smooth=smooth,
                bandwidth=bandwidth,
                show_xlabel=(row == 1),
                show_ylabel=(col == 0),
                condition_label=group,
            )

    for ax in axes.flat:
        ax.label_outer()

    fig.legend(
        handles=_legend_handles_standard(),
        loc="upper center",
        ncol=3,
        fontsize=LEGEND_FONT_SIZE,
        frameon=False,
    )

    out = out or (fig_dir(repo_root) / "plots_calib_data_vs_models.png")
    return save_fig(fig, out, dpi=dpi)


def main() -> None:
    ap = argparse.ArgumentParser(description="Confidence vs accuracy calibration figures.")
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--out-exp", type=Path, default=None)
    ap.add_argument("--out-merged", type=Path, default=None)
    ap.add_argument("--n-boot", type=int, default=DEFAULT_N_BOOT, help="Subject bootstrap draws for CI.")
    ap.add_argument(
        "--smooth",
        choices=("llo", "subject_llo", "subject_interp", "interp", "ksr"),
        default=DEFAULT_SMOOTH,
        help="interp: PCHIP through coh grand means (default); "
        "subject_interp: per-subject linear interp then mean; "
        "llo: LLO on coh grand means + subject bootstrap; "
        "subject_llo: mean of per-subject LLOs; ksr: pooled Nadaraya–Watson.",
    )
    ap.add_argument(
        "--bandwidth",
        type=float,
        default=DEFAULT_BANDWIDTH,
        help=f"KSR bandwidth on accuracy (default: {DEFAULT_BANDWIDTH}; ignored for interp). "
        "Pass a negative value to use Silverman.",
    )
    args = ap.parse_args()
    bw = None if args.bandwidth is not None and args.bandwidth < 0 else args.bandwidth
    print(
        plot_calib_by_experiment(
            args.repo_root,
            out=args.out_exp,
            dpi=args.dpi,
            n_boot=args.n_boot,
            smooth=args.smooth,
            bandwidth=bw,
        )
    )
    print(
        plot_calib_data_vs_models(
            args.repo_root,
            out=args.out_merged,
            dpi=args.dpi,
            n_boot=args.n_boot,
            smooth=args.smooth,
            bandwidth=bw,
        )
    )


if __name__ == "__main__":
    main()
