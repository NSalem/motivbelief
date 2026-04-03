# Trial-level data files

CSV files are comma-separated, one row per trial.

## Files


| File             | Experiment    |
| ---------------- | ------------- |
| `data_exp1a.csv` | Experiment 1a |
| `data_exp1b.csv` | Experiment 1b |
| `data_exp2.csv`  | Experiment 2  |
| `data_exp3.csv`  | Experiment 3  |


## Core columns (typical)


| Column          | Description                                                  |
| --------------- | ------------------------------------------------------------ |
| `participantID` | Anonymous participant identifier                             |
| `trial`         | Trial index within session                                   |
| `coh`           | Motion coherence (signed = direction)                        |
| `stim`          | Stimulus strength / signed coherence                         |
| `resp`          | Response (e.g. left/right)                                   |
| `correct`       | Accuracy (0/1)                                               |
| `conf`          | Belief rating (a.k.a. confidence)                            |
| `incentive`     | Incentive level (coded, e.g. −1, 0, 1 for loss/neutral/gain) |
| `choiceType`    | Task context (e.g. Free, Observed, Replayed, Forced)         |
| `rt`            | Response time (ms)                                           |


Other columns may include frame timing, bonus, and task metadata. The analysis code in `src/motivbelief/` documents any additional fields used in GLMs and fits.

