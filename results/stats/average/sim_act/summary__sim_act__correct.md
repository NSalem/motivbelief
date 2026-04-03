# sim_act | AVG stats

## Response variable: `correct`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 73.9508 | 0.6484 | 36.9395 |  192 | 0      |
| Free         | b_inc  | -0.1231 | 0.2343 | -0.5252 |  192 | 0.6001 |
| Free         | b_abs  | -0.0842 | 0.3411 | -0.2468 |  192 | 0.8053 |
| Non-Free     | b0     | 74.6826 | 0.3242 | 76.1357 |  192 | 0      |
| Non-Free     | b_inc  | -0.136  | 0.2333 | -0.583  |  192 | 0.5606 |
| Non-Free     | b_abs  | -0.0712 | 0.4078 | -0.1747 |  192 | 0.8615 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|
| Non-Free - Free | b0     |  0.7319 | 0.7249 |  1.0096 | 282.355 | 0.3136 |
| Non-Free - Free | b_inc  | -0.013  | 0.3307 | -0.0392 | 383.993 | 0.9688 |
| Non-Free - Free | b_abs  |  0.013  | 0.5316 |  0.0244 | 372.375 | 0.9806 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        | -0.5055 |  192 | 0.6138 |
| Free     | -1 - 0       |  0.0931 |  192 | 0.926  |
| Free     | 1 - -1       | -0.5252 |  192 | 0.6001 |
| Non-Free | 1 - 0        | -0.4369 |  192 | 0.6627 |
| Non-Free | -1 - 0       |  0.1392 |  192 | 0.8894 |
| Non-Free | 1 - -1       | -0.583  |  192 | 0.5606 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.3588 |   0 | 193 |
| Non-Free | 0.5069 |   0 | 193 |

