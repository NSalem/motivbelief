# exp2 | meta-d′ AVG-style stats

## Response variable: `beta1`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Observed     | b0     |  1.6702 | 0.1096 | 15.2376 |   99 | 0      |
| Observed     | b_inc  |  0.0297 | 0.0301 |  0.9877 |   99 | 0.3257 |
| Observed     | b_abs  | -0.0177 | 0.0636 | -0.2785 |   99 | 0.7812 |
| Free         | b0     |  1.5771 | 0.0946 | 16.6747 |   96 | 0      |
| Free         | b_inc  |  0.0826 | 0.0322 |  2.5667 |   96 | 0.0118 |
| Free         | b_abs  |  0.0418 | 0.0571 |  0.7324 |   96 | 0.4657 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p | test   |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Observed - Free | b0     |  0.0931 | 0.1448 |  0.643  | 191.708 | 0.521  | welch  |
| Observed - Free | b_inc  | -0.0529 | 0.0441 | -1.2008 | 193.667 | 0.2313 | welch  |
| Observed - Free | b_abs  | -0.0596 | 0.0855 | -0.6965 | 193.354 | 0.487  | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  1.7559 |   96 | 0.0823 |
| Free     | -1 - 0       | -0.6822 |   96 | 0.4968 |
| Free     | 1 - -1       |  2.5667 |   96 | 0.0118 |
| Observed | 1 - 0        |  0.1608 |   99 | 0.8726 |
| Observed | -1 - 0       | -0.7192 |   99 | 0.4737 |
| Observed | 1 - -1       |  0.9877 |   99 | 0.3257 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.5255 |   0 |  97 |
| Observed | 0.6395 |   0 | 100 |

