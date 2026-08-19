# sim_intent | AVG stats

## Response variable: `confSym`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 75.7581 | 0.982  | 26.231  |  192 | 0      |
| Free         | b_inc  |  2.0209 | 0.2488 |  8.1221 |  192 | 0      |
| Free         | b_abs  | -0.0834 | 0.2352 | -0.3545 |  192 | 0.7233 |
| Non-Free     | b0     | 62.3642 | 0.4268 | 28.9723 |  192 | 0      |
| Non-Free     | b_inc  |  0.6392 | 0.1189 |  5.3758 |  192 | 0      |
| Non-Free     | b_abs  | -0.2046 | 0.1696 | -1.2065 |  192 | 0.2291 |


### Between-group tests (pairwise Welch)

| pair            | coef   |     mean |     se |        t |   df |      p | test   |
|:----------------|:-------|---------:|-------:|---------:|-----:|-------:|:-------|
| Non-Free - Free | b0     | -13.3939 | 0.6881 | -19.4646 |  192 | 0      | paired |
| Non-Free - Free | b_inc  |  -1.3817 | 0.2047 |  -6.7507 |  192 | 0      | paired |
| Non-Free - Free | b_abs  |  -0.1212 | 0.2318 |  -0.5231 |  192 | 0.6015 | paired |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  6.699  |  192 | 0      |
| Free     | -1 - 0       | -5.4183 |  192 | 0      |
| Free     | 1 - -1       |  8.1221 |  192 | 0      |
| Non-Free | 1 - 0        |  2.1552 |  192 | 0.0324 |
| Non-Free | -1 - 0       | -3.9714 |  192 | 0.0001 |
| Non-Free | 1 - -1       |  5.3758 |  192 | 0      |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |       r |      p |   n |
|:---------|--------:|-------:|----:|
| Free     | -0.0586 | 0.4186 | 193 |
| Non-Free |  0.3414 | 0      | 193 |

