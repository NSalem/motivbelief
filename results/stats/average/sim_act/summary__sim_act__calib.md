# sim_act | AVG stats

## Response variable: `calib`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     |  0.9032 | 1.1079 |  0.8152 |  192 | 0.4159 |
| Free         | b_inc  |  2.9121 | 0.4044 |  7.2003 |  192 | 0      |
| Free         | b_abs  | -1.4312 | 0.4586 | -3.1207 |  192 | 0.0021 |
| Non-Free     | b0     | -8.8988 | 1.1327 | -7.8564 |  192 | 0      |
| Non-Free     | b_inc  |  3.1023 | 0.4333 |  7.1594 |  192 | 0      |
| Non-Free     | b_abs  | -0.6979 | 0.4442 | -1.5712 |  192 | 0.1178 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |        t |   df |      p | test   |
|:----------------|:-------|--------:|-------:|---------:|-----:|-------:|:-------|
| Non-Free - Free | b0     | -9.802  | 0.9655 | -10.1522 |  192 | 0      | paired |
| Non-Free - Free | b_inc  |  0.1902 | 0.2969 |   0.6407 |  192 | 0.5225 | paired |
| Non-Free - Free | b_abs  |  0.7333 | 0.528  |   1.389  |  192 | 0.1664 | paired |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  2.8044 |  192 | 0.0056 |
| Free     | -1 - 0       | -6.3423 |  192 | 0      |
| Free     | 1 - -1       |  7.2003 |  192 | 0      |
| Non-Free | 1 - 0        |  4.5329 |  192 | 0      |
| Non-Free | -1 - 0       | -5.4358 |  192 | 0      |
| Non-Free | 1 - -1       |  7.1594 |  192 | 0      |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |      p |   n |
|:---------|-------:|-------:|----:|
| Free     | 0.1293 | 0.073  | 193 |
| Non-Free | 0.0257 | 0.7227 | 193 |

