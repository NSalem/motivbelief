# exp2 | AVG stats

## Response variable: `confSym`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Observed     | b0     | 65.6945 | 0.7298 | 21.5037 |   99 | 0      |
| Observed     | b_inc  |  1.0874 | 0.2178 |  4.9925 |   99 | 0      |
| Observed     | b_abs  |  1.0411 | 0.4922 |  2.115  |   99 | 0.0369 |
| Free         | b0     | 71.2326 | 1.1098 | 19.1313 |   96 | 0      |
| Free         | b_inc  |  2.3264 | 0.3012 |  7.7234 |   96 | 0      |
| Free         | b_abs  |  0.649  | 0.3092 |  2.099  |   96 | 0.0384 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |     p | test   |
|:----------------|:-------|--------:|-------:|--------:|--------:|------:|:-------|
| Observed - Free | b0     | -5.5381 | 1.3283 | -4.1693 | 166.747 | 0     | welch  |
| Observed - Free | b_inc  | -1.239  | 0.3717 | -3.3334 | 175.979 | 0.001 | welch  |
| Observed - Free | b_abs  |  0.3921 | 0.5813 |  0.6745 | 165.901 | 0.501 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  7.0223 |   96 | 0      |
| Free     | -1 - 0       | -3.8168 |   96 | 0.0002 |
| Free     | 1 - -1       |  7.7234 |   96 | 0      |
| Observed | 1 - 0        |  3.8888 |   99 | 0.0002 |
| Observed | -1 - 0       | -0.0874 |   99 | 0.9305 |
| Observed | 1 - -1       |  4.9925 |   99 | 0      |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |     p |   n |
|:---------|-------:|------:|----:|
| Free     | 0.0262 | 0.799 |  97 |
| Observed | 0.6729 | 0     | 100 |

