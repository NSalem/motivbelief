# exp3 | meta-d′ AVG-style stats

## Response variable: `beta1`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Forced       | b0     |  1.9418 | 0.1041 | 18.6499 |   97 | 0      |
| Forced       | b_inc  |  0.0679 | 0.0408 |  1.6631 |   97 | 0.0995 |
| Forced       | b_abs  | -0.0396 | 0.0589 | -0.6722 |   97 | 0.503  |
| Replayed     | b0     |  1.5186 | 0.0815 | 18.6422 |   97 | 0      |
| Replayed     | b_inc  | -0.0093 | 0.0299 | -0.3113 |   97 | 0.7562 |
| Replayed     | b_abs  |  0.1237 | 0.0529 |  2.3385 |   97 | 0.0214 |


### Between-group tests (pairwise Welch)

| pair              | coef   |    mean |     se |       t |      df |      p | test   |
|:------------------|:-------|--------:|-------:|--------:|--------:|-------:|:-------|
| Forced - Replayed | b0     |  0.4232 | 0.1322 |  3.2009 | 183.386 | 0.0016 | welch  |
| Forced - Replayed | b_inc  |  0.0772 | 0.0506 |  1.5262 | 177.679 | 0.1287 | welch  |
| Forced - Replayed | b_abs  | -0.1633 | 0.0792 | -2.0626 | 191.799 | 0.0405 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Replayed | 1 - 0        |  1.7055 |   97 | 0.0913 |
| Replayed | -1 - 0       |  2.4781 |   97 | 0.0149 |
| Replayed | 1 - -1       | -0.3113 |   97 | 0.7562 |
| Forced   | 1 - 0        |  0.3741 |   97 | 0.7092 |
| Forced   | -1 - 0       | -1.5946 |   97 | 0.1141 |
| Forced   | 1 - -1       |  1.6631 |   97 | 0.0995 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |      p |   n |
|:---------|-------:|-------:|----:|
| Forced   | 0.3532 | 0.0004 |  98 |
| Replayed | 0.5296 | 0      |  98 |

