# sim_act | AVG stats

## Response variable: `confSym`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 75.7339 | 0.9811 | 26.2283 |  192 | 0      |
| Free         | b_inc  |  2.0215 | 0.249  |  8.1181 |  192 | 0      |
| Free         | b_abs  | -0.064  | 0.2344 | -0.2729 |  192 | 0.7852 |
| Non-Free     | b0     | 67.0106 | 1.0006 | 17.0008 |  192 | 0      |
| Non-Free     | b_inc  |  1.3616 | 0.2515 |  5.413  |  192 | 0      |
| Non-Free     | b_abs  |  0.0224 | 0.3056 |  0.0732 |  192 | 0.9417 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |        t |   df |      p | test   |
|:----------------|:-------|--------:|-------:|---------:|-----:|-------:|:-------|
| Non-Free - Free | b0     | -8.7233 | 0.4556 | -19.1451 |  192 | 0      | paired |
| Non-Free - Free | b_inc  | -0.66   | 0.1696 |  -3.892  |  192 | 0.0001 | paired |
| Non-Free - Free | b_abs  |  0.0863 | 0.1753 |   0.4925 |  192 | 0.6229 | paired |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  6.8013 |  192 | 0      |
| Free     | -1 - 0       | -5.3664 |  192 | 0      |
| Free     | 1 - -1       |  8.1181 |  192 | 0      |
| Non-Free | 1 - 0        |  4.2371 |  192 | 0      |
| Non-Free | -1 - 0       | -2.9456 |  192 | 0.0036 |
| Non-Free | 1 - -1       |  5.413  |  192 | 0      |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |       r |      p |   n |
|:---------|--------:|-------:|----:|
| Free     | -0.0633 | 0.3817 | 193 |
| Non-Free |  0.203  | 0.0046 | 193 |

