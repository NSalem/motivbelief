# exp3 | AVG stats

## Response variable: `conf`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Forced       | b0     | 66.0069 | 0.7019 | 22.805  |   97 | 0      |
| Forced       | b_inc  |  1.5615 | 0.3516 |  4.441  |   97 | 0      |
| Forced       | b_abs  |  0.5084 | 0.4477 |  1.1355 |   97 | 0.259  |
| Replayed     | b0     | 67.0522 | 0.8797 | 19.385  |   97 | 0      |
| Replayed     | b_inc  |  1.2878 | 0.2331 |  5.5243 |   97 | 0      |
| Replayed     | b_abs  |  0.1542 | 0.3288 |  0.469  |   97 | 0.6401 |


### Between-group tests (pairwise Welch)

| pair              | coef   |    mean |     se |       t |      df |      p | test   |
|:------------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Forced - Replayed | b0     | -1.0454 | 1.1254 | -0.9289 | 184.889 | 0.3542 | welch  |
| Forced - Replayed | b_inc  |  0.2736 | 0.4219 |  0.6486 | 168.475 | 0.5175 | welch  |
| Forced - Replayed | b_abs  |  0.3541 | 0.5555 |  0.6375 | 178.07  | 0.5246 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Replayed | 1 - 0        |  3.5078 |   97 | 0.0007 |
| Replayed | -1 - 0       | -2.8705 |   97 | 0.005  |
| Replayed | 1 - -1       |  5.5243 |   97 | 0      |
| Forced   | 1 - 0        |  3.7449 |   97 | 0.0003 |
| Forced   | -1 - 0       | -1.7991 |   97 | 0.0751 |
| Forced   | 1 - -1       |  4.441  |   97 | 0      |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |      p |   n |
|:---------|-------:|-------:|----:|
| Forced   | 0.2374 | 0.0186 |  98 |
| Replayed | 0.3313 | 0.0009 |  98 |

