# exp1a_exp3 | AVG stats

## Response variable: `calib`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |     mean |     se |        t |   df |      p |
|:-------------|:-------|---------:|-------:|---------:|-----:|-------:|
| Free         | b0     |   0.0046 | 1.5721 |   0.003  |   95 | 0.9976 |
| Free         | b_inc  |   3.8705 | 0.5832 |   6.6365 |   95 | 0      |
| Free         | b_abs  |  -0.3087 | 0.8458 |  -0.365  |   95 | 0.7159 |
| Observed     | b0     | -10.0049 | 0.8503 | -11.7667 |   99 | 0      |
| Observed     | b_inc  |   0.9882 | 0.3246 |   3.0445 |   99 | 0.003  |
| Observed     | b_abs  |   1.4046 | 0.552  |   2.5445 |   99 | 0.0125 |
| Forced       | b0     |  -7.8629 | 0.7355 | -10.6908 |   97 | 0      |
| Forced       | b_inc  |   1.283  | 0.42   |   3.0546 |   97 | 0.0029 |
| Forced       | b_abs  |   0.0832 | 0.5765 |   0.1444 |   97 | 0.8855 |
| Replayed     | b0     |  -2.8599 | 0.947  |  -3.02   |   97 | 0.0032 |
| Replayed     | b_inc  |   1.0221 | 0.3227 |   3.1675 |   97 | 0.0021 |
| Replayed     | b_abs  |  -1.2609 | 0.6341 |  -1.9883 |   97 | 0.0496 |


### Between-group tests (pairwise Welch)

| pair                | coef   |     mean |     se |       t |      df |      p |
|:--------------------|:-------|---------:|-------:|--------:|--------:|-------:|
| Replayed - Free     | b0     |  -2.8645 | 1.8353 | -1.5608 | 156.293 | 0.1206 |
| Replayed - Free     | b_inc  |  -2.8484 | 0.6665 | -4.2735 | 148.44  | 0      |
| Replayed - Free     | b_abs  |  -0.9522 | 1.0571 | -0.9007 | 177.038 | 0.369  |
| Forced - Free       | b0     |  -7.8675 | 1.7356 | -4.5329 | 134.81  | 0      |
| Forced - Free       | b_inc  |  -2.5876 | 0.7187 | -3.6003 | 173.411 | 0.0004 |
| Forced - Free       | b_abs  |   0.392  | 1.0236 |  0.3829 | 168.218 | 0.7023 |
| Observed - Free     | b0     | -10.0096 | 1.7873 | -5.6003 | 146.665 | 0      |
| Observed - Free     | b_inc  |  -2.8824 | 0.6674 | -4.3185 | 149.223 | 0      |
| Observed - Free     | b_abs  |   1.7133 | 1.01   |  1.6964 | 164.526 | 0.0917 |
| Forced - Replayed   | b0     |  -5.003  | 1.199  | -4.1725 | 182.802 | 0      |
| Forced - Replayed   | b_inc  |   0.2609 | 0.5297 |  0.4925 | 181.92  | 0.6229 |
| Forced - Replayed   | b_abs  |   1.3441 | 0.857  |  1.5684 | 192.264 | 0.1184 |
| Observed - Replayed | b0     |  -7.1451 | 1.2727 | -5.6142 | 193.331 | 0      |
| Observed - Replayed | b_inc  |  -0.0339 | 0.4577 | -0.0741 | 195.996 | 0.941  |
| Observed - Replayed | b_abs  |   2.6654 | 0.8407 |  3.1704 | 191.797 | 0.0018 |
| Observed - Forced   | b0     |  -2.1421 | 1.1242 | -1.9054 | 192.551 | 0.0582 |
| Observed - Forced   | b_inc  |  -0.2948 | 0.5308 | -0.5554 | 183.371 | 0.5793 |
| Observed - Forced   | b_abs  |   1.3213 | 0.7982 |  1.6555 | 195.439 | 0.0994 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  3.8681 |   95 | 0.0002 |
| Free     | -1 - 0       | -3.7187 |   95 | 0.0003 |
| Free     | 1 - -1       |  6.6365 |   95 | 0      |
| Replayed | 1 - 0        | -0.3375 |   97 | 0.7364 |
| Replayed | -1 - 0       | -3.1902 |   97 | 0.0019 |
| Replayed | 1 - -1       |  3.1675 |   97 | 0.0021 |
| Forced   | 1 - 0        |  1.8544 |   97 | 0.0667 |
| Forced   | -1 - 0       | -1.7413 |   97 | 0.0848 |
| Forced   | 1 - -1       |  3.0546 |   97 | 0.0029 |
| Observed | 1 - 0        |  3.5927 |   99 | 0.0005 |
| Observed | -1 - 0       |  0.6786 |   99 | 0.499  |
| Observed | 1 - -1       |  3.0445 |   99 | 0.003  |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |      p |   n |
|:---------|-------:|-------:|----:|
| Forced   | 0.3072 | 0.0021 |  98 |
| Free     | 0.3625 | 0.0003 |  96 |
| Observed | 0.4878 | 0      | 100 |
| Replayed | 0.5887 | 0      |  98 |

