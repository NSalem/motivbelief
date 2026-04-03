# exp3 | AVG stats

## Response variable: `calib`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |        t |   df |      p |
|:-------------|:-------|--------:|-------:|---------:|-----:|-------:|
| Forced       | b0     | -7.8629 | 0.7355 | -10.6908 |   97 | 0      |
| Forced       | b_inc  |  1.283  | 0.42   |   3.0546 |   97 | 0.0029 |
| Forced       | b_abs  |  0.0832 | 0.5765 |   0.1444 |   97 | 0.8855 |
| Replayed     | b0     | -2.8599 | 0.947  |  -3.02   |   97 | 0.0032 |
| Replayed     | b_inc  |  1.0221 | 0.3227 |   3.1675 |   97 | 0.0021 |
| Replayed     | b_abs  | -1.2609 | 0.6341 |  -1.9883 |   97 | 0.0496 |


### Between-group tests (pairwise Welch)

| pair              | coef   |    mean |     se |       t |      df |      p |
|:------------------|:-------|--------:|-------:|--------:|--------:|-------:|
| Forced - Replayed | b0     | -5.003  | 1.199  | -4.1725 | 182.802 | 0      |
| Forced - Replayed | b_inc  |  0.2609 | 0.5297 |  0.4925 | 181.92  | 0.6229 |
| Forced - Replayed | b_abs  |  1.3441 | 0.857  |  1.5684 | 192.264 | 0.1184 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Replayed | 1 - 0        | -0.3375 |   97 | 0.7364 |
| Replayed | -1 - 0       | -3.1902 |   97 | 0.0019 |
| Replayed | 1 - -1       |  3.1675 |   97 | 0.0021 |
| Forced   | 1 - 0        |  1.8544 |   97 | 0.0667 |
| Forced   | -1 - 0       | -1.7413 |   97 | 0.0848 |
| Forced   | 1 - -1       |  3.0546 |   97 | 0.0029 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |      p |   n |
|:---------|-------:|-------:|----:|
| Forced   | 0.3072 | 0.0021 |  98 |
| Replayed | 0.5887 | 0      |  98 |

