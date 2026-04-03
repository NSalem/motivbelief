# sim_confirm | AVG stats

## Response variable: `calib`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |     mean |     se |        t |   df |     p |
|:-------------|:-------|---------:|-------:|---------:|-----:|------:|
| Free         | b0     |   4.4422 | 0.6806 |   6.527  |  192 | 0     |
| Free         | b_inc  |   3.4843 | 0.2221 |  15.6897 |  192 | 0     |
| Free         | b_abs  |  -0.0045 | 0.3555 |  -0.0126 |  192 | 0.99  |
| Non-Free     | b0     | -11.3592 | 0.4743 | -23.9504 |  192 | 0     |
| Non-Free     | b_inc  |   2.1752 | 0.2071 |  10.501  |  192 | 0     |
| Non-Free     | b_abs  |  -0.182  | 0.3593 |  -0.5066 |  192 | 0.613 |


### Between-group tests (pairwise Welch)

| pair            | coef   |     mean |     se |        t |      df |      p |
|:----------------|:-------|---------:|-------:|---------:|--------:|-------:|
| Non-Free - Free | b0     | -15.8014 | 0.8295 | -19.0483 | 342.895 | 0      |
| Non-Free - Free | b_inc  |  -1.3092 | 0.3037 |  -4.3109 | 382.152 | 0      |
| Non-Free - Free | b_abs  |  -0.1775 | 0.5054 |  -0.3512 | 383.957 | 0.7256 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |   p |
|:---------|:-------------|--------:|-----:|----:|
| Free     | 1 - 0        |  8.5057 |  192 |   0 |
| Free     | -1 - 0       | -8.1324 |  192 |   0 |
| Free     | 1 - -1       | 15.6897 |  192 |   0 |
| Non-Free | 1 - 0        |  5.1141 |  192 |   0 |
| Non-Free | -1 - 0       | -5.3784 |  192 |   0 |
| Non-Free | 1 - -1       | 10.501  |  192 |   0 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.4391 |   0 | 193 |
| Non-Free | 0.5045 |   0 | 193 |

