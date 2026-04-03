# exp1a_exp2free_exp3 | AVG stats

## Response variable: `rt_log`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |        t |   df |      p |
|:-------------|:-------|--------:|-------:|---------:|-----:|-------:|
| Free         | b0     |  6.3715 | 0.0251 | 254.304  |  192 | 0      |
| Free         | b_inc  |  0.0015 | 0.0027 |   0.5362 |  192 | 0.5924 |
| Free         | b_abs  | -0.0079 | 0.0052 |  -1.5233 |  192 | 0.1293 |
| Non-Free     | b0     |  6.6328 | 0.021  | 315.573  |  295 | 0      |
| Non-Free     | b_inc  |  0.0047 | 0.002  |   2.3065 |  295 | 0.0218 |
| Non-Free     | b_abs  | -0.0006 | 0.0034 |  -0.1652 |  295 | 0.8689 |


### Between-group tests (pairwise Welch)

| pair            | coef   |   mean |     se |      t |      df |      p |
|:----------------|:-------|-------:|-------:|-------:|--------:|-------:|
| Non-Free - Free | b0     | 0.2613 | 0.0327 | 7.991  | 421.474 | 0      |
| Non-Free - Free | b_inc  | 0.0032 | 0.0034 | 0.9427 | 385.248 | 0.3464 |
| Non-Free - Free | b_abs  | 0.0074 | 0.0062 | 1.1844 | 349.717 | 0.2371 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        | -1.0544 |  192 | 0.293  |
| Free     | -1 - 0       | -1.6769 |  192 | 0.0952 |
| Free     | 1 - -1       |  0.5362 |  192 | 0.5924 |
| Non-Free | 1 - 0        |  1.0646 |  295 | 0.2879 |
| Non-Free | -1 - 0       | -1.2816 |  295 | 0.201  |
| Non-Free | 1 - -1       |  2.3065 |  295 | 0.0218 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.5731 |   0 | 193 |
| Non-Free | 0.4811 |   0 | 296 |

