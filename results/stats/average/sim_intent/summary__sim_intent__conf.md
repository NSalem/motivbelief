# sim_intent | AVG stats

## Response variable: `conf`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 78.4151 | 0.5615 | 50.606  |  192 | 0      |
| Free         | b_inc  |  3.1257 | 0.1062 | 29.4272 |  192 | 0      |
| Free         | b_abs  | -0.2438 | 0.134  | -1.8195 |  192 | 0.0704 |
| Non-Free     | b0     | 63.3708 | 0.4246 | 31.4914 |  192 | 0      |
| Non-Free     | b_inc  |  0.9491 | 0.1566 |  6.0613 |  192 | 0      |
| Non-Free     | b_abs  | -0.219  | 0.2399 | -0.9129 |  192 | 0.3625 |


### Between-group tests (pairwise Welch)

| pair            | coef   |     mean |     se |        t |      df |      p |
|:----------------|:-------|---------:|-------:|---------:|--------:|-------:|
| Non-Free - Free | b0     | -15.0443 | 0.704  | -21.3711 | 357.469 | 0      |
| Non-Free - Free | b_inc  |  -2.1766 | 0.1892 | -11.5037 | 337.825 | 0      |
| Non-Free - Free | b_abs  |   0.0248 | 0.2748 |   0.0902 | 301.158 | 0.9282 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |        t |   df |      p |
|:---------|:-------------|---------:|-----:|-------:|
| Free     | 1 - 0        |  19.2752 |  192 | 0      |
| Free     | -1 - 0       | -17.7307 |  192 | 0      |
| Free     | 1 - -1       |  29.4272 |  192 | 0      |
| Non-Free | 1 - 0        |   2.4196 |  192 | 0.0165 |
| Non-Free | -1 - 0       |  -4.3206 |  192 | 0      |
| Non-Free | 1 - -1       |   6.0613 |  192 | 0      |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |     p |   n |
|:---------|-------:|------:|----:|
| Free     | 0.2347 | 0.001 | 193 |
| Non-Free | 0.4049 | 0     | 193 |

