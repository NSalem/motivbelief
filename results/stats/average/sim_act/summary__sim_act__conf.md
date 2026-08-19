# sim_act | AVG stats

## Response variable: `conf`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 75.3843 | 1.0275 | 24.7052 |  192 | 0      |
| Free         | b_inc  |  2.6321 | 0.3621 |  7.2684 |  192 | 0      |
| Free         | b_abs  | -0.5233 | 0.2367 | -2.2108 |  192 | 0.0282 |
| Non-Free     | b0     | 65.6025 | 1.1137 | 14.0095 |  192 | 0      |
| Non-Free     | b_inc  |  2.6748 | 0.3904 |  6.8513 |  192 | 0      |
| Non-Free     | b_abs  | -0.7886 | 0.2783 | -2.8331 |  192 | 0.0051 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |        t |   df |      p | test   |
|:----------------|:-------|--------:|-------:|---------:|-----:|-------:|:-------|
| Non-Free - Free | b0     | -9.7818 | 0.3981 | -24.5693 |  192 | 0      | paired |
| Non-Free - Free | b_inc  |  0.0428 | 0.087  |   0.4917 |  192 | 0.6235 | paired |
| Non-Free - Free | b_abs  | -0.2653 | 0.1235 |  -2.1485 |  192 | 0.0329 | paired |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |   p |
|:---------|:-------------|--------:|-----:|----:|
| Free     | 1 - 0        |  7.2584 |  192 |   0 |
| Free     | -1 - 0       | -5.8604 |  192 |   0 |
| Free     | 1 - -1       |  7.2684 |  192 |   0 |
| Non-Free | 1 - 0        |  5.7755 |  192 |   0 |
| Non-Free | -1 - 0       | -5.8282 |  192 |   0 |
| Non-Free | 1 - -1       |  6.8513 |  192 |   0 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |       r |   p |   n |
|:---------|--------:|----:|----:|
| Free     | -0.4802 |   0 | 193 |
| Non-Free | -0.3862 |   0 | 193 |

