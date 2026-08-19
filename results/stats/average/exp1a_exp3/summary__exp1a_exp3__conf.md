# exp1a_exp3 | AVG stats

## Response variable: `conf`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 74.594  | 1.4568 | 16.8823 |   95 | 0      |
| Free         | b_inc  |  3.5164 | 0.5359 |  6.5618 |   95 | 0      |
| Free         | b_abs  |  0.2167 | 0.5328 |  0.4067 |   95 | 0.6852 |
| Observed     | b0     | 65.1897 | 0.7435 | 20.4299 |   99 | 0      |
| Observed     | b_inc  |  0.9949 | 0.2437 |  4.0819 |   99 | 0.0001 |
| Observed     | b_abs  |  0.4183 | 0.376  |  1.1124 |   99 | 0.2687 |
| Forced       | b0     | 66.0069 | 0.7019 | 22.805  |   97 | 0      |
| Forced       | b_inc  |  1.5615 | 0.3516 |  4.441  |   97 | 0      |
| Forced       | b_abs  |  0.5084 | 0.4477 |  1.1355 |   97 | 0.259  |
| Replayed     | b0     | 67.0522 | 0.8797 | 19.385  |   97 | 0      |
| Replayed     | b_inc  |  1.2878 | 0.2331 |  5.5243 |   97 | 0      |
| Replayed     | b_abs  |  0.1542 | 0.3288 |  0.469  |   97 | 0.6401 |


### Between-group tests (pairwise Welch)

| pair                | coef   |    mean |     se |       t |      df |      p | test   |
|:--------------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Replayed - Free     | b0     | -7.5418 | 1.7018 | -4.4317 | 156.527 | 0      | welch  |
| Replayed - Free     | b_inc  | -2.2286 | 0.5844 | -3.8135 | 129.806 | 0.0002 | welch  |
| Replayed - Free     | b_abs  | -0.0625 | 0.6261 | -0.0998 | 158.614 | 0.9207 | welch  |
| Forced - Free       | b0     | -8.5872 | 1.6171 | -5.3103 | 136.996 | 0      | welch  |
| Forced - Free       | b_inc  | -1.955  | 0.6409 | -3.0502 | 164.532 | 0.0027 | welch  |
| Forced - Free       | b_abs  |  0.2917 | 0.6959 |  0.4191 | 185.792 | 0.6756 | welch  |
| Observed - Free     | b0     | -9.4043 | 1.6356 | -5.7499 | 141.71  | 0      | welch  |
| Observed - Free     | b_inc  | -2.5215 | 0.5887 | -4.2831 | 132.912 | 0      | welch  |
| Observed - Free     | b_abs  |  0.2016 | 0.6522 |  0.3091 | 172.208 | 0.7576 | welch  |
| Forced - Replayed   | b0     | -1.0454 | 1.1254 | -0.9289 | 184.889 | 0.3542 | welch  |
| Forced - Replayed   | b_inc  |  0.2736 | 0.4219 |  0.6486 | 168.475 | 0.5175 | welch  |
| Forced - Replayed   | b_abs  |  0.3541 | 0.5555 |  0.6375 | 178.07  | 0.5246 | welch  |
| Observed - Replayed | b0     | -1.8625 | 1.1518 | -1.6171 | 190.058 | 0.1075 | welch  |
| Observed - Replayed | b_inc  | -0.2929 | 0.3373 | -0.8685 | 195.77  | 0.3862 | welch  |
| Observed - Replayed | b_abs  |  0.2641 | 0.4996 |  0.5286 | 193.072 | 0.5977 | welch  |
| Observed - Forced   | b0     | -0.8172 | 1.0225 | -0.7992 | 195.562 | 0.4251 | welch  |
| Observed - Forced   | b_inc  | -0.5665 | 0.4278 | -1.3242 | 173.396 | 0.1872 | welch  |
| Observed - Forced   | b_abs  | -0.0901 | 0.5847 | -0.154  | 189.658 | 0.8777 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  5.7392 |   95 | 0      |
| Free     | -1 - 0       | -3.8913 |   95 | 0.0002 |
| Free     | 1 - -1       |  6.5618 |   95 | 0      |
| Replayed | 1 - 0        |  3.5078 |   97 | 0.0007 |
| Replayed | -1 - 0       | -2.8705 |   97 | 0.005  |
| Replayed | 1 - -1       |  5.5243 |   97 | 0      |
| Forced   | 1 - 0        |  3.7449 |   97 | 0.0003 |
| Forced   | -1 - 0       | -1.7991 |   97 | 0.0751 |
| Forced   | 1 - -1       |  4.441  |   97 | 0      |
| Observed | 1 - 0        |  2.9476 |   99 | 0.004  |
| Observed | -1 - 0       | -1.3913 |   99 | 0.1673 |
| Observed | 1 - -1       |  4.0819 |   99 | 0.0001 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |       r |      p |   n |
|:---------|--------:|-------:|----:|
| Forced   |  0.2374 | 0.0186 |  98 |
| Free     | -0.0059 | 0.9543 |  96 |
| Observed |  0.4127 | 0      | 100 |
| Replayed |  0.3313 | 0.0009 |  98 |

