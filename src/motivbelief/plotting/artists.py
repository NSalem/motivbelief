"""Shared matplotlib artist helpers (violins, etc.)."""

from __future__ import annotations

from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde


def kde_violin(
    ax: plt.Axes,
    data: np.ndarray,
    x_pos: float,
    color: Tuple[float, float, float] | np.ndarray,
    *,
    width: float = 0.4,
    alpha: float = 0.25,
    edgecolor: Tuple[float, float, float] = (0.3, 0.3, 0.3),
    edgewidth: float = 0.6,
) -> None:
    data = np.asarray(data, dtype=float)
    data = data[np.isfinite(data)]
    if data.size == 0:
        return
    if data.size == 1:
        ax.scatter([x_pos], [float(data[0])], c=[color], edgecolors="k", zorder=3)
        return
    lo, hi = float(np.min(data)), float(np.max(data))
    if lo == hi:
        y = np.linspace(lo - 0.5, hi + 0.5, 50)
        d = np.ones_like(y) * width
    else:
        kde = gaussian_kde(data)
        y = np.linspace(lo, hi, 80)
        d = kde(y)
        d_max = float(np.max(d)) if np.max(d) > 0 else 1.0
        d = d / d_max * width
    # Face alpha would also fade the edge if set on fill_betweenx; draw outline separately.
    ax.fill_betweenx(
        y,
        x_pos - d,
        x_pos + d,
        facecolor=color,
        alpha=alpha,
        edgecolor="none",
        linewidth=0,
        zorder=1,
    )
    ax.plot(x_pos - d, y, color=edgecolor, linewidth=edgewidth, solid_capstyle="round", zorder=2)
    ax.plot(x_pos + d, y, color=edgecolor, linewidth=edgewidth, solid_capstyle="round", zorder=2)
