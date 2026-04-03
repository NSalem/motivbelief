# exp1b | AVG stats

## Response variable: `calib`

### Model used for participant coefficients

- `y ~ 1 + incentive`
- Incentive levels: 0.1, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |     mean |     se |        t |   df |      p |
|:-------------|:-------|---------:|-------:|---------:|-----:|-------:|
| Free         | b0     |   0.1319 | 1.3434 |   0.0982 |   91 | 0.922  |
| Free         | b_inc  |   3.1011 | 0.8789 |   3.5284 |   91 | 0.0007 |
| Observed     | b0     | -11.4737 | 0.8257 | -13.8966 |   99 | 0      |
| Observed     | b_inc  |   1.9524 | 0.6294 |   3.1021 |   99 | 0.0025 |


### Between-group tests (pairwise Welch)

| pair            | coef   |     mean |     se |       t |      df |      p |
|:----------------|:-------|---------:|-------:|--------:|--------:|-------:|
| Observed - Free | b0     | -11.6056 | 1.5769 | -7.3599 | 152.702 | 0      |
| Observed - Free | b_inc  |  -1.1487 | 1.081  | -1.0627 | 167.72  | 0.2895 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |      t |   df |      p |
|:---------|:-------------|-------:|-----:|-------:|
| Free     | 1.0 - 0.1    | 3.5284 |   91 | 0.0007 |
| Observed | 1.0 - 0.1    | 3.1021 |   99 | 0.0025 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

_None_

