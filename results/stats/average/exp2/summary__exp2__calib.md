# exp2 | AVG stats

## Response variable: `calib`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |        t |   df |      p |
|:-------------|:-------|--------:|-------:|---------:|-----:|-------:|
| Observed     | b0     | -8.9246 | 0.8538 | -10.4533 |   99 | 0      |
| Observed     | b_inc  |  0.6505 | 0.3282 |   1.9818 |   99 | 0.0503 |
| Observed     | b_abs  |  0.9424 | 0.8142 |   1.1574 |   99 | 0.2499 |
| Free         | b0     | -3.1413 | 1.1766 |  -2.6697 |   96 | 0.0089 |
| Free         | b_inc  |  2.7548 | 0.4651 |   5.9227 |   96 | 0      |
| Free         | b_abs  | -0.8593 | 0.4962 |  -1.7318 |   96 | 0.0865 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p | test   |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Observed - Free | b0     | -5.7832 | 1.4537 | -3.9782 | 176.305 | 0.0001 | welch  |
| Observed - Free | b_inc  | -2.1043 | 0.5693 | -3.6963 | 173.664 | 0.0003 | welch  |
| Observed - Free | b_abs  |  1.8016 | 0.9535 |  1.8895 | 162.996 | 0.0606 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  2.6563 |   96 | 0.0093 |
| Free     | -1 - 0       | -5.6049 |   96 | 0      |
| Free     | 1 - -1       |  5.9227 |   96 | 0      |
| Observed | 1 - 0        |  1.9014 |   99 | 0.0602 |
| Observed | -1 - 0       |  0.3185 |   99 | 0.7508 |
| Observed | 1 - -1       |  1.9818 |   99 | 0.0503 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |      p |   n |
|:---------|-------:|-------:|----:|
| Free     | 0.0648 | 0.5281 |  97 |
| Observed | 0.7233 | 0      | 100 |

