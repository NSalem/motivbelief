# exp1a | meta-d′ AVG-style stats

## Response variable: `beta1`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     |  1.559  | 0.1085 | 14.3693 |   95 | 0      |
| Free         | b_inc  |  0.0168 | 0.0314 |  0.5345 |   95 | 0.5943 |
| Free         | b_abs  | -0.011  | 0.0673 | -0.1636 |   95 | 0.8704 |
| Observed     | b0     |  1.5349 | 0.094  | 16.3248 |   99 | 0      |
| Observed     | b_inc  |  0.0397 | 0.0286 |  1.3878 |   99 | 0.1683 |
| Observed     | b_abs  |  0.0987 | 0.0631 |  1.5632 |   99 | 0.1212 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p | test   |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Observed - Free | b0     | -0.024  | 0.1436 | -0.1675 | 188.99  | 0.8671 | welch  |
| Observed - Free | b_inc  |  0.0229 | 0.0424 |  0.54   | 191.561 | 0.5898 | welch  |
| Observed - Free | b_abs  |  0.1097 | 0.0923 |  1.1884 | 192.601 | 0.2361 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  0.0728 |   95 | 0.9421 |
| Free     | -1 - 0       | -0.4005 |   95 | 0.6897 |
| Free     | 1 - -1       |  0.5345 |   95 | 0.5943 |
| Observed | 1 - 0        |  1.8625 |   99 | 0.0655 |
| Observed | -1 - 0       |  0.9228 |   99 | 0.3584 |
| Observed | 1 - -1       |  1.3878 |   99 | 0.1683 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.6488 |   0 |  96 |
| Observed | 0.6669 |   0 | 100 |

