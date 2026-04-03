# sim_act | AVG stats

## Response variable: `conf`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 78.4044 | 0.5708 | 49.7645 |  192 | 0      |
| Free         | b_inc  |  3.2265 | 0.1099 | 29.365  |  192 | 0      |
| Free         | b_abs  | -0.396  | 0.1377 | -2.8758 |  192 | 0.0045 |
| Non-Free     | b0     | 63.5899 | 0.4474 | 30.3737 |  192 | 0      |
| Non-Free     | b_inc  |  2.9669 | 0.1655 | 17.9292 |  192 | 0      |
| Non-Free     | b_abs  | -0.2928 | 0.26   | -1.126  |  192 | 0.2616 |


### Between-group tests (pairwise Welch)

| pair            | coef   |     mean |     se |        t |      df |      p |
|:----------------|:-------|---------:|-------:|---------:|--------:|-------:|
| Non-Free - Free | b0     | -14.8145 | 0.7252 | -20.427  | 363.285 | 0      |
| Non-Free - Free | b_inc  |  -0.2595 | 0.1986 |  -1.3065 | 333.741 | 0.1923 |
| Non-Free - Free | b_abs  |   0.1032 | 0.2942 |   0.3507 | 291.824 | 0.7261 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |        t |   df |   p |
|:---------|:-------------|---------:|-----:|----:|
| Free     | 1 - 0        |  16.3585 |  192 |   0 |
| Free     | -1 - 0       | -20.2109 |  192 |   0 |
| Free     | 1 - -1       |  29.365  |  192 |   0 |
| Non-Free | 1 - 0        |   8.5207 |  192 |   0 |
| Non-Free | -1 - 0       | -10.7763 |  192 |   0 |
| Non-Free | 1 - -1       |  17.9292 |  192 |   0 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |      p |   n |
|:---------|-------:|-------:|----:|
| Free     | 0.2221 | 0.0019 | 193 |
| Non-Free | 0.4238 | 0      | 193 |

