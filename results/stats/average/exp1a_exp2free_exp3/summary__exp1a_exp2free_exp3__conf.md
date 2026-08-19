# exp1a_exp2free_exp3 | AVG stats

## Response variable: `conf`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 72.9046 | 0.9201 | 24.8941 |  192 | 0      |
| Free         | b_inc  |  3.0297 | 0.3281 |  9.2339 |  192 | 0      |
| Free         | b_abs  |  0.3226 | 0.3027 |  1.0657 |  192 | 0.2879 |
| Non-Free     | b0     | 66.0769 | 0.45   | 35.7245 |  295 | 0      |
| Non-Free     | b_inc  |  1.2795 | 0.1621 |  7.8908 |  295 | 0      |
| Non-Free     | b_abs  |  0.3607 | 0.2229 |  1.6179 |  295 | 0.1068 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p | test   |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Non-Free - Free | b0     | -6.8277 | 1.0242 | -6.6661 | 284.265 | 0      | welch  |
| Non-Free - Free | b_inc  | -1.7503 | 0.366  | -4.7823 | 286.125 | 0      | welch  |
| Non-Free - Free | b_abs  |  0.0381 | 0.3759 |  0.1014 | 383.402 | 0.9193 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  8.6558 |  192 | 0      |
| Free     | -1 - 0       | -5.4303 |  192 | 0      |
| Free     | 1 - -1       |  9.2339 |  192 | 0      |
| Non-Free | 1 - 0        |  5.8717 |  295 | 0      |
| Non-Free | -1 - 0       | -3.3785 |  295 | 0.0008 |
| Non-Free | 1 - -1       |  7.8908 |  295 | 0      |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |       r |      p |   n |
|:---------|--------:|-------:|----:|
| Free     | -0.0831 | 0.2504 | 193 |
| Non-Free |  0.3082 | 0      | 296 |

