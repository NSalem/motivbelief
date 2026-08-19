# exp3 | AVG stats

## Response variable: `correct`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Forced       | b0     | 73.8697 | 0.4515 | 52.8727 |   97 | 0      |
| Forced       | b_inc  |  0.2785 | 0.3028 |  0.9198 |   97 | 0.36   |
| Forced       | b_abs  |  0.4251 | 0.5824 |  0.7299 |   97 | 0.4672 |
| Replayed     | b0     | 69.9121 | 0.9775 | 20.3694 |   97 | 0      |
| Replayed     | b_inc  |  0.2658 | 0.3199 |  0.8308 |   97 | 0.4081 |
| Replayed     | b_abs  |  1.4151 | 0.5866 |  2.4125 |   97 | 0.0177 |


### Between-group tests (pairwise Welch)

| pair              | coef   |    mean |     se |       t |      df |      p | test   |
|:------------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Forced - Replayed | b0     |  3.9576 | 1.0768 |  3.6755 | 136.577 | 0.0003 | welch  |
| Forced - Replayed | b_inc  |  0.0127 | 0.4404 |  0.0289 | 193.416 | 0.977  | welch  |
| Forced - Replayed | b_abs  | -0.99   | 0.8266 | -1.1976 | 193.99  | 0.2325 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |      t |   df |      p |
|:---------|:-------------|-------:|-----:|-------:|
| Replayed | 1 - 0        | 2.5162 |   97 | 0.0135 |
| Replayed | -1 - 0       | 1.72   |   97 | 0.0886 |
| Replayed | 1 - -1       | 0.8308 |   97 | 0.4081 |
| Forced   | 1 - 0        | 1.0447 |   97 | 0.2987 |
| Forced   | -1 - 0       | 0.2295 |   97 | 0.819  |
| Forced   | 1 - -1       | 0.9198 |   97 | 0.36   |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Forced   | 0.5753 |   0 |  98 |
| Replayed | 0.5415 |   0 |  98 |

