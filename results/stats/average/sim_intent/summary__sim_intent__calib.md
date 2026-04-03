# sim_intent | AVG stats

## Response variable: `calib`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |     mean |     se |        t |   df |      p |
|:-------------|:-------|---------:|-------:|---------:|-----:|-------:|
| Free         | b0     |   4.5162 | 0.6666 |   6.7746 |  192 | 0      |
| Free         | b_inc  |   2.9702 | 0.2295 |  12.9449 |  192 | 0      |
| Free         | b_abs  |  -0.3733 | 0.3923 |  -0.9516 |  192 | 0.3425 |
| Non-Free     | b0     | -10.7224 | 0.452  | -23.7216 |  192 | 0      |
| Non-Free     | b_inc  |   1.0657 | 0.2419 |   4.4048 |  192 | 0      |
| Non-Free     | b_abs  |  -0.5752 | 0.3783 |  -1.5204 |  192 | 0.13   |


### Between-group tests (pairwise Welch)

| pair            | coef   |     mean |     se |        t |      df |      p |
|:----------------|:-------|---------:|-------:|---------:|--------:|-------:|
| Non-Free - Free | b0     | -15.2386 | 0.8054 | -18.9199 | 337.74  | 0      |
| Non-Free - Free | b_inc  |  -1.9046 | 0.3334 |  -5.7119 | 382.928 | 0      |
| Non-Free - Free | b_abs  |  -0.2019 | 0.545  |  -0.3705 | 383.496 | 0.7112 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  5.6714 |  192 | 0      |
| Free     | -1 - 0       | -7.4134 |  192 | 0      |
| Free     | 1 - -1       | 12.9449 |  192 | 0      |
| Non-Free | 1 - 0        |  1.0697 |  192 | 0.2861 |
| Non-Free | -1 - 0       | -3.7341 |  192 | 0.0002 |
| Non-Free | 1 - -1       |  4.4048 |  192 | 0      |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.4902 |   0 | 193 |
| Non-Free | 0.4199 |   0 | 193 |

