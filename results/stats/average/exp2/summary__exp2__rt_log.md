# exp2 | AVG stats

## Response variable: `rt_log`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |        t |   df |      p |
|:-------------|:-------|--------:|-------:|---------:|-----:|-------:|
| Observed     | b0     |  6.6601 | 0.0347 | 191.963  |   99 | 0      |
| Observed     | b_inc  | -0.0058 | 0.004  |  -1.4489 |   99 | 0.1505 |
| Observed     | b_abs  | -0.002  | 0.0061 |  -0.3327 |   99 | 0.7401 |
| Free         | b0     |  6.4169 | 0.038  | 168.845  |   96 | 0      |
| Free         | b_inc  |  0.0008 | 0.0039 |   0.2114 |   96 | 0.833  |
| Free         | b_abs  | -0.0141 | 0.0076 |  -1.8563 |   96 | 0.0665 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|
| Observed - Free | b0     |  0.2432 | 0.0515 |  4.7251 | 192.822 | 0      |
| Observed - Free | b_inc  | -0.0066 | 0.0056 | -1.1864 | 194.966 | 0.2369 |
| Observed - Free | b_abs  |  0.0121 | 0.0097 |  1.2439 | 184.556 | 0.2151 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        | -1.573  |   96 | 0.119  |
| Free     | -1 - 0       | -1.7344 |   96 | 0.086  |
| Free     | 1 - -1       |  0.2114 |   96 | 0.833  |
| Observed | 1 - 0        | -1.074  |   99 | 0.2855 |
| Observed | -1 - 0       |  0.517  |   99 | 0.6063 |
| Observed | 1 - -1       | -1.4489 |   99 | 0.1505 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.5886 |   0 |  97 |
| Observed | 0.3974 |   0 | 100 |

