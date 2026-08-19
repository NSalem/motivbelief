# Meta-d′ helpers

## Default: Bayesian individual (`scripts/r/fit_hmeta_d.R`)

Per-participant Bayesian meta-d′ / M-ratio via CRAN [`hmetad`](https://cran.r-project.org/package=hmetad)
(brms / Stan). One fit per **participant × choiceType** (Free / Observed / Forced / Replayed as present in the data). Formula (default mode):

- `log M ~ incentive × coh3`
- `d′ ~ coh3`
- type-1 `c ~ 1`
- type-2 criteria `~ incentive`

Confidence: **equal-width bins on [0, 100]** (default K=6).

```bash
Rscript scripts/r/fit_hmeta_d.R --dataset exp1a
Rscript scripts/r/fit_hmeta_d.R --dataset exp3 --choice-types Forced Replayed
Rscript scripts/r/fit_hmeta_d.R --all
python scripts/fit_hmeta_d.py --dataset exp1a          # thin wrapper → R
Rscript scripts/r/fit_hmeta_d.R --dataset exp1a --max-subjects 2
```

Fit datasets: `exp1a`, `exp1b`, `exp2`, `exp3`, `sim_act`, `sim_intent`, `sim_confirm` (no separate `merged` fit; data-vs-models plots pool exp1a+exp2 subject results).

**coh3 bins:** low={1,3}→−1, mid={5}→0, high={9,38}→+1.

Outputs under `results/hmeta_d/<dataset>/`:

| File | Content |
|------|---------|
| `subject_summary.csv` | Posterior means / R̂ / ESS per fixed effect × subject |
| `subject_effects.csv` | Subject contrasts for plotting (`mu_incentive`, `type2_incentive`, …) |
| `group_summary.csv` | Across-subject mean / SEM / *t* vs 0 |
| `cell_mratio_summary.csv` | Group mean ± SEM of *M* / meta-*d′* / *d′* on the grid |
| `convergence_qc.csv` | Per-subject R̂ / ESS flags (`qc_pass`) |
| `preparation.json`, `meta.json` | Coding + fit metadata |

Stats (after fits exist): per participant × incentive, `meta_d ~ 1 + coh3` on the Bayes-implied grid, giving per-participant `beta0` (intercept) and `beta1` (slope). `beta0`/`beta1` are then analyzed exactly like the average-level behavioral outcomes in `stats_avg` (accuracy, belief, calibration, ...): per-participant regression on incentive (`y ~ 1 + incentive`, or `y ~ 1 + incentive + |incentive|` for signed −1/0/+1 designs), then within-group one-sample t-tests, between-group Welch/paired t-tests, pairwise incentive-level t-tests, and (for −1/0/+1 designs) the gain/loss correlation — see `motivbelief.stats.stats_avg`.

```bash
python -m motivbelief.stats.stats_hmeta
# or via the full pipeline (step 6):
python scripts/run_stats_pipeline.py --repo-root .
```

Outputs under `results/stats/hmeta/<dataset>/`: `coh_fits.csv`, `meta_d_grid.csv`, and per response variable (`beta0`, `beta1`) `sub_effects__*.csv`, `within_summary__*.csv`, `between_summary__*.csv`, `ttests_incentives__*.csv`, `gain_loss_corr__*.csv` (signed designs only), `summary__*.md` — same file layout as `results/stats/average/<stem>/`.

Figures (condition = rows × dataset = columns; meta-d′, *M*-ratio, type-2 avg S1/S2, incentive-effect violins):

```bash
python scripts/plot_figures.py --only hmeta
python -m motivbelief.plotting.fig_hmeta --layout by_experiment
python -m motivbelief.plotting.fig_hmeta --layout data_vs_models
```

## Legacy

| Script | Role |
|--------|------|
| [`_old/fit_hmeta_d_hierarchical.R`](_old/fit_hmeta_d_hierarchical.R) | Group hierarchical (diverged on exp1a) |
| [`../_old/fit_hmeta_d_mle.py`](../_old/fit_hmeta_d_mle.py) | Cell-wise MLE via `metadpy` → `results/hmeta_d_mle/` |
| [`_old/fit_hmeta_d_bayes_indiv.R`](_old/fit_hmeta_d_bayes_indiv.R) | Deprecated stub → `fit_hmeta_d.R` |

Upstream JAGS HMeta-d sources remain under `_vendor/HMeta-d/`.
