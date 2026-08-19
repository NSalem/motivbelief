"""
Free-condition recovery figures from ``scripts/recover_free.py`` outputs under
``results/modeling/recovery_conf/Free/``:

1. Model confusion matrix (bootstrap BMC max-PXP fractions).
2. Within-model parameter-recovery correlation heatmaps.
3. Generative-vs-recovered scatterplots per parameter.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from motivbelief.modeling.conf_recovery import correlation_block
from motivbelief.plotting.paths import fig_dir
from motivbelief.plotting.style import save_fig

FONT_SIZE = 20
plt.rcParams.update(
    {
        "font.size": FONT_SIZE,
        "axes.titlesize": FONT_SIZE,
        "axes.labelsize": FONT_SIZE,
        "xtick.labelsize": FONT_SIZE,
        "ytick.labelsize": FONT_SIZE,
        "legend.fontsize": FONT_SIZE,
        "figure.titlesize": FONT_SIZE,
    }
)

# Match scripts/recover_free.py VARIANTS
FREE_MODELS: Tuple[str, ...] = ("pe_wt_v", "bel_bias_v")
MODEL_PARAMS: Dict[str, Tuple[str, ...]] = {
    "pe_wt_v": ("pe_wt", "pe_wt_v", "bel_noise"),
    "bel_bias_v": ("pe_wt", "bel_bias_v", "bel_noise"),
}

PARAM_LABELS: Dict[str, str] = {
    "pe_wt": r"$\alpha_0$",
    "pe_wt_v": r"$\alpha_V$",
    "bel_bias_v": r"$\gamma_V$",
    "bel_noise": r"$\sigma_{\mathrm{bel}}$",
}
# Names used specifically in the model-confusion matrix.
MODEL_LABELS: Dict[str, str] = {
    "pe_wt_v": "weight",
    "bel_bias_v": "add",
}

POINT_COLOR = "#3b6fa0"
LINE_COLOR = "#999999"


def recovery_free_dir(repo: Path) -> Path:
    return repo.resolve() / "results" / "modeling" / "recovery_conf" / "Free"


def _param_label(name: str) -> str:
    return PARAM_LABELS.get(name, name)


def _model_label(name: str) -> str:
    return MODEL_LABELS.get(name, name)


def load_bootstrap_bmc(repo: Path) -> pd.DataFrame:
    """Per-resample BMC table from ``analyze_recovery_identifiability.py``."""
    path = recovery_free_dir(repo) / "bootstrap_bmc.csv"
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing {path}; run scripts/recover_free.py then "
            "scripts/analyze_recovery_identifiability.py."
        )
    return pd.read_csv(path)


def bootstrap_pxp_confusion(
    boot: pd.DataFrame,
    *,
    models: Sequence[str] = FREE_MODELS,
    pxp_col: str = "protected_exceedance_probability",
) -> pd.DataFrame:
    """Generative × recovered: fraction of bootstraps where each fit_model
    had the maximum protected exceedance probability.

    Ties on max PXP are broken by earlier models in ``models`` order.
    """
    models = list(models)
    boot = boot.copy()
    boot["fit_model"] = pd.Categorical(boot["fit_model"], categories=models, ordered=True)
    winners = (
        boot.sort_values([pxp_col, "fit_model"], ascending=[False, True], kind="mergesort")
        .groupby(["generative_model", "boot_iter"], as_index=False)
        .first()[["generative_model", "boot_iter", "fit_model"]]
        .rename(columns={"fit_model": "predicted_model"})
    )
    winners["predicted_model"] = winners["predicted_model"].astype(str)

    counts = (
        winners.groupby(["generative_model", "predicted_model"], observed=False)
        .size()
        .rename("n")
        .reset_index()
    )
    totals = winners.groupby("generative_model").size().rename("n_total")
    out = counts.merge(totals, on="generative_model")
    out["fraction"] = out["n"] / out["n_total"]
    return out


def confusion_matrix(confusion: pd.DataFrame, models: Sequence[str] = FREE_MODELS) -> pd.DataFrame:
    """Square generative × predicted fraction matrix (missing cells → 0)."""
    models = list(models)
    mat = (
        confusion.pivot(index="generative_model", columns="predicted_model", values="fraction")
        .reindex(index=models, columns=models)
        .fillna(0.0)
    )
    return mat.astype(float)


def load_param_corr(repo: Path, model: str) -> pd.DataFrame:
    """True(rows) × recovered(cols) correlation block for one Free model."""
    root = recovery_free_dir(repo)
    cached = root / f"param_recovery_corr_{model}.csv"
    if cached.is_file():
        return pd.read_csv(cached, index_col=0)

    path = root / f"param_recovery_{model}.csv"
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing {cached} and {path}; run scripts/recover_free.py first."
        )
    params = list(MODEL_PARAMS[model])
    return correlation_block(pd.read_csv(path), params)


def load_param_recovery(repo: Path, model: str) -> pd.DataFrame:
    root = recovery_free_dir(repo)
    path = root / f"param_recovery_{model}.csv"
    if not path.is_file():
        raise FileNotFoundError(f"Missing {path}; run scripts/recover_free.py first.")
    return pd.read_csv(path)


def _annotate_heatmap(ax: plt.Axes, data: np.ndarray, *, fmt: str = ".2f") -> None:
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            val = data[i, j]
            if not np.isfinite(val):
                continue
            # Dark text on light cells, light text on dark cells (RdBu_r / Blues).
            text_color = "white" if abs(val) > 0.55 else "black"
            ax.text(j, i, format(val, fmt), ha="center", va="center", color=text_color, fontsize=FONT_SIZE)


def _draw_labeled_heatmap(
    ax: plt.Axes,
    mat: pd.DataFrame,
    *,
    cmap: str,
    vmin: float,
    vmax: float,
    center: Optional[float] = None,
    row_labels: Sequence[str],
    col_labels: Sequence[str],
    xlabel: str,
    ylabel: str,
):
    data = mat.to_numpy(dtype=float)
    if center is not None:
        # Symmetric diverging map around ``center`` without seaborn.
        from matplotlib.colors import TwoSlopeNorm

        norm = TwoSlopeNorm(vmin=vmin, vcenter=center, vmax=vmax)
        im = ax.imshow(data, cmap=cmap, norm=norm, aspect="equal")
    else:
        im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax, aspect="equal")

    n_r, n_c = data.shape
    ax.set_xticks(range(n_c))
    ax.set_yticks(range(n_r))
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    _annotate_heatmap(ax, data, fmt=".2f")
    return im


def plot_confusion_matrix_figure(
    repo_root: Path,
    *,
    out_path: Optional[Path] = None,
    dpi: int = 150,
) -> Path:
    """Heatmap of bootstrap PXP-winner proportions (generative × recovered)."""
    repo_root = repo_root.resolve()
    conf = confusion_matrix(bootstrap_pxp_confusion(load_bootstrap_bmc(repo_root)))
    labels = [_model_label(m) for m in conf.index]

    fig, ax = plt.subplots(figsize=(4.55, 3.92), constrained_layout=True)
    fig.patch.set_facecolor("white")
    im = _draw_labeled_heatmap(
        ax,
        conf,
        cmap="Blues",
        vmin=0.0,
        vmax=1.0,
        row_labels=labels,
        col_labels=labels,
        xlabel="Recovered (max PXP)",
        ylabel="Generative model",
    )
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Proportion of bootstraps")

    out = out_path or (fig_dir(repo_root) / "plots_recov_confusion_free.png")
    return save_fig(fig, out, dpi=dpi, facecolor="white")


def plot_param_recovery_corr_figure(
    repo_root: Path,
    *,
    out_path: Optional[Path] = None,
    dpi: int = 150,
    models: Sequence[str] = FREE_MODELS,
) -> Path:
    """Side-by-side within-model true×recovered correlation heatmaps."""
    repo_root = repo_root.resolve()
    models = list(models)
    fig, axes = plt.subplots(1, len(models), figsize=(4.34 * len(models), 4.06), constrained_layout=True)
    if len(models) == 1:
        axes = [axes]
    fig.patch.set_facecolor("white")

    last_im = None
    for ax, model in zip(axes, models):
        corr = load_param_corr(repo_root, model)
        params = list(corr.index)
        # Keep column order aligned with index when possible.
        corr = corr.reindex(index=params, columns=params)
        labels = [_param_label(p) for p in params]
        last_im = _draw_labeled_heatmap(
            ax,
            corr,
            cmap="RdBu_r",
            vmin=-1.0,
            vmax=1.0,
            center=0.0,
            row_labels=labels,
            col_labels=labels,
            xlabel="Recovered parameters",
            ylabel="Generative parameters",
        )

    if last_im is not None:
        fig.colorbar(last_im, ax=axes[-1], fraction=0.046, pad=0.04, label="Pearson r")

    out = out_path or (fig_dir(repo_root) / "plots_recov_param_corr_free.png")
    return save_fig(fig, out, dpi=dpi, facecolor="white")


def plot_recovery_scatter_figure(
    repo_root: Path,
    *,
    out_path: Optional[Path] = None,
    dpi: int = 150,
    models: Sequence[str] = FREE_MODELS,
) -> Path:
    """True vs recovered scatter per parameter, one row per Free model."""
    repo_root = repo_root.resolve()
    models = list(models)
    n_rows = len(models)
    n_cols = max(len(MODEL_PARAMS[m]) for m in models)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4.2 * n_cols, 4.2 * n_rows))
    if n_rows == 1:
        axes = np.asarray([axes])
    fig.patch.set_facecolor("white")

    for i, model in enumerate(models):
        df = load_param_recovery(repo_root, model)
        params = list(MODEL_PARAMS[model])
        for j in range(n_cols):
            ax = axes[i, j]
            if j >= len(params):
                ax.axis("off")
                continue
            p = params[j]
            x = df[f"true_{p}"].to_numpy(dtype=float)
            y = df[f"hat_{p}"].to_numpy(dtype=float)
            mask = np.isfinite(x) & np.isfinite(y)
            x, y = x[mask], y[mask]
            r = float(np.corrcoef(x, y)[0, 1]) if len(x) > 1 else float("nan")

            lo = min(x.min(), y.min())
            hi = max(x.max(), y.max())
            pad = 0.05 * (hi - lo if hi > lo else 1.0)
            ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad], "--", color=LINE_COLOR, lw=1, zorder=1)
            ax.scatter(x, y, s=14, color=POINT_COLOR, alpha=0.6, edgecolors="none", zorder=2)
            ax.set_xlim(lo - pad, hi + pad)
            ax.set_ylim(lo - pad, hi + pad)
            ax.text(
                0.05,
                0.95,
                f"{_param_label(p)}  r={r:.2f}",
                transform=ax.transAxes,
                ha="left",
                va="top",
                fontsize=FONT_SIZE,
            )
            if j == 0:
                ax.set_ylabel("Recovered parameters")
            if i == n_rows - 1:
                ax.set_xlabel("Generative parameters")

    fig.tight_layout()
    out = out_path or (fig_dir(repo_root) / "plots_recov_scatter_free.png")
    return save_fig(fig, out, dpi=dpi, facecolor="white")


def plot_recov_figures(repo_root: Path, *, dpi: int = 150) -> List[Path]:
    """Build all Free recovery figures; return output PNG paths."""
    return [
        plot_confusion_matrix_figure(repo_root, dpi=dpi),
        plot_param_recovery_corr_figure(repo_root, dpi=dpi),
        plot_recovery_scatter_figure(repo_root, dpi=dpi),
    ]


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Free recovery figures (confusion, param corr, scatter)."
    )
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument(
        "--only",
        nargs="*",
        default=None,
        metavar="NAME",
        help="Subset: confusion, param_corr, scatter (default: all).",
    )
    args = ap.parse_args()
    want = set(args.only) if args.only else {"confusion", "param_corr", "scatter"}
    repo = args.repo_root.resolve()
    if "confusion" in want:
        print(plot_confusion_matrix_figure(repo, dpi=args.dpi))
    if "param_corr" in want:
        print(plot_param_recovery_corr_figure(repo, dpi=args.dpi))
    if "scatter" in want:
        print(plot_recovery_scatter_figure(repo, dpi=args.dpi))


if __name__ == "__main__":
    main()
