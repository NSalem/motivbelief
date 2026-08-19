"""Shared colors, marker face/edge helpers, and figure save."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Mapping, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np

CMAP_INC_3 = 0.7 * np.array([[1.0, 0.0, 0.0], [0.5, 0.5, 0.5], [0.0, 1.0, 0.0]])
CMAP_EXP1B = 0.7 * np.array([[0.0, 0.5, 0.0], [0.0, 1.0, 0.0]])

# Incentive hue for 5-level / by-incentive plots; lighter = correct, darker = error
INC_COLORS: Dict[float, Dict[str, str]] = {
    -1.0: {"correct": "#e07070", "error": "#8b1515"},
    0.0: {"correct": "#a8a8a8", "error": "#3a3a3a"},
    1.0: {"correct": "#6db86d", "error": "#1a5c1a"},
}
INC_LINE_COLOR: Dict[float, str] = {
    -1.0: "#c04040",
    0.0: "#606060",
    1.0: "#2a8a2a",
}
INC_LABELS: Dict[float, str] = {-1.0: "inc −1", 0.0: "inc 0", 1.0: "inc +1"}
INC_LEVELS = (-1.0, 0.0, 1.0)


def make_inc_map_flexible(inc_levels: np.ndarray | Sequence[float], n_colors: int) -> Dict[float, int]:
    inc_levels = np.sort(np.unique(np.asarray(inc_levels, dtype=float)))
    if n_colors == 3 and len(inc_levels) == 3 and np.allclose(inc_levels, [-1, 0, 1]):
        return {-1.0: 0, 0.0: 1, 1.0: 2}
    out: Dict[float, int] = {}
    for i, v in enumerate(inc_levels):
        out[float(v)] = min(i, n_colors - 1)
    return out


def lookup_inc_idx(inc_to_idx: Mapping[float, int], inc: float) -> int:
    for k, v in inc_to_idx.items():
        if np.isclose(float(inc), float(k), rtol=0.0, atol=1e-9):
            return v
    raise KeyError(f"incentive {inc!r} not in {list(inc_to_idx.keys())}")


def open_filled_faces(panel_k: int, cmap: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """panel_k 1 = open markers (edge color); 2 = filled markers."""
    n = cmap.shape[0]
    if panel_k == 1:
        return np.ones((n, 3)), cmap.copy()
    return cmap.copy(), np.zeros((n, 3))


def save_fig(fig: plt.Figure, path: Path, *, dpi: int = 150, facecolor: str | None = None) -> Path:
    """Write PNG + SVG next to ``path`` and close the figure."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    kw = {}
    if facecolor is not None:
        kw["facecolor"] = facecolor
    fig.savefig(path, dpi=dpi, **kw)
    fig.savefig(path.with_suffix(".svg"), **kw)
    plt.close(fig)
    return path
