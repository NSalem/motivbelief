# sim_intent | AVG stats

## Response variable: `calib`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |     mean |     se |        t |   df |      p |
|:-------------|:-------|---------:|-------:|---------:|-----:|-------:|
| Free         | b0     |   0.9287 | 1.1087 |   0.8377 |  192 | 0.4033 |
| Free         | b_inc  |   2.9148 | 0.4046 |   7.2034 |  192 | 0      |
| Free         | b_abs  |  -1.4546 | 0.4591 |  -3.1687 |  192 | 0.0018 |
| Non-Free     | b0     | -12.3821 | 0.4859 | -25.4816 |  192 | 0      |
| Non-Free     | b_inc  |   0.9009 | 0.2219 |   4.0605 |  192 | 0.0001 |
| Non-Free     | b_abs  |  -0.248  | 0.328  |  -0.7562 |  192 | 0.4504 |


### Between-group tests (pairwise Welch)

| pair            | coef   |     mean |     se |        t |   df |      p | test   |
|:----------------|:-------|---------:|-------:|---------:|-----:|-------:|:-------|
| Non-Free - Free | b0     | -13.3109 | 1.0214 | -13.0319 |  192 | 0      | paired |
| Non-Free - Free | b_inc  |  -2.0139 | 0.3839 |  -5.2454 |  192 | 0      | paired |
| Non-Free - Free | b_abs  |   1.2066 | 0.5345 |   2.2572 |  192 | 0.0251 | paired |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  2.7598 |  192 | 0.0063 |
| Free     | -1 - 0       | -6.3803 |  192 | 0      |
| Free     | 1 - -1       |  7.2034 |  192 | 0      |
| Non-Free | 1 - 0        |  1.7573 |  192 | 0.0805 |
| Non-Free | -1 - 0       | -2.742  |  192 | 0.0067 |
| Non-Free | 1 - -1       |  4.0605 |  192 | 0.0001 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |      p |   n |
|:---------|-------:|-------:|----:|
| Free     | 0.1297 | 0.0722 | 193 |
| Non-Free | 0.3748 | 0      | 193 |

