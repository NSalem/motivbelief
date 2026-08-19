# exp1b | AVG stats

## Response variable: `rt_log`

### Model used for participant coefficients

- `y ~ 1 + incentive`
- Incentive levels: 0.1, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |        t |   df |      p |
|:-------------|:-------|--------:|-------:|---------:|-----:|-------:|
| Free         | b0     |  6.2782 | 0.0399 | 157.351  |   91 | 0      |
| Free         | b_inc  | -0.0015 | 0.0084 |  -0.1774 |   91 | 0.8596 |
| Observed     | b0     |  6.6129 | 0.0344 | 192.034  |   99 | 0      |
| Observed     | b_inc  | -0.0098 | 0.007  |  -1.3893 |   99 | 0.1679 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p | test   |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Observed - Free | b0     |  0.3346 | 0.0527 |  6.3491 | 183.482 | 0      | welch  |
| Observed - Free | b_inc  | -0.0083 | 0.011  | -0.7565 | 181.456 | 0.4503 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1.0 - 0.1    | -0.1774 |   91 | 0.8596 |
| Observed | 1.0 - 0.1    | -1.3893 |   99 | 0.1679 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

_None_

