# exp1a_exp2free_exp3 | AVG stats

## Response variable: `calib`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |        t |   df |      p |
|:-------------|:-------|--------:|-------:|---------:|-----:|-------:|
| Free         | b0     | -1.5765 | 0.9844 |  -1.6014 |  192 | 0.1109 |
| Free         | b_inc  |  3.3098 | 0.3738 |   8.8553 |  192 | 0      |
| Free         | b_abs  | -0.5854 | 0.4882 |  -1.1992 |  192 | 0.2319 |
| Non-Free     | b0     | -6.9301 | 0.5185 | -13.3649 |  295 | 0      |
| Non-Free     | b_inc  |  1.097  | 0.2063 |   5.3186 |  295 | 0      |
| Non-Free     | b_abs  |  0.0846 | 0.3443 |   0.2458 |  295 | 0.806  |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p | test   |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Non-Free - Free | b0     | -5.3536 | 1.1126 | -4.8117 | 298.373 | 0      | welch  |
| Non-Free - Free | b_inc  | -2.2128 | 0.4269 | -5.1834 | 308.144 | 0      | welch  |
| Non-Free - Free | b_abs  |  0.67   | 0.5974 |  1.1217 | 370.791 | 0.2627 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  4.6704 |  192 | 0      |
| Free     | -1 - 0       | -6.0411 |  192 | 0      |
| Free     | 1 - -1       |  8.8553 |  192 | 0      |
| Non-Free | 1 - 0        |  2.8843 |  295 | 0.0042 |
| Non-Free | -1 - 0       | -2.5772 |  295 | 0.0104 |
| Non-Free | 1 - -1       |  5.3186 |  295 | 0      |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |      p |   n |
|:---------|-------:|-------:|----:|
| Free     | 0.2622 | 0.0002 | 193 |
| Non-Free | 0.4722 | 0      | 296 |

