# exp1a_exp3 | AVG stats

## Response variable: `confSym`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 75.1494 | 1.3533 | 18.5836 |   95 | 0      |
| Free         | b_inc  |  2.8369 | 0.4522 |  6.2733 |   95 | 0      |
| Free         | b_abs  |  0.6416 | 0.5253 |  1.2215 |   95 | 0.2249 |
| Observed     | b0     | 65.2378 | 0.7335 | 20.7745 |   99 | 0      |
| Observed     | b_inc  |  0.9864 | 0.2432 |  4.0551 |   99 | 0.0001 |
| Observed     | b_abs  |  0.3855 | 0.3711 |  1.0389 |   99 | 0.3014 |
| Forced       | b0     | 66.0089 | 0.7014 | 22.8236 |   97 | 0      |
| Forced       | b_inc  |  1.3813 | 0.318  |  4.3438 |   97 | 0      |
| Forced       | b_abs  |  0.6865 | 0.4369 |  1.5713 |   97 | 0.1194 |
| Replayed     | b0     | 67.0522 | 0.8797 | 19.385  |   97 | 0      |
| Replayed     | b_inc  |  1.2298 | 0.2292 |  5.3656 |   97 | 0      |
| Replayed     | b_abs  |  0.2123 | 0.3255 |  0.652  |   97 | 0.5159 |


### Between-group tests (pairwise Welch)

| pair                | coef   |    mean |     se |       t |      df |      p | test   |
|:--------------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Replayed - Free     | b0     | -8.0972 | 1.6141 | -5.0166 | 163.628 | 0      | welch  |
| Replayed - Free     | b_inc  | -1.6071 | 0.507  | -3.1699 | 140.966 | 0.0019 | welch  |
| Replayed - Free     | b_abs  | -0.4294 | 0.618  | -0.6948 | 159.011 | 0.4882 | welch  |
| Forced - Free       | b0     | -9.1405 | 1.5243 | -5.9966 | 142.804 | 0      | welch  |
| Forced - Free       | b_inc  | -1.4556 | 0.5528 | -2.633  | 171.185 | 0.0092 | welch  |
| Forced - Free       | b_abs  |  0.0448 | 0.6832 |  0.0656 | 185.128 | 0.9477 | welch  |
| Observed - Free     | b0     | -9.9116 | 1.5393 | -6.439  | 146.852 | 0      | welch  |
| Observed - Free     | b_inc  | -1.8505 | 0.5135 | -3.6039 | 146.182 | 0.0004 | welch  |
| Observed - Free     | b_abs  | -0.2561 | 0.6432 | -0.3982 | 172.299 | 0.6909 | welch  |
| Forced - Replayed   | b0     | -1.0433 | 1.1251 | -0.9273 | 184.838 | 0.355  | welch  |
| Forced - Replayed   | b_inc  |  0.1515 | 0.392  |  0.3864 | 176.366 | 0.6996 | welch  |
| Forced - Replayed   | b_abs  |  0.4742 | 0.5448 |  0.8704 | 179.332 | 0.3852 | welch  |
| Observed - Replayed | b0     | -1.8144 | 1.1453 | -1.5842 | 189.173 | 0.1148 | welch  |
| Observed - Replayed | b_inc  | -0.2434 | 0.3342 | -0.7284 | 195.527 | 0.4673 | welch  |
| Observed - Replayed | b_abs  |  0.1733 | 0.4936 |  0.351  | 193.218 | 0.726  | welch  |
| Observed - Forced   | b0     | -0.7711 | 1.0149 | -0.7598 | 195.767 | 0.4483 | welch  |
| Observed - Forced   | b_inc  | -0.3949 | 0.4004 | -0.9864 | 182.503 | 0.3252 | welch  |
| Observed - Forced   | b_abs  | -0.301  | 0.5732 | -0.5251 | 190.366 | 0.6002 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  5.5634 |   95 | 0      |
| Free     | -1 - 0       | -2.9079 |   95 | 0.0045 |
| Free     | 1 - -1       |  6.2733 |   95 | 0      |
| Replayed | 1 - 0        |  3.5078 |   97 | 0.0007 |
| Replayed | -1 - 0       | -2.6449 |   97 | 0.0095 |
| Replayed | 1 - -1       |  5.3656 |   97 | 0      |
| Forced   | 1 - 0        |  3.7432 |   97 | 0.0003 |
| Forced   | -1 - 0       | -1.3158 |   97 | 0.1913 |
| Forced   | 1 - -1       |  4.3438 |   97 | 0      |
| Observed | 1 - 0        |  2.8762 |   99 | 0.0049 |
| Observed | -1 - 0       | -1.4737 |   99 | 0.1437 |
| Observed | 1 - -1       |  4.0551 |   99 | 0.0001 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |      p |   n |
|:---------|-------:|-------:|----:|
| Forced   | 0.3077 | 0.0021 |  98 |
| Free     | 0.1513 | 0.141  |  96 |
| Observed | 0.4038 | 0      | 100 |
| Replayed | 0.3379 | 0.0007 |  98 |

