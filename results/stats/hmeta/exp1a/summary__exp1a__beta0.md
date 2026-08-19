# exp1a | meta-d′ AVG-style stats

## Response variable: `beta0`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |   mean |     se |       t |   df |      p |
|:-------------|:-------|-------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 1.7484 | 0.1409 | 12.4125 |   95 | 0      |
| Free         | b_inc  | 0.0281 | 0.0363 |  0.7754 |   95 | 0.4401 |
| Free         | b_abs  | 0.0633 | 0.0586 |  1.0791 |   95 | 0.2833 |
| Observed     | b0     | 2.1694 | 0.1588 | 13.6624 |   99 | 0      |
| Observed     | b_inc  | 0.053  | 0.0312 |  1.7013 |   99 | 0.092  |
| Observed     | b_abs  | 0.0278 | 0.0602 |  0.4614 |   99 | 0.6455 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p | test   |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Observed - Free | b0     |  0.421  | 0.2123 |  1.9835 | 192.131 | 0.0487 | welch  |
| Observed - Free | b_inc  |  0.0249 | 0.0478 |  0.5211 | 188.506 | 0.6029 | welch  |
| Observed - Free | b_abs  | -0.0355 | 0.0841 | -0.4223 | 193.993 | 0.6733 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  1.2411 |   95 | 0.2176 |
| Free     | -1 - 0       |  0.5504 |   95 | 0.5834 |
| Free     | 1 - -1       |  0.7754 |   95 | 0.4401 |
| Observed | 1 - 0        |  1.1368 |   99 | 0.2584 |
| Observed | -1 - 0       | -0.3921 |   99 | 0.6958 |
| Observed | 1 - -1       |  1.7013 |   99 | 0.092  |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.4515 |   0 |  96 |
| Observed | 0.5803 |   0 | 100 |

