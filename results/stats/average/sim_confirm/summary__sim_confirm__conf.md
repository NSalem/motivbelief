# sim_confirm | AVG stats

## Response variable: `conf`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 75.409  | 1.0276 | 24.7278 |  192 | 0      |
| Free         | b_inc  |  2.6444 | 0.3622 |  7.3006 |  192 | 0      |
| Free         | b_abs  | -0.5459 | 0.2376 | -2.2976 |  192 | 0.0227 |
| Non-Free     | b0     | 62.899  | 0.6651 | 19.3929 |  192 | 0      |
| Non-Free     | b_inc  |  1.6223 | 0.2438 |  6.6541 |  192 | 0      |
| Non-Free     | b_abs  | -0.4223 | 0.2192 | -1.9262 |  192 | 0.0556 |


### Between-group tests (pairwise Welch)

| pair            | coef   |     mean |     se |        t |   df |      p | test   |
|:----------------|:-------|---------:|-------:|---------:|-----:|-------:|:-------|
| Non-Free - Free | b0     | -12.51   | 0.4755 | -26.3066 |  192 | 0      | paired |
| Non-Free - Free | b_inc  |  -1.022  | 0.1531 |  -6.6773 |  192 | 0      | paired |
| Non-Free - Free | b_abs  |   0.1236 | 0.1815 |   0.6809 |  192 | 0.4967 | paired |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |   p |
|:---------|:-------------|--------:|-----:|----:|
| Free     | 1 - 0        |  7.1912 |  192 |   0 |
| Free     | -1 - 0       | -5.9227 |  192 |   0 |
| Free     | 1 - -1       |  7.3006 |  192 |   0 |
| Non-Free | 1 - 0        |  4.6567 |  192 |   0 |
| Non-Free | -1 - 0       | -5.3041 |  192 |   0 |
| Non-Free | 1 - -1       |  6.6541 |  192 |   0 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |       r |      p |   n |
|:---------|--------:|-------:|----:|
| Free     | -0.4756 | 0      | 193 |
| Non-Free | -0.1146 | 0.1126 | 193 |

