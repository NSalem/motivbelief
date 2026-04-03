# exp1a_exp2free_exp3 | AVG stats

## Response variable: `confSym`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 73.1808 | 0.8833 | 26.243  |  192 | 0      |
| Free         | b_inc  |  2.5803 | 0.2711 |  9.5196 |  192 | 0      |
| Free         | b_abs  |  0.6454 | 0.3032 |  2.1284 |  192 | 0.0346 |
| Non-Free     | b0     | 66.0938 | 0.448  | 35.9264 |  295 | 0      |
| Non-Free     | b_inc  |  1.1977 | 0.1534 |  7.8088 |  295 | 0      |
| Non-Free     | b_abs  |  0.4278 | 0.2192 |  1.9515 |  295 | 0.0519 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|
| Non-Free - Free | b0     | -7.087  | 0.9904 | -7.1556 | 290.937 | 0      |
| Non-Free - Free | b_inc  | -1.3826 | 0.3114 | -4.4394 | 313.711 | 0      |
| Non-Free - Free | b_abs  | -0.2176 | 0.3742 | -0.5814 | 377.968 | 0.5613 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  8.5703 |  192 | 0      |
| Free     | -1 - 0       | -4.4491 |  192 | 0      |
| Free     | 1 - -1       |  9.5196 |  192 | 0      |
| Non-Free | 1 - 0        |  5.8298 |  295 | 0      |
| Non-Free | -1 - 0       | -3.0101 |  295 | 0.0028 |
| Non-Free | 1 - -1       |  7.8088 |  295 | 0      |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |      p |   n |
|:---------|-------:|-------:|----:|
| Free     | 0.1128 | 0.1182 | 193 |
| Non-Free | 0.344  | 0      | 296 |

