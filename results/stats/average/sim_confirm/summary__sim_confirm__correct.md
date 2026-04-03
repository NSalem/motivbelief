# sim_confirm | AVG stats

## Response variable: `correct`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 73.7953 | 0.6899 | 34.4927 |  192 | 0      |
| Free         | b_inc  | -0.3918 | 0.2308 | -1.6981 |  192 | 0.0911 |
| Free         | b_abs  | -0.1652 | 0.3755 | -0.4399 |  192 | 0.6605 |
| Non-Free     | b0     | 74.6762 | 0.3254 | 75.835  |  192 | 0      |
| Non-Free     | b_inc  | -0.0518 | 0.2211 | -0.2343 |  192 | 0.815  |
| Non-Free     | b_abs  |  0.272  | 0.3958 |  0.6873 |  192 | 0.4927 |


### Between-group tests (pairwise Welch)

| pair            | coef   |   mean |     se |      t |      df |      p |
|:----------------|:-------|-------:|-------:|-------:|--------:|-------:|
| Non-Free - Free | b0     | 0.8808 | 0.7628 | 1.1548 | 273.402 | 0.2492 |
| Non-Free - Free | b_inc  | 0.34   | 0.3196 | 1.0639 | 383.305 | 0.288  |
| Non-Free - Free | b_abs  | 0.4372 | 0.5455 | 0.8014 | 382.939 | 0.4234 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        | -1.313  |  192 | 0.1907 |
| Free     | -1 - 0       |  0.4964 |  192 | 0.6201 |
| Free     | 1 - -1       | -1.6981 |  192 | 0.0911 |
| Non-Free | 1 - 0        |  0.5077 |  192 | 0.6123 |
| Non-Free | -1 - 0       |  0.6859 |  192 | 0.4936 |
| Non-Free | 1 - -1       | -0.2343 |  192 | 0.815  |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.4529 |   0 | 193 |
| Non-Free | 0.5261 |   0 | 193 |

