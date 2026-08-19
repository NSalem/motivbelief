# exp1a | AVG stats

## Response variable: `confSym`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 75.1494 | 1.3533 | 18.5836 |   95 | 0      |
| Free         | b_inc  |  2.8369 | 0.4522 |  6.2733 |   95 | 0      |
| Free         | b_abs  |  0.6416 | 0.5253 |  1.2215 |   95 | 0.2249 |
| Observed     | b0     | 65.2378 | 0.7335 | 20.7745 |   99 | 0      |
| Observed     | b_inc  |  0.9864 | 0.2432 |  4.0551 |   99 | 0.0001 |
| Observed     | b_abs  |  0.3855 | 0.3711 |  1.0389 |   99 | 0.3014 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p | test   |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Observed - Free | b0     | -9.9116 | 1.5393 | -6.439  | 146.852 | 0      | welch  |
| Observed - Free | b_inc  | -1.8505 | 0.5135 | -3.6039 | 146.182 | 0.0004 | welch  |
| Observed - Free | b_abs  | -0.2561 | 0.6432 | -0.3982 | 172.299 | 0.6909 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  5.5634 |   95 | 0      |
| Free     | -1 - 0       | -2.9079 |   95 | 0.0045 |
| Free     | 1 - -1       |  6.2733 |   95 | 0      |
| Observed | 1 - 0        |  2.8762 |   99 | 0.0049 |
| Observed | -1 - 0       | -1.4737 |   99 | 0.1437 |
| Observed | 1 - -1       |  4.0551 |   99 | 0.0001 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |     p |   n |
|:---------|-------:|------:|----:|
| Free     | 0.1513 | 0.141 |  96 |
| Observed | 0.4038 | 0     | 100 |

