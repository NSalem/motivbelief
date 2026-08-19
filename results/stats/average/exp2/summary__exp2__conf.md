# exp2 | AVG stats

## Response variable: `conf`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Observed     | b0     | 65.3069 | 0.8087 | 18.9272 |   99 | 0      |
| Observed     | b_inc  |  1.2097 | 0.2319 |  5.2162 |   99 | 0      |
| Observed     | b_abs  |  1.3005 | 0.6838 |  1.9018 |   99 | 0.0601 |
| Free         | b0     | 71.2326 | 1.1098 | 19.1313 |   96 | 0      |
| Free         | b_inc  |  2.5481 | 0.3772 |  6.7551 |   96 | 0      |
| Free         | b_abs  |  0.4273 | 0.2937 |  1.4551 |   96 | 0.1489 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p | test   |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Observed - Free | b0     | -5.9257 | 1.3732 | -4.3151 | 176.705 | 0      | welch  |
| Observed - Free | b_inc  | -1.3384 | 0.4428 | -3.0225 | 160.109 | 0.0029 | welch  |
| Observed - Free | b_abs  |  0.8731 | 0.7442 |  1.1732 | 134.185 | 0.2428 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  7.0223 |   96 | 0      |
| Free     | -1 - 0       | -4.0255 |   96 | 0.0001 |
| Free     | 1 - -1       |  6.7551 |   96 | 0      |
| Observed | 1 - 0        |  3.4907 |   99 | 0.0007 |
| Observed | -1 - 0       |  0.1252 |   99 | 0.9007 |
| Observed | 1 - -1       |  5.2162 |   99 | 0      |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |       r |      p |   n |
|:---------|--------:|-------:|----:|
| Free     | -0.251  | 0.0131 |  97 |
| Observed |  0.7937 | 0      | 100 |

