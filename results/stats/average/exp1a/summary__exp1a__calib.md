# exp1a | AVG stats

## Response variable: `calib`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |     mean |     se |        t |   df |      p |
|:-------------|:-------|---------:|-------:|---------:|-----:|-------:|
| Free         | b0     |   0.0046 | 1.5721 |   0.003  |   95 | 0.9976 |
| Free         | b_inc  |   3.8705 | 0.5832 |   6.6365 |   95 | 0      |
| Free         | b_abs  |  -0.3087 | 0.8458 |  -0.365  |   95 | 0.7159 |
| Observed     | b0     | -10.0049 | 0.8503 | -11.7667 |   99 | 0      |
| Observed     | b_inc  |   0.9882 | 0.3246 |   3.0445 |   99 | 0.003  |
| Observed     | b_abs  |   1.4046 | 0.552  |   2.5445 |   99 | 0.0125 |


### Between-group tests (pairwise Welch)

| pair            | coef   |     mean |     se |       t |      df |      p | test   |
|:----------------|:-------|---------:|-------:|--------:|--------:|-------:|:-------|
| Observed - Free | b0     | -10.0096 | 1.7873 | -5.6003 | 146.665 | 0      | welch  |
| Observed - Free | b_inc  |  -2.8824 | 0.6674 | -4.3185 | 149.223 | 0      | welch  |
| Observed - Free | b_abs  |   1.7133 | 1.01   |  1.6964 | 164.526 | 0.0917 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  3.8681 |   95 | 0.0002 |
| Free     | -1 - 0       | -3.7187 |   95 | 0.0003 |
| Free     | 1 - -1       |  6.6365 |   95 | 0      |
| Observed | 1 - 0        |  3.5927 |   99 | 0.0005 |
| Observed | -1 - 0       |  0.6786 |   99 | 0.499  |
| Observed | 1 - -1       |  3.0445 |   99 | 0.003  |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |      p |   n |
|:---------|-------:|-------:|----:|
| Free     | 0.3625 | 0.0003 |  96 |
| Observed | 0.4878 | 0      | 100 |

