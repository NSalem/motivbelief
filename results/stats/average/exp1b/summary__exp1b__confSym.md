# exp1b | AVG stats

## Response variable: `confSym`

### Model used for participant coefficients

- `y ~ 1 + incentive`
- Incentive levels: 0.1, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 76.4005 | 1.2453 | 21.2002 |   91 | 0      |
| Free         | b_inc  |  2.711  | 0.4626 |  5.8607 |   91 | 0      |
| Observed     | b0     | 64.0059 | 0.7416 | 18.8859 |   99 | 0      |
| Observed     | b_inc  |  1.0867 | 0.5607 |  1.9382 |   99 | 0.0555 |


### Between-group tests (pairwise Welch)

| pair            | coef   |     mean |     se |       t |      df |      p | test   |
|:----------------|:-------|---------:|-------:|--------:|--------:|-------:|:-------|
| Observed - Free | b0     | -12.3946 | 1.4494 | -8.5516 | 149.687 | 0      | welch  |
| Observed - Free | b_inc  |  -1.6242 | 0.7269 | -2.2345 | 185.923 | 0.0266 | welch  |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |      t |   df |      p |
|:---------|:-------------|-------:|-----:|-------:|
| Free     | 1.0 - 0.1    | 5.8607 |   91 | 0      |
| Observed | 1.0 - 0.1    | 1.9382 |   99 | 0.0555 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

_None_

