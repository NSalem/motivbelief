# exp3 | AVG stats

## Response variable: `confSym`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Forced       | b0     | 66.0089 | 0.7014 | 22.8236 |   97 | 0      |
| Forced       | b_inc  |  1.3813 | 0.318  |  4.3438 |   97 | 0      |
| Forced       | b_abs  |  0.6865 | 0.4369 |  1.5713 |   97 | 0.1194 |
| Replayed     | b0     | 67.0522 | 0.8797 | 19.385  |   97 | 0      |
| Replayed     | b_inc  |  1.2298 | 0.2292 |  5.3656 |   97 | 0      |
| Replayed     | b_abs  |  0.2123 | 0.3255 |  0.652  |   97 | 0.5159 |


### Between-group tests (pairwise Welch)

| pair              | coef   |    mean |     se |       t |      df |      p |
|:------------------|:-------|--------:|-------:|--------:|--------:|-------:|
| Forced - Replayed | b0     | -1.0433 | 1.1251 | -0.9273 | 184.838 | 0.355  |
| Forced - Replayed | b_inc  |  0.1515 | 0.392  |  0.3864 | 176.366 | 0.6996 |
| Forced - Replayed | b_abs  |  0.4742 | 0.5448 |  0.8704 | 179.332 | 0.3852 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Replayed | 1 - 0        |  3.5078 |   97 | 0.0007 |
| Replayed | -1 - 0       | -2.6449 |   97 | 0.0095 |
| Replayed | 1 - -1       |  5.3656 |   97 | 0      |
| Forced   | 1 - 0        |  3.7432 |   97 | 0.0003 |
| Forced   | -1 - 0       | -1.3158 |   97 | 0.1913 |
| Forced   | 1 - -1       |  4.3438 |   97 | 0      |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |      p |   n |
|:---------|-------:|-------:|----:|
| Forced   | 0.3077 | 0.0021 |  98 |
| Replayed | 0.3379 | 0.0007 |  98 |

