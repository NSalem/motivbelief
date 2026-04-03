# sim_act | AVG stats

## Response variable: `calib`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |     mean |     se |        t |   df |      p |
|:-------------|:-------|---------:|-------:|---------:|-----:|-------:|
| Free         | b0     |   4.4536 | 0.6391 |   6.9689 |  192 | 0      |
| Free         | b_inc  |   3.3495 | 0.2343 |  14.2955 |  192 | 0      |
| Free         | b_abs  |  -0.3118 | 0.3507 |  -0.8891 |  192 | 0.3751 |
| Non-Free     | b0     | -11.0928 | 0.4823 | -22.9995 |  192 | 0      |
| Non-Free     | b_inc  |   3.103  | 0.2346 |  13.2291 |  192 | 0      |
| Non-Free     | b_abs  |  -0.2215 | 0.3896 |  -0.5687 |  192 | 0.5702 |


### Between-group tests (pairwise Welch)

| pair            | coef   |     mean |     se |        t |      df |      p |
|:----------------|:-------|---------:|-------:|---------:|--------:|-------:|
| Non-Free - Free | b0     | -15.5464 | 0.8006 | -19.4174 | 357.141 | 0      |
| Non-Free - Free | b_inc  |  -0.2466 | 0.3315 |  -0.7437 | 384     | 0.4575 |
| Non-Free - Free | b_abs  |   0.0902 | 0.5242 |   0.1721 | 379.828 | 0.8634 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |   p |
|:---------|:-------------|--------:|-----:|----:|
| Free     | 1 - 0        |  7.1318 |  192 |   0 |
| Free     | -1 - 0       | -8.7693 |  192 |   0 |
| Free     | 1 - -1       | 14.2955 |  192 |   0 |
| Non-Free | 1 - 0        |  6.2281 |  192 |   0 |
| Non-Free | -1 - 0       | -7.4427 |  192 |   0 |
| Non-Free | 1 - -1       | 13.2291 |  192 |   0 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.3828 |   0 | 193 |
| Non-Free | 0.4682 |   0 | 193 |

