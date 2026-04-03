# exp1a | AVG stats

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


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|
| Observed - Free | b0     | -9.4043 | 1.6356 | -5.7499 | 141.71  | 0      |
| Observed - Free | b_inc  | -2.5215 | 0.5887 | -4.2831 | 132.912 | 0      |
| Observed - Free | b_abs  |  0.2016 | 0.6522 |  0.3091 | 172.208 | 0.7576 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  5.7392 |   95 | 0      |
| Free     | -1 - 0       | -3.8913 |   95 | 0.0002 |
| Free     | 1 - -1       |  6.5618 |   95 | 0      |
| Observed | 1 - 0        |  2.9476 |   99 | 0.004  |
| Observed | -1 - 0       | -1.3913 |   99 | 0.1673 |
| Observed | 1 - -1       |  4.0819 |   99 | 0.0001 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |       r |      p |   n |
|:---------|--------:|-------:|----:|
| Free     | -0.0059 | 0.9543 |  96 |
| Observed |  0.4127 | 0      | 100 |

