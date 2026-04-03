# sim_intent | AVG stats

## Response variable: `confSym`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 78.6741 | 0.4881 | 58.7423 |  192 | 0      |
| Free         | b_inc  |  3.1907 | 0.0956 | 33.3676 |  192 | 0      |
| Free         | b_abs  | -0.2878 | 0.1335 | -2.1552 |  192 | 0.0324 |
| Non-Free     | b0     | 63.5638 | 0.3914 | 34.6535 |  192 | 0      |
| Non-Free     | b_inc  |  0.919  | 0.157  |  5.8536 |  192 | 0      |
| Non-Free     | b_abs  | -0.1923 | 0.2396 | -0.8029 |  192 | 0.423  |


### Between-group tests (pairwise Welch)

| pair            | coef   |     mean |     se |        t |      df |      p |
|:----------------|:-------|---------:|-------:|---------:|--------:|-------:|
| Non-Free - Free | b0     | -15.1103 | 0.6257 | -24.1502 | 366.684 | 0      |
| Non-Free - Free | b_inc  |  -2.2717 | 0.1838 | -12.3581 | 317.222 | 0      |
| Non-Free - Free | b_abs  |   0.0954 | 0.2743 |   0.348  | 300.793 | 0.7281 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |        t |   df |      p |
|:---------|:-------------|---------:|-----:|-------:|
| Free     | 1 - 0        |  19.6965 |  192 | 0      |
| Free     | -1 - 0       | -19.377  |  192 | 0      |
| Free     | 1 - -1       |  33.3676 |  192 | 0      |
| Non-Free | 1 - 0        |   2.4177 |  192 | 0.0166 |
| Non-Free | -1 - 0       |  -4.0922 |  192 | 0.0001 |
| Non-Free | 1 - -1       |   5.8536 |  192 | 0      |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.3283 |   0 | 193 |
| Non-Free | 0.4012 |   0 | 193 |

