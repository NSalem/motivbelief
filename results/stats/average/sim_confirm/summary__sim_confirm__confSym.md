# sim_confirm | AVG stats

## Response variable: `confSym`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 75.757  | 0.9814 | 26.2453 |  192 | 0      |
| Free         | b_inc  |  2.0305 | 0.2483 |  8.1766 |  192 | 0      |
| Free         | b_abs  | -0.0788 | 0.2356 | -0.3343 |  192 | 0.7385 |
| Non-Free     | b0     | 63.3953 | 0.6119 | 21.8904 |  192 | 0      |
| Non-Free     | b_inc  |  0.9227 | 0.1534 |  6.0133 |  192 | 0      |
| Non-Free     | b_abs  |  0.0722 | 0.2268 |  0.3184 |  192 | 0.7505 |


### Between-group tests (pairwise Welch)

| pair            | coef   |     mean |     se |        t |   df |      p | test   |
|:----------------|:-------|---------:|-------:|---------:|-----:|-------:|:-------|
| Non-Free - Free | b0     | -12.3617 | 0.4898 | -25.2362 |  192 | 0      | paired |
| Non-Free - Free | b_inc  |  -1.1079 | 0.1576 |  -7.0304 |  192 | 0      | paired |
| Non-Free - Free | b_abs  |   0.151  | 0.1881 |   0.8025 |  192 | 0.4232 | paired |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  6.773  |  192 | 0      |
| Free     | -1 - 0       | -5.4231 |  192 | 0      |
| Free     | 1 - -1       |  8.1766 |  192 | 0      |
| Non-Free | 1 - 0        |  3.8234 |  192 | 0.0002 |
| Non-Free | -1 - 0       | -2.9654 |  192 | 0.0034 |
| Non-Free | 1 - -1       |  6.0133 |  192 | 0      |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |       r |      p |   n |
|:---------|--------:|-------:|----:|
| Free     | -0.0551 | 0.4464 | 193 |
| Non-Free |  0.3738 | 0      | 193 |

