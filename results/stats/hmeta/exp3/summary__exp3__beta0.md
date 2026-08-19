# exp3 | meta-d′ AVG-style stats

## Response variable: `beta0`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Forced       | b0     |  2.5608 | 0.1639 | 15.6228 |   97 | 0      |
| Forced       | b_inc  |  0.1106 | 0.0486 |  2.2735 |   97 | 0.0252 |
| Forced       | b_abs  |  0.0305 | 0.0674 |  0.453  |   97 | 0.6516 |
| Replayed     | b0     |  1.6413 | 0.113  | 14.5254 |   97 | 0      |
| Replayed     | b_inc  | -0.0218 | 0.0265 | -0.8221 |   97 | 0.413  |
| Replayed     | b_abs  |  0.1597 | 0.0546 |  2.9239 |   97 | 0.0043 |


### Between-group tests (pairwise Welch)

| pair              | coef   |    mean |     se |       t |      df |      p | test   |
|:------------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Forced - Replayed | b0     |  0.9195 | 0.1991 |  4.6184 | 172.209 | 0      | welch  |
| Forced - Replayed | b_inc  |  0.1323 | 0.0554 |  2.3899 | 149.8   | 0.0181 | welch  |
| Forced - Replayed | b_abs  | -0.1292 | 0.0867 | -1.4898 | 186.063 | 0.138  | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Replayed | 1 - 0        |  2.2753 |   97 | 0.0251 |
| Replayed | -1 - 0       |  2.9867 |   97 | 0.0036 |
| Replayed | 1 - -1       | -0.8221 |   97 | 0.413  |
| Forced   | 1 - 0        |  1.4837 |   97 | 0.1411 |
| Forced   | -1 - 0       | -1.16   |   97 | 0.2489 |
| Forced   | 1 - -1       |  2.2735 |   97 | 0.0252 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |      p |   n |
|:---------|-------:|-------:|----:|
| Forced   | 0.3309 | 0.0009 |  98 |
| Replayed | 0.6199 | 0      |  98 |

