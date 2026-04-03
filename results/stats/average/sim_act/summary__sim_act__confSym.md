# sim_act | AVG stats

## Response variable: `confSym`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 78.6591 | 0.5001 | 57.3095 |  192 | 0      |
| Free         | b_inc  |  3.2475 | 0.1066 | 30.4669 |  192 | 0      |
| Free         | b_abs  | -0.4099 | 0.1375 | -2.9813 |  192 | 0.0032 |
| Non-Free     | b0     | 63.7777 | 0.4164 | 33.0844 |  192 | 0      |
| Non-Free     | b_inc  |  2.9359 | 0.1505 | 19.5034 |  192 | 0      |
| Non-Free     | b_abs  | -0.1741 | 0.2623 | -0.664  |  192 | 0.5075 |


### Between-group tests (pairwise Welch)

| pair            | coef   |     mean |     se |        t |      df |      p |
|:----------------|:-------|---------:|-------:|---------:|--------:|-------:|
| Non-Free - Free | b0     | -14.8815 | 0.6508 | -22.8675 | 371.819 | 0      |
| Non-Free - Free | b_inc  |  -0.3116 | 0.1845 |  -1.6894 | 345.857 | 0.0921 |
| Non-Free - Free | b_abs  |   0.2357 | 0.2961 |   0.7961 | 290.106 | 0.4266 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |        t |   df |   p |
|:---------|:-------------|---------:|-----:|----:|
| Free     | 1 - 0        |  16.4582 |  192 |   0 |
| Free     | -1 - 0       | -20.8407 |  192 |   0 |
| Free     | 1 - -1       |  30.4669 |  192 |   0 |
| Non-Free | 1 - 0        |   8.9129 |  192 |   0 |
| Non-Free | -1 - 0       | -10.5515 |  192 |   0 |
| Non-Free | 1 - -1       |  19.5034 |  192 |   0 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |      p |   n |
|:---------|-------:|-------:|----:|
| Free     | 0.2492 | 0.0005 | 193 |
| Non-Free | 0.505  | 0      | 193 |

