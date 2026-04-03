# sim_confirm | AVG stats

## Response variable: `conf`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 78.2375 | 0.574  | 49.1937 |  192 | 0      |
| Free         | b_inc  |  3.0925 | 0.1157 | 26.7225 |  192 | 0      |
| Free         | b_abs  | -0.1696 | 0.1423 | -1.1923 |  192 | 0.2346 |
| Non-Free     | b0     | 63.3169 | 0.4326 | 30.7863 |  192 | 0      |
| Non-Free     | b_inc  |  2.1234 | 0.1513 | 14.0337 |  192 | 0      |
| Non-Free     | b_abs  |  0.09   | 0.2532 |  0.3556 |  192 | 0.7226 |


### Between-group tests (pairwise Welch)

| pair            | coef   |     mean |     se |        t |      df |     p |
|:----------------|:-------|---------:|-------:|---------:|--------:|------:|
| Non-Free - Free | b0     | -14.9206 | 0.7187 | -20.7593 | 356.891 | 0     |
| Non-Free - Free | b_inc  |  -0.9691 | 0.1905 |  -5.0877 | 359.366 | 0     |
| Non-Free - Free | b_abs  |   0.2596 | 0.2904 |   0.8941 | 302.267 | 0.372 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |        t |   df |   p |
|:---------|:-------------|---------:|-----:|----:|
| Free     | 1 - 0        |  16.015  |  192 |   0 |
| Free     | -1 - 0       | -17.7027 |  192 |   0 |
| Free     | 1 - -1       |  26.7225 |  192 |   0 |
| Non-Free | 1 - 0        |   7.7352 |  192 |   0 |
| Non-Free | -1 - 0       |  -6.7002 |  192 |   0 |
| Non-Free | 1 - -1       |  14.0337 |  192 |   0 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |      p |   n |
|:---------|-------:|-------:|----:|
| Free     | 0.2036 | 0.0045 | 193 |
| Non-Free | 0.4745 | 0      | 193 |

