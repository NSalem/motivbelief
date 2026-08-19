# exp1a | AVG stats

## Response variable: `rt_log`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |        t |   df |      p |
|:-------------|:-------|--------:|-------:|---------:|-----:|-------:|
| Free         | b0     |  6.3255 | 0.0321 | 196.95   |   95 | 0      |
| Free         | b_inc  |  0.0021 | 0.0038 |   0.5487 |   95 | 0.5845 |
| Free         | b_abs  | -0.0017 | 0.0071 |  -0.2333 |   95 | 0.816  |
| Observed     | b0     |  6.7057 | 0.0401 | 167.382  |   99 | 0      |
| Observed     | b_inc  |  0.0059 | 0.0036 |   1.6246 |   99 | 0.1074 |
| Observed     | b_abs  | -0.0105 | 0.0057 |  -1.8508 |   99 | 0.0672 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p | test   |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Observed - Free | b0     |  0.3802 | 0.0513 |  7.4053 | 186.757 | 0      | welch  |
| Observed - Free | b_inc  |  0.0038 | 0.0053 |  0.7153 | 192.783 | 0.4753 | welch  |
| Observed - Free | b_abs  | -0.0089 | 0.0091 | -0.9778 | 183.809 | 0.3295 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  0.0513 |   95 | 0.9592 |
| Free     | -1 - 0       | -0.5274 |   95 | 0.5992 |
| Free     | 1 - -1       |  0.5487 |   95 | 0.5845 |
| Observed | 1 - 0        | -0.7144 |   99 | 0.4767 |
| Observed | -1 - 0       | -2.3533 |   99 | 0.0206 |
| Observed | 1 - -1       |  1.6246 |   99 | 0.1074 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.5582 |   0 |  96 |
| Observed | 0.4245 |   0 | 100 |

