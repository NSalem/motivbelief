# exp2 | AVG stats

## Response variable: `correct`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Observed     | b0     | 74.2315 | 0.5228 | 46.3488 |   99 | 0      |
| Observed     | b_inc  |  0.5592 | 0.3414 |  1.638  |   99 | 0.1046 |
| Observed     | b_abs  |  0.3581 | 0.546  |  0.6559 |   99 | 0.5134 |
| Free         | b0     | 74.3739 | 0.9199 | 26.4962 |   96 | 0      |
| Free         | b_inc  | -0.2068 | 0.3214 | -0.6434 |   96 | 0.5215 |
| Free         | b_abs  |  1.2866 | 0.5222 |  2.464  |   96 | 0.0155 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|
| Observed - Free | b0     | -0.1424 | 1.0581 | -0.1346 | 152.594 | 0.8931 |
| Observed - Free | b_inc  |  0.7659 | 0.4688 |  1.6337 | 194.606 | 0.1039 |
| Observed - Free | b_abs  | -0.9285 | 0.7555 | -1.229  | 194.833 | 0.2205 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  1.723  |   96 | 0.0881 |
| Free     | -1 - 0       |  2.4922 |   96 | 0.0144 |
| Free     | 1 - -1       | -0.6434 |   96 | 0.5215 |
| Observed | 1 - 0        |  1.4269 |   99 | 0.1567 |
| Observed | -1 - 0       | -0.3117 |   99 | 0.7559 |
| Observed | 1 - -1       |  1.638  |   99 | 0.1046 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.451  |   0 |  97 |
| Observed | 0.4379 |   0 | 100 |

