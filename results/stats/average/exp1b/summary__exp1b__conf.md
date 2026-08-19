# exp1b | AVG stats

## Response variable: `conf`

### Model used for participant coefficients

- `y ~ 1 + incentive`
- Incentive levels: 0.1, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 75.9158 | 1.3649 | 18.9874 |   91 | 0      |
| Free         | b_inc  |  3.1792 | 0.7208 |  4.4106 |   91 | 0      |
| Observed     | b0     | 63.923  | 0.7578 | 18.3726 |   99 | 0      |
| Observed     | b_inc  |  0.9935 | 0.5708 |  1.7406 |   99 | 0.0849 |


### Between-group tests (pairwise Welch)

| pair            | coef   |     mean |     se |       t |      df |      p | test   |
|:----------------|:-------|---------:|-------:|--------:|--------:|-------:|:-------|
| Observed - Free | b0     | -11.9928 | 1.5612 | -7.682  | 143.24  | 0      | welch  |
| Observed - Free | b_inc  |  -2.1857 | 0.9194 | -2.3772 | 176.952 | 0.0185 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |      t |   df |      p |
|:---------|:-------------|-------:|-----:|-------:|
| Free     | 1.0 - 0.1    | 4.4106 |   91 | 0      |
| Observed | 1.0 - 0.1    | 1.7406 |   99 | 0.0849 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

_None_

