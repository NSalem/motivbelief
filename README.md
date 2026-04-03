## Code and data for Motivated Beliefs paper

This repository contains the analysis pipeline for a (currently unpublished) study on motivated beliefs in a perceptual task (see [preprint](https://osf.io/heaf8_v1)).  
  
Contents include: trial-level data, psychometric fits of choice, computational model simulations of belief ratings, average- and trial-level statistics and figure generation (Python).

**Tested with:** Python 3.9+. Install dependencies via `pip install -e .` (`[pyproject.toml](pyproject.toml)`).

---

### Layout


| Path                                   | Contents                                                                                       |
| -------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `[data/](data/)`                       | Trial-level CSVs per experiment (`data_exp1a.csv`, …). See `[data/README.md](data/README.md)`. |
| `[src/motivbelief/](src/motivbelief/)` | Library code (stats, tables, figures).                                                         |
| `[scripts/](scripts/)`                 | Runnable entry points (fit choice, simulate belief, stats pipeline, figures).                  |
| `results/`                             | Generated outputs: `fit_choice/`, `sims/`, `**stats/`** (statistics, tables, effect sizes).    |
| `plots/`                               | Figures from `scripts/plot_makefigs.py` (created alongside PNGs).                              |


---

### Install

Create an environment with `venv` or `conda create`, then on the root folder do:

```bash
pip install -e .
```

---

### Full reproduction

From the repository root, in order:

1. **Choice model** — per participant × incentive × experiment; writes `results/fits_choice/`.
  ```bash
   python scripts/fit_choice_model.py
  ```
2. **Belief simulations** — three model variants (`act`, `intent`, `confirm`); writes `results/sims/`.
  ```bash
   python scripts/simulate_belief_models.py
  ```
3. **Statistics** — participant-average GLMs, trial-level xpatt models, aggregate markdown tables, Cohen’s *d* tables:
  ```bash
   python scripts/run_stats_pipeline.py --repo-root .
  ```
   Defaults write to `results/stats/average`, `results/stats/trial`, `results/stats/effectsizes`. Override with `--avg-root`, `--trial-root`, `--effects-root` if needed.
   Equivalent modular steps (for debugging):
4. **Figures** — PNG + SVG under `plots/`:
  ```bash
   python scripts/plot_makefigs.py --repo-root .
  ```
   Select subsets: `python scripts/plot_makefigs.py --only behav glm` (see `--help` for group names).

---

### Scripts reference


| Script                              | Role                                                                                                        |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `scripts/fit_choice_model.py`       | 3-parameter choice model (`sigma_act`, `choice_bias`, `p_lapse`); pickles + CSVs in `results/fits_choice/`. |
| `scripts/simulate_belief_models.py` | Simulate trial-level belief under different models (action/intention/confirmation-congruent).               |
| `scripts/run_stats_pipeline.py`     | Chains stats_avg → summaries → stats_xpatt → effect sizes.                                                  |
| `scripts/plot_makefigs.py`          | All figure groups (`model_avg`, `xpatt`, `behav`, `glm`, `psyfun`, …).                                      |


