# exp1b | AVG stats

## Response variable: `correct`

### Model used for participant coefficients

- `y ~ 1 + incentive`
- Incentive levels: 0.1, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 75.7839 | 1.1063 | 23.3055 |   91 | 0      |
| Free         | b_inc  |  0.0781 | 0.5761 |  0.1355 |   91 | 0.8925 |
| Observed     | b0     | 75.3967 | 0.4806 | 52.8426 |   99 | 0      |
| Observed     | b_inc  | -0.9589 | 0.7039 | -1.3622 |   99 | 0.1762 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|
| Observed - Free | b0     | -0.3872 | 1.2062 | -0.321  | 124.511 | 0.7488 |
| Observed - Free | b_inc  | -1.0369 | 0.9096 | -1.1399 | 185.5   | 0.2558 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1.0 - 0.1    |  0.1355 |   91 | 0.8925 |
| Observed | 1.0 - 0.1    | -1.3622 |   99 | 0.1762 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

_None_

