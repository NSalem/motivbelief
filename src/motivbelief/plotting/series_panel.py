"""Generic points/lines panel drawing for X-pattern and calibration figures."""

from __future__ import annotations

from typing import Any, Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np

COH_LEVELS_DEFAULT = (1.0, 3.0, 5.0, 9.0, 38.0)


class Series:
    """One plotted series (points and/or a line). Empty lists skip that layer."""

    __slots__ = (
        "x",
        "y",
        "yerr",
        "xerr",
        "color",
        "markerfacecolor",
        "markeredgecolor",
        "linestyle",
        "marker",
        "label",
        "linewidth",
        "markersize",
        "markeredgewidth",
        "capsize",
        "elinewidth",
        "alpha",
        "zorder",
    )

    def __init__(
        self,
        x: np.ndarray | Sequence[float],
        y: np.ndarray | Sequence[float],
        *,
        yerr: np.ndarray | Sequence[float] | None = None,
        xerr: np.ndarray | Sequence[float] | None = None,
        color: Any = "k",
        markerfacecolor: Any = None,
        markeredgecolor: Any = None,
        linestyle: str = "-",
        marker: str = "o",
        label: str | None = None,
        linewidth: float = 1.6,
        markersize: float = 5.0,
        markeredgewidth: float = 1.0,
        capsize: float = 0.0,
        elinewidth: float | None = None,
        alpha: float = 1.0,
        zorder: int = 3,
    ) -> None:
        self.x = np.asarray(x, dtype=float)
        self.y = np.asarray(y, dtype=float)
        self.yerr = None if yerr is None else np.asarray(yerr, dtype=float)
        self.xerr = None if xerr is None else np.asarray(xerr, dtype=float)
        self.color = color
        self.markerfacecolor = markerfacecolor if markerfacecolor is not None else color
        self.markeredgecolor = markeredgecolor if markeredgecolor is not None else color
        self.linestyle = linestyle
        self.marker = marker
        self.label = label
        self.linewidth = linewidth
        self.markersize = markersize
        self.markeredgewidth = markeredgewidth
        self.capsize = capsize
        self.elinewidth = elinewidth
        self.alpha = alpha
        self.zorder = zorder


def draw_points(ax: plt.Axes, series: Sequence[Series] | None) -> None:
    if not series:
        return
    for s in series:
        good = np.isfinite(s.x) & np.isfinite(s.y)
        if s.yerr is not None:
            good &= np.isfinite(s.yerr)
        if s.xerr is not None:
            good &= np.isfinite(s.xerr)
        if not np.any(good):
            continue
        xg, yg = s.x[good], s.y[good]
        # Markers first, then errorbars on top (stem/caps visible through open markers).
        ax.plot(
            xg,
            yg,
            linestyle="none",
            marker=s.marker,
            color=s.color,
            markerfacecolor=s.markerfacecolor,
            markeredgecolor=s.markeredgecolor,
            markeredgewidth=s.markeredgewidth,
            markersize=s.markersize,
            alpha=s.alpha,
            zorder=s.zorder,
            label=s.label,
        )
        if s.yerr is not None or s.xerr is not None:
            eb_kw: dict[str, Any] = {}
            if s.elinewidth is not None:
                eb_kw["elinewidth"] = s.elinewidth
            ax.errorbar(
                xg,
                yg,
                xerr=None if s.xerr is None else s.xerr[good],
                yerr=None if s.yerr is None else s.yerr[good],
                fmt="none",
                ecolor=s.color,
                alpha=s.alpha,
                zorder=s.zorder + 0.5,
                capsize=s.capsize,
                **eb_kw,
            )



def draw_lines(ax: plt.Axes, series: Sequence[Series] | None, *, band: bool = True) -> None:
    if not series:
        return
    for s in series:
        good = np.isfinite(s.x) & np.isfinite(s.y)
        if not np.any(good):
            continue
        xg, yg = s.x[good], s.y[good]
        if band and s.yerr is not None:
            ye = s.yerr[good]
            ok = np.isfinite(ye)
            if np.sum(ok) >= 2:
                ax.fill_between(
                    xg[ok],
                    yg[ok] - ye[ok],
                    yg[ok] + ye[ok],
                    color=s.color,
                    alpha=0.18,
                    linewidth=0,
                    zorder=max(1, s.zorder - 1),
                )
        if len(xg) >= 2:
            ax.plot(
                xg,
                yg,
                linestyle=s.linestyle,
                color=s.color,
                linewidth=s.linewidth,
                alpha=s.alpha,
                zorder=s.zorder,
                label=s.label,
            )


def style_coh_log_axis(
    ax: plt.Axes,
    coh_levels: Sequence[float] = COH_LEVELS_DEFAULT,
    *,
    xlabel: str = "|coherence| (%)",
) -> None:
    ax.set_xscale("log")
    ax.set_xticks(list(coh_levels))
    ax.set_xticklabels([str(int(c)) for c in coh_levels])
    ax.set_xlabel(xlabel)


def style_belief_axis(
    ax: plt.Axes,
    *,
    ylim: tuple[float, float] = (40.0, 100.0),
    ylabel: str = "confidence",
    title: Optional[str] = None,
    xlim: tuple[float, float] | None = None,
    grid: bool = True,
) -> None:
    ax.set_ylim(*ylim)
    ax.set_ylabel(ylabel)
    if xlim is not None:
        ax.set_xlim(*xlim)
    if title:
        ax.set_title(title)
    if grid:
        ax.grid(True, alpha=0.25, linestyle=":")
    else:
        ax.grid(False)
