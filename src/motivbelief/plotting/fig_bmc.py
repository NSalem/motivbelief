"""
Free-condition BMC bar chart: pe_wt_v vs bel_bias_v (AICc evidence).

Bars = expected model frequency (groupBMC frequency_mean); error bars =
sqrt(frequency_var). Protected exceedance probability (PXP) annotated on
each bar. One column per scope (exp1a, exp2, merged), shared y-axis;
models distinguished by white / grey face colors.

Computes BMC from fits under ``results/modeling/fits_conf`` (same as
``scripts/compare_conf_free.py``); see ``free_model_bmc``.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from motivbelief.modeling.analysis_free import (
    FREE_BMC_FIT_TAGS,
    free_model_bmc,
    load_conf_fits,
)
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

# (scope key, panel title, experiments pooled)
BMC_SCOPES: Tuple[Tuple[str, str, Tuple[str, ...]], ...] = (
    ("exp1a", "Exp. 1a", ("exp1a",)),
    ("exp2", "Exp. 2", ("exp2",)),
    ("merged", "Merged", ("exp1a", "exp2")),
)

MODEL_LABELS: Dict[str, str] = {
    "pe_wt_v": r"weight",
    "bel_bias_v": r"add",
}
# White / grey faces (edge always black) — pe_wt_v first, then bel_bias_v.
MODEL_FACE: Dict[str, str] = {
    "pe_wt_v": "white",
    "bel_bias_v": "0.65",
}


def _scope_key(experiments: Sequence[str]) -> str:
    return "+".join(experiments)


def _plot_scope_bars(
    ax: plt.Axes,
    bmc: pd.DataFrame,
    *,
    experiments: Sequence[str],
    models: Sequence[str],
    show_ylabel: bool,
) -> None:
    scope = _scope_key(experiments)
    sub = bmc.loc[bmc["scope"] == scope].set_index("fit_model").reindex(list(models))
    if sub["expected_frequency"].isna().any():
        missing = sub.index[sub["expected_frequency"].isna()].tolist()
        raise ValueError(f"BMC missing models {missing} for scope={scope!r}")

    freqs = sub["expected_frequency"].to_numpy(dtype=float)
    errs = np.sqrt(np.clip(sub["frequency_var"].to_numpy(dtype=float), 0.0, None))
    pxp = sub["protected_exceedance_probability"].to_numpy(dtype=float)

    x = np.arange(len(models), dtype=float)
    colors = [MODEL_FACE[m] for m in models]
    bars = ax.bar(
        x,
        freqs,
        yerr=errs,
        width=0.65,
        color=colors,
        edgecolor="k",
        linewidth=0.7,
        capsize=4,
        error_kw={"elinewidth": 1.0, "capthick": 1.0, "ecolor": "k"},
    )

    winner = int(np.argmax(pxp))
    bar, f, e, p = bars[winner], freqs[winner], errs[winner], pxp[winner]
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        f + e + 0.03,
        f"PXP = {p:.2f}",
        ha="center",
        va="bottom",
        fontsize=FONT_SIZE,
        color="k",
    )

    ax.set_xlabel("Model")
    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_LABELS.get(m, m) for m in models])
    ax.set_yticks([0.0, 1.0])
    if show_ylabel:
        ax.set_ylabel("Expected model frequency")
    ax.set_ylim(0.0, 1.2)
    ax.axhline(0.5, color="0.75", linewidth=0.6, linestyle="--", zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_bounds(0.0, 1.0)
    ax.spines["bottom"].set_bounds(float(x[0]), float(x[-1]))


def plot_free_bmc_figure(
    repo_root: Path,
    out_path: Optional[Path] = None,
    *,
    dpi: int = 150,
) -> Path:
    """Expected frequency ± SD and PXP for Free pe_wt_v vs bel_bias_v BMC."""
    repo_root = Path(repo_root).resolve()
    data = load_conf_fits(repo_root / "results" / "modeling" / "fits_conf")

    # Run per-scope so we can attach n_participants to each panel title.
    models = list(FREE_BMC_FIT_TAGS)
    scope_frames: list[pd.DataFrame] = []
    n_by_scope: Dict[str, Optional[int]] = {}
    for key, _, experiments in BMC_SCOPES:
        frame = free_model_bmc(data, experiments=experiments)
        n_raw = frame.attrs.get("n_participants")
        n_by_scope[key] = int(n_raw) if n_raw is not None else None
        scope_frames.append(frame)
    bmc = pd.concat(scope_frames, ignore_index=True)

    fig, axes = plt.subplots(
        1,
        len(BMC_SCOPES),
        figsize=(7.5, 4.48),
        sharey=True,
        constrained_layout=True,
    )
    fig.patch.set_facecolor("white")
    if len(BMC_SCOPES) == 1:
        axes = [axes]

    for ax, (key, title, experiments) in zip(axes, BMC_SCOPES):
        _plot_scope_bars(
            ax,
            bmc,
            experiments=experiments,
            models=models,
            show_ylabel=(ax is axes[0]),
        )
        n = n_by_scope.get(key)
        n_str = f", n={n}" if n is not None else ""
        ax.set_title(f"{title}{n_str}")

    out = out_path or (fig_dir(repo_root) / "plots_free_bmc.png")
    return save_fig(fig, out, dpi=dpi, facecolor="white")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Free pe_wt_v vs bel_bias_v BMC bar chart (expected frequency ± SD, PXP)."
    )
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()
    print(plot_free_bmc_figure(args.repo_root, out_path=args.out, dpi=args.dpi))


if __name__ == "__main__":
    main()
