## Code and data for "Deciphering the effects of incentive motivation on probabilistic judgments"

This repository contains the analysis pipeline for the study by Salem-Garcia, Massoni & Lebreton on how monetary incentives and agency (Free vs. Observed/Forced/Replayed choice) bias probabilistic judgments (belief ratings).

Contents include: trial-level data, psychometric fits of choice, the computational (2D-SDT) model of belief formation and its Bayesian model comparison / recovery, belief simulations for Free vs. Non-Free choice, average- and trial-level statistics, and all figure generation (Python).


**Tested with:** Python 3.14.3 on WSL. Install dependencies via `pip install -e .` ([`pyproject.toml`](pyproject.toml)).

---

### Layout

| Path | Contents |
|------|----------|
| [`data/`](data/) | Trial-level CSVs per experiment (`data_exp1a.csv`, …). See [`data/README.md`](data/README.md). |
| [`src/motivbelief/`](src/motivbelief/) | Library code: `modeling/` (generative model, LL, fits, Free analysis), `stats/`, `plotting/` (`fig_*`). |
| [`scripts/`](scripts/) | Runnable entry points for the paper core. |
| [`scripts/r/`](scripts/r/) | Project-owned R helpers (e.g. `hmetad` bridge); not third-party. |
| `results/` | Generated outputs under `results/modeling/` (`fits_choice/`, `fits_conf/`, `bmc_conf/`, `recovery_conf/`), plus `sims/`, `stats/` (`average/`, `trial/`, `effectsizes/`, `hmeta/`), and `hmeta_d/`. |
| `plots/` | Figures from `scripts/plot_figures.py`. |

---

### Install

```bash
pip install -e .
```

---

### Full reproduction

From the repository root, in order:

1. **Choice model** — Free + Replayed; writes `results/modeling/fits_choice/<exp>/`.
   ```bash
   python scripts/fit_choice_model.py
   ```
2. **Free confidence fits** — `pe_wt_v` (incentive-weighting) and `bel_bias_v` (additive-evidence alternative); writes `results/modeling/fits_conf/<exp>/results_Free_*.csv`. Sensory/choice parameters are fixed from step 1.
   ```bash
   python scripts/fit_conf_free.py
   ```
3. **Free recovery / identifiability** (main analysis; expensive — hundreds of synthetic participants × cross-fits). Writes `results/modeling/recovery_conf/Free/`.
   ```bash
   python scripts/recover_free.py
   python scripts/analyze_recovery_identifiability.py
   ```
4. **Model comparison (BMC)** — `pe_wt_v` vs `bel_bias_v`; writes `results/modeling/bmc_conf/`.
   ```bash
   python scripts/compare_conf_free.py
   ```
5. **Belief simulations** — Action-/Intention-/Confirmation-congruent models, Free vs. Non-Free; writes `results/sims/`.
   ```bash
   python scripts/simulate_belief.py
   ```
6. **Statistics** — participant-average GLMs, trial-level X-pattern (incl. reaction-time control analyses), effect sizes:
   ```bash
   python scripts/run_stats_pipeline.py --repo-root .
   ```
7. **Figures** — PNG + SVG under `plots/`:
   ```bash
   python scripts/plot_figures.py --repo-root .
   ```
   Subsets: `python scripts/plot_figures.py --only behav glm`. Additional opt-in groups: `--only chosen_contrib`, `--only hmeta`, `--only xpatt_coh` (see mapping table below for what each produces).

`scripts/run_all.py` chains steps 1–2 and 4–7. Pass `--with-recovery` to also run step 3.

