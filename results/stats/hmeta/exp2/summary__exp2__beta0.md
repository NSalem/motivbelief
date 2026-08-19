# exp2 | meta-d′ AVG-style stats

## Response variable: `beta0`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |   mean |     se |       t |   df |      p |
|:-------------|:-------|-------:|-------:|--------:|-----:|-------:|
| Observed     | b0     | 2.1826 | 0.1754 | 12.4444 |   99 | 0      |
| Observed     | b_inc  | 0.0448 | 0.03   |  1.495  |   99 | 0.1381 |
| Observed     | b_abs  | 0.0302 | 0.0599 |  0.5042 |   99 | 0.6153 |
| Free         | b0     | 1.7658 | 0.1209 | 14.61   |   96 | 0      |
| Free         | b_inc  | 0.0423 | 0.0282 |  1.497  |   96 | 0.1377 |
| Free         | b_abs  | 0.0204 | 0.0584 |  0.3483 |   96 | 0.7284 |


### Between-group tests (pairwise Welch)

| pair            | coef   |   mean |     se |      t |      df |      p | test   |
|:----------------|:-------|-------:|-------:|-------:|--------:|-------:|:-------|
| Observed - Free | b0     | 0.4167 | 0.213  | 1.9565 | 174.722 | 0.052  | welch  |
| Observed - Free | b_inc  | 0.0025 | 0.0412 | 0.0611 | 194.628 | 0.9513 | welch  |
| Observed - Free | b_abs  | 0.0099 | 0.0837 | 0.1177 | 194.982 | 0.9064 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  0.8606 |   96 | 0.3916 |
| Free     | -1 - 0       | -0.3916 |   96 | 0.6962 |
| Free     | 1 - -1       |  1.497  |   96 | 0.1377 |
| Observed | 1 - 0        |  1.0366 |   99 | 0.3025 |
| Observed | -1 - 0       | -0.2383 |   99 | 0.8122 |
| Observed | 1 - -1       |  1.495  |   99 | 0.1381 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.6431 |   0 |  97 |
| Observed | 0.6085 |   0 | 100 |

