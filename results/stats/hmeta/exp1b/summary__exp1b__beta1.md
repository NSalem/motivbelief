# exp1b | meta-d′ AVG-style stats

## Response variable: `beta1`

### Model used for participant coefficients

- `y ~ 1 + incentive`
- Incentive levels: 0.1, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |   mean |     se |       t |   df |      p |
|:-------------|:-------|-------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 1.6799 | 0.0943 | 17.8152 |   91 | 0      |
| Free         | b_inc  | 0.1739 | 0.0825 |  2.1069 |   91 | 0.0379 |
| Observed     | b0     | 1.5658 | 0.1001 | 15.648  |   99 | 0      |
| Observed     | b_inc  | 0.1225 | 0.0853 |  1.4355 |   99 | 0.1543 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p | test   |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Observed - Free | b0     | -0.1142 | 0.1375 | -0.8303 | 189.944 | 0.4074 | welch  |
| Observed - Free | b_inc  | -0.0514 | 0.1187 | -0.433  | 189.985 | 0.6655 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |      t |   df |      p |
|:---------|:-------------|-------:|-----:|-------:|
| Free     | 1.0 - 0.1    | 2.1069 |   91 | 0.0379 |
| Observed | 1.0 - 0.1    | 1.4355 |   99 | 0.1543 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

_None_

