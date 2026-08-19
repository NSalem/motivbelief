# exp1a_exp3 | AVG stats

## Response variable: `rt_log`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |        t |   df |      p |
|:-------------|:-------|--------:|-------:|---------:|-----:|-------:|
| Free         | b0     |  6.3255 | 0.0321 | 196.95   |   95 | 0      |
| Free         | b_inc  |  0.0021 | 0.0038 |   0.5487 |   95 | 0.5845 |
| Free         | b_abs  | -0.0017 | 0.0071 |  -0.2333 |   95 | 0.816  |
| Observed     | b0     |  6.7057 | 0.0401 | 167.382  |   99 | 0      |
| Observed     | b_inc  |  0.0059 | 0.0036 |   1.6246 |   99 | 0.1074 |
| Observed     | b_abs  | -0.0105 | 0.0057 |  -1.8508 |   99 | 0.0672 |
| Forced       | b0     |  6.5765 | 0.0323 | 203.92   |   97 | 0      |
| Forced       | b_inc  |  0.0034 | 0.0028 |   1.1969 |   97 | 0.2342 |
| Forced       | b_abs  | -0.0008 | 0.0047 |  -0.1692 |   97 | 0.866  |
| Replayed     | b0     |  6.6147 | 0.0354 | 186.77   |   97 | 0      |
| Replayed     | b_inc  |  0.0046 | 0.004  |   1.1764 |   97 | 0.2423 |
| Replayed     | b_abs  |  0.0098 | 0.007  |   1.4047 |   97 | 0.1633 |


### Between-group tests (pairwise Welch)

| pair                | coef   |    mean |     se |       t |      df |      p | test   |
|:--------------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Replayed - Free     | b0     |  0.2892 | 0.0478 |  6.0484 | 190.556 | 0      | welch  |
| Replayed - Free     | b_inc  |  0.0025 | 0.0055 |  0.4616 | 191.932 | 0.6449 | welch  |
| Replayed - Free     | b_abs  |  0.0115 | 0.0099 |  1.1538 | 191.913 | 0.25   | welch  |
| Forced - Free       | b0     |  0.251  | 0.0455 |  5.5141 | 191.992 | 0      | welch  |
| Forced - Free       | b_inc  |  0.0013 | 0.0048 |  0.2724 | 176.083 | 0.7857 | welch  |
| Forced - Free       | b_abs  |  0.0009 | 0.0085 |  0.1017 | 164.982 | 0.9191 | welch  |
| Observed - Free     | b0     |  0.3802 | 0.0513 |  7.4053 | 186.757 | 0      | welch  |
| Observed - Free     | b_inc  |  0.0038 | 0.0053 |  0.7153 | 192.783 | 0.4753 | welch  |
| Observed - Free     | b_abs  | -0.0089 | 0.0091 | -0.9778 | 183.809 | 0.3295 | welch  |
| Forced - Replayed   | b0     | -0.0382 | 0.0479 | -0.7976 | 192.323 | 0.4261 | welch  |
| Forced - Replayed   | b_inc  | -0.0012 | 0.0049 | -0.2549 | 176.312 | 0.7991 | welch  |
| Forced - Replayed   | b_abs  | -0.0106 | 0.0084 | -1.2628 | 168.954 | 0.2084 | welch  |
| Observed - Replayed | b0     |  0.0911 | 0.0535 |  1.703  | 193.553 | 0.0902 | welch  |
| Observed - Replayed | b_inc  |  0.0012 | 0.0054 |  0.2296 | 194.133 | 0.8187 | welch  |
| Observed - Replayed | b_abs  | -0.0204 | 0.009  | -2.2574 | 187.368 | 0.0251 | welch  |
| Observed - Forced   | b0     |  0.1293 | 0.0514 |  2.5135 | 188.215 | 0.0128 | welch  |
| Observed - Forced   | b_inc  |  0.0025 | 0.0046 |  0.5368 | 186.536 | 0.592  | welch  |
| Observed - Forced   | b_abs  | -0.0097 | 0.0074 | -1.324  | 189.457 | 0.1871 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  0.0513 |   95 | 0.9592 |
| Free     | -1 - 0       | -0.5274 |   95 | 0.5992 |
| Free     | 1 - -1       |  0.5487 |   95 | 0.5845 |
| Replayed | 1 - 0        |  1.8162 |   97 | 0.0724 |
| Replayed | -1 - 0       |  0.6394 |   97 | 0.5241 |
| Replayed | 1 - -1       |  1.1764 |   97 | 0.2423 |
| Forced   | 1 - 0        |  0.5122 |   97 | 0.6097 |
| Forced   | -1 - 0       | -0.7246 |   97 | 0.4704 |
| Forced   | 1 - -1       |  1.1969 |   97 | 0.2342 |
| Observed | 1 - 0        | -0.7144 |   99 | 0.4767 |
| Observed | -1 - 0       | -2.3533 |   99 | 0.0206 |
| Observed | 1 - -1       |  1.6246 |   99 | 0.1074 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Forced   | 0.4603 |   0 |  98 |
| Free     | 0.5582 |   0 |  96 |
| Observed | 0.4245 |   0 | 100 |
| Replayed | 0.5163 |   0 |  98 |