Optional Bayesian individual meta-d′ (CRAN [`hmetad`](https://cran.r-project.org/package=hmetad); Free/Observed/Forced/Replayed — SOM Section 10): `Rscript scripts/r/fit_hmeta_d.R --dataset exp1a` or `python scripts/fit_hmeta_d.py --dataset exp1a` → `results/hmeta_d/`; stats via `run_stats_pipeline.py` (`stats_hmeta` step) → `results/stats/hmeta/`; figures via `python scripts/plot_figures.py --only hmeta` (notes in [`scripts/r/README.md`](scripts/r/README.md)).

---

### Scripts reference

| Script | Role |
|--------|------|
| `scripts/fit_choice_model.py` | 3-parameter choice model; Free + Replayed. |
| `scripts/fit_conf_free.py` | Free confidence BADS fits (`pe_wt_v`, `bel_bias_v`). |
| `scripts/recover_free.py` | Free model/parameter recovery cross-fits. |
| `scripts/analyze_recovery_identifiability.py` | Confusion matrix + bootstrap BMC on recovery output. |
| `scripts/compare_conf_free.py` | Free BMC (`pe_wt_v` vs `bel_bias_v`). |
| `scripts/simulate_belief.py` | Simulate Action-/Intention-/Confirmation-congruent belief models, Free vs. Non-Free. |
| `scripts/run_stats_pipeline.py` | stats_avg → summaries → stats_xpatt (incl. RT controls) → effect sizes → stats_hmeta. |
| `scripts/plot_figures.py` | Figure groups — core: `model_avg, xpatt, falsif_xpatt, calib, behav, glm, psyfun, params, recov`; opt-in: `hmeta, chosen_contrib, xpatt_coh` (see mapping table). |
| `scripts/run_all.py` | Chains the pipeline (`--with-recovery` optional). |
| `scripts/fit_hmeta_d.py` | Bayesian individual meta-d′ (wraps `scripts/r/fit_hmeta_d.R`). |

### Library map (modeling)

| Module | Role |
|--------|------|
| `modeling.choice` | Choice psychometric LL |
| `modeling.conf_core` | Generative confidence core + simulate + `expected_confidence` |
| `modeling.conf_ll` | Binned joint-simulation LL + `fit_conf_bads` |
| `modeling.optimize` | BADS / L-BFGS restarts; priors and bounds |
| `modeling.fit_conf` | Shared Free/nonfree fitting loop |
| `modeling.io` | Trial loading + fit CSV/metadata writers |
| `modeling.analysis_free` | Free fit loading, t-tests, BMC, IC helpers |
| `modeling.conf_recovery` | Free recovery engine |

---

### Paper → code map

Every reported analysis below has a corresponding script/output; SOM section numbers refer to the table of contents.

| Paper location | Analysis | Script(s) | Output |
|---|---|---|---|
| Fig. 1–3; SOM §1–3, Supp. Tables 2–9 | Choice psychometrics; average- and trial-level belief statistics (X-pattern) | `fit_choice_model.py`, `run_stats_pipeline.py`, `plot_figures.py --only behav glm psyfun xpatt` | `results/modeling/fits_choice/`, `results/stats/average/`, `results/stats/trial/`, `plots/` |
| Methods "Computational models"; SOM §8 | Generative 2D-SDT model (sensory evidence, covert commitment, offset-clip, belief read-out) | `modeling/conf_core.py` | — (library) |
| Methods "Computational models" (weighting family); SOM §9 (three-model definitions) | Action-/Intention-/Confirmation-congruent bias models | `modeling/conf_core.py` (`mismatch_coef`, `mismatch_gate_baseline`), `modeling/analysis_free.py` | — (library) |
| SOM §9 "Alternative model" | `bel_bias_v` additive-evidence model | `fit_conf_free.py` (`bel_bias_v` variant) | `results/modeling/fits_conf/<exp>/results_Free_bel_bias_v.csv` |
| Methods "Model fitting"; SOM §9, Supp. Table 18 | Free confidence BADS fits, both variants; fitted α₀/α_V/σ_BEL | `fit_conf_free.py` | `results/modeling/fits_conf/<exp>/results_Free_*.csv` |
| SOM §9, Supp. Fig. 4/5 (BMC, confusion matrix, parameter recovery) | `pe_wt_v` vs `bel_bias_v` model comparison + recovery/identifiability | `compare_conf_free.py`, `recover_free.py`, `analyze_recovery_identifiability.py`, `plot_figures.py --only params recov` | `results/modeling/bmc_conf/`, `results/modeling/recovery_conf/Free/` |
| Fig. 4A (x꜀ₕₒₛₑₙ contribution panels) | Chosen-evidence contribution vs. incentive under the three mismatch hypotheses | `plot_figures.py --only chosen_contrib` (`plotting/fig_chosen_contribution.py`) | `plots/` |
| Fig. 4B; SOM §4, Supp. Tables 10–15 | Free vs. Non-Free belief simulations; model-vs-data statistics | `simulate_belief.py`, `run_stats_pipeline.py`, `plot_figures.py --only falsif_xpatt` | `results/sims/`, `results/stats/` |
| Results "calibration"; Discussion calibration paragraph | Calibration curves (belief vs. accuracy), by experiment and data-vs-model | `run_stats_pipeline.py` (`stats_calib`), `plot_figures.py --only calib` | `results/stats/`, `plots/` |
| SOM §5, Supp. Tables 16–17 | RT control analyses (incentive effects on log RT; belief regression with log-RT covariate) | `run_stats_pipeline.py` (`stats_xpatt`, automatic when `rt` present) | `results/stats/trial/` |
| SOM §6 "Matching probability elicitation rule"; §7 "Pilot" | Truth-telling proof; pilot-study calibration of coherence levels | Prose/derivation only — no pipeline code (pilot was a separate one-off study, not part of the main data pipeline) | — |
| Discussion calibration paragraph; SOM §10, Supp. Table 19, Supp. Fig. 5/6 | Meta-d′/M-ratio (Bayesian individual, `hmetad`) | `scripts/r/fit_hmeta_d.R` / `fit_hmeta_d.py`, `run_stats_pipeline.py` (`stats_hmeta`), `plot_figures.py --only hmeta` | `results/hmeta_d/`, `results/stats/hmeta/` |

