# exp1b | meta-d′ AVG-style stats

## Response variable: `beta0`

### Model used for participant coefficients

- `y ~ 1 + incentive`
- Incentive levels: 0.1, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |   mean |     se |       t |   df |      p |
|:-------------|:-------|-------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 2.0531 | 0.1306 | 15.7255 |   91 | 0      |
| Free         | b_inc  | 0.0974 | 0.0803 |  1.2125 |   91 | 0.2285 |
| Observed     | b0     | 2.4103 | 0.1571 | 15.3411 |   99 | 0      |
| Observed     | b_inc  | 0.01   | 0.0686 |  0.1461 |   99 | 0.8841 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p | test   |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Observed - Free | b0     |  0.3571 | 0.2043 |  1.7483 | 186.293 | 0.0821 | welch  |
| Observed - Free | b_inc  | -0.0874 | 0.1057 | -0.8268 | 182.825 | 0.4094 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |      t |   df |      p |
|:---------|:-------------|-------:|-----:|-------:|
| Free     | 1.0 - 0.1    | 1.2125 |   91 | 0.2285 |
| Observed | 1.0 - 0.1    | 0.1461 |   99 | 0.8841 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

_None_

