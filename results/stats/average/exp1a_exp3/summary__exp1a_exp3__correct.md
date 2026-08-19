# exp1a_exp3 | AVG stats

## Response variable: `correct`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 74.5894 | 1.0316 | 23.8367 |   95 | 0      |
| Free         | b_inc  | -0.3541 | 0.2884 | -1.2278 |   95 | 0.2226 |
| Free         | b_abs  |  0.5254 | 0.5856 |  0.8971 |   95 | 0.3719 |
| Observed     | b0     | 75.1946 | 0.4796 | 52.5339 |   99 | 0      |
| Observed     | b_inc  |  0.0068 | 0.3397 |  0.0199 |   99 | 0.9842 |
| Observed     | b_abs  | -0.9863 | 0.616  | -1.6012 |   99 | 0.1125 |
| Forced       | b0     | 73.8697 | 0.4515 | 52.8727 |   97 | 0      |
| Forced       | b_inc  |  0.2785 | 0.3028 |  0.9198 |   97 | 0.36   |
| Forced       | b_abs  |  0.4251 | 0.5824 |  0.7299 |   97 | 0.4672 |
| Replayed     | b0     | 69.9121 | 0.9775 | 20.3694 |   97 | 0      |
| Replayed     | b_inc  |  0.2658 | 0.3199 |  0.8308 |   97 | 0.4081 |
| Replayed     | b_abs  |  1.4151 | 0.5866 |  2.4125 |   97 | 0.0177 |


### Between-group tests (pairwise Welch)

| pair                | coef   |    mean |     se |       t |      df |      p | test   |
|:--------------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Replayed - Free     | b0     | -4.6773 | 1.4212 | -3.2911 | 191.213 | 0.0012 | welch  |
| Replayed - Free     | b_inc  |  0.6198 | 0.4307 |  1.4392 | 190.359 | 0.1517 | welch  |
| Replayed - Free     | b_abs  |  0.8897 | 0.8289 |  1.0734 | 191.985 | 0.2844 | welch  |
| Forced - Free       | b0     | -0.7197 | 1.126  | -0.6391 | 130.197 | 0.5239 | welch  |
| Forced - Free       | b_inc  |  0.6326 | 0.4181 |  1.5128 | 191.721 | 0.132  | welch  |
| Forced - Free       | b_abs  | -0.1003 | 0.8259 | -0.1214 | 191.952 | 0.9035 | welch  |
| Observed - Free     | b0     |  0.6052 | 1.1376 |  0.532  | 134.476 | 0.5956 | welch  |
| Observed - Free     | b_inc  |  0.3608 | 0.4456 |  0.8098 | 190.184 | 0.4191 | welch  |
| Observed - Free     | b_abs  | -1.5117 | 0.8499 | -1.7786 | 193.827 | 0.0769 | welch  |
| Forced - Replayed   | b0     |  3.9576 | 1.0768 |  3.6755 | 136.577 | 0.0003 | welch  |
| Forced - Replayed   | b_inc  |  0.0127 | 0.4404 |  0.0289 | 193.416 | 0.977  | welch  |
| Forced - Replayed   | b_abs  | -0.99   | 0.8266 | -1.1976 | 193.99  | 0.2325 | welch  |
| Observed - Replayed | b0     |  5.2825 | 1.0889 |  4.8515 | 141.294 | 0      | welch  |
| Observed - Replayed | b_inc  | -0.259  | 0.4666 | -0.5551 | 195.515 | 0.5795 | welch  |
| Observed - Replayed | b_abs  | -2.4014 | 0.8506 | -2.8233 | 195.707 | 0.0052 | welch  |
| Observed - Forced   | b0     |  1.3249 | 0.6586 |  2.0115 | 195.508 | 0.0456 | welch  |
| Observed - Forced   | b_inc  | -0.2717 | 0.455  | -0.5972 | 193.887 | 0.5511 | welch  |
| Observed - Forced   | b_abs  | -1.4114 | 0.8477 | -1.6649 | 195.591 | 0.0975 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  0.248  |   95 | 0.8047 |
| Free     | -1 - 0       |  1.4361 |   95 | 0.1542 |
| Free     | 1 - -1       | -1.2278 |   95 | 0.2226 |
| Replayed | 1 - 0        |  2.5162 |   97 | 0.0135 |
| Replayed | -1 - 0       |  1.72   |   97 | 0.0886 |
| Replayed | 1 - -1       |  0.8308 |   97 | 0.4081 |
| Forced   | 1 - 0        |  1.0447 |   97 | 0.2987 |
| Forced   | -1 - 0       |  0.2295 |   97 | 0.819  |
| Forced   | 1 - -1       |  0.9198 |   97 | 0.36   |
| Observed | 1 - 0        | -1.3735 |   99 | 0.1727 |
| Observed | -1 - 0       | -1.4318 |   99 | 0.1553 |
| Observed | 1 - -1       |  0.0199 |   99 | 0.9842 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Forced   | 0.5753 |   0 |  98 |
| Free     | 0.6141 |   0 |  96 |
| Observed | 0.5338 |   0 | 100 |
| Replayed | 0.5415 |   0 |  98 |

