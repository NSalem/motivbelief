# exp3 | AVG stats

## Response variable: `rt_log`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |        t |   df |      p |
|:-------------|:-------|--------:|-------:|---------:|-----:|-------:|
| Forced       | b0     |  6.5765 | 0.0323 | 203.92   |   97 | 0      |
| Forced       | b_inc  |  0.0034 | 0.0028 |   1.1969 |   97 | 0.2342 |
| Forced       | b_abs  | -0.0008 | 0.0047 |  -0.1692 |   97 | 0.866  |
| Replayed     | b0     |  6.6147 | 0.0354 | 186.77   |   97 | 0      |
| Replayed     | b_inc  |  0.0046 | 0.004  |   1.1764 |   97 | 0.2423 |
| Replayed     | b_abs  |  0.0098 | 0.007  |   1.4047 |   97 | 0.1633 |


### Between-group tests (pairwise Welch)

| pair              | coef   |    mean |     se |       t |      df |      p |
|:------------------|:-------|--------:|-------:|--------:|--------:|-------:|
| Forced - Replayed | b0     | -0.0382 | 0.0479 | -0.7976 | 192.323 | 0.4261 |
| Forced - Replayed | b_inc  | -0.0012 | 0.0049 | -0.2549 | 176.312 | 0.7991 |
| Forced - Replayed | b_abs  | -0.0106 | 0.0084 | -1.2628 | 168.954 | 0.2084 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Replayed | 1 - 0        |  1.8162 |   97 | 0.0724 |
| Replayed | -1 - 0       |  0.6394 |   97 | 0.5241 |
| Replayed | 1 - -1       |  1.1764 |   97 | 0.2423 |
| Forced   | 1 - 0        |  0.5122 |   97 | 0.6097 |
| Forced   | -1 - 0       | -0.7246 |   97 | 0.4704 |
| Forced   | 1 - -1       |  1.1969 |   97 | 0.2342 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Forced   | 0.4603 |   0 |  98 |
| Replayed | 0.5163 |   0 |  98 |

