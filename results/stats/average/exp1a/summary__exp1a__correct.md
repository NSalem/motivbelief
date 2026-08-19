# exp1a | AVG stats

## Response variable: `correct`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 74.5894 | 1.0316 | 23.8367 |   95 | 0      |
| Free         | b_inc  | -0.3541 | 0.2884 | -1.2278 |   95 | 0.2226 |
| Free         | b_abs  |  0.5254 | 0.5856 |  0.8971 |   95 | 0.3719 |
| Observed     | b0     | 75.1946 | 0.4796 | 52.5339 |   99 | 0      |
| Observed     | b_inc  |  0.0068 | 0.3397 |  0.0199 |   99 | 0.9842 |
| Observed     | b_abs  | -0.9863 | 0.616  | -1.6012 |   99 | 0.1125 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p | test   |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Observed - Free | b0     |  0.6052 | 1.1376 |  0.532  | 134.476 | 0.5956 | welch  |
| Observed - Free | b_inc  |  0.3608 | 0.4456 |  0.8098 | 190.184 | 0.4191 | welch  |
| Observed - Free | b_abs  | -1.5117 | 0.8499 | -1.7786 | 193.827 | 0.0769 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  0.248  |   95 | 0.8047 |
| Free     | -1 - 0       |  1.4361 |   95 | 0.1542 |
| Free     | 1 - -1       | -1.2278 |   95 | 0.2226 |
| Observed | 1 - 0        | -1.3735 |   99 | 0.1727 |
| Observed | -1 - 0       | -1.4318 |   99 | 0.1553 |
| Observed | 1 - -1       |  0.0199 |   99 | 0.9842 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.6141 |   0 |  96 |
| Observed | 0.5338 |   0 | 100 |

