# exp1a_exp2free_exp3 | AVG stats

## Response variable: `correct`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 74.4811 | 0.6889 | 35.5354 |  192 | 0      |
| Free         | b_inc  | -0.28   | 0.2155 | -1.2994 |  192 | 0.1954 |
| Free         | b_abs  |  0.908  | 0.392  |  2.3162 |  192 | 0.0216 |
| Non-Free     | b0     | 73.007  | 0.4115 | 55.9054 |  295 | 0      |
| Non-Free     | b_inc  |  0.1825 | 0.1851 |  0.9859 |  295 | 0.325  |
| Non-Free     | b_abs  |  0.2761 | 0.3474 |  0.7946 |  295 | 0.4275 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|
| Non-Free - Free | b0     | -1.4741 | 0.8025 | -1.8369 | 326.423 | 0.0671 |
| Non-Free - Free | b_inc  |  0.4625 | 0.2841 |  1.6281 | 428.075 | 0.1042 |
| Non-Free - Free | b_abs  | -0.6319 | 0.5238 | -1.2064 | 436.712 | 0.2283 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  1.3472 |  192 | 0.1795 |
| Free     | -1 - 0       |  2.777  |  192 | 0.006  |
| Free     | 1 - -1       | -1.2994 |  192 | 0.1954 |
| Non-Free | 1 - 0        |  1.1473 |  295 | 0.2522 |
| Non-Free | -1 - 0       |  0.2415 |  295 | 0.8094 |
| Non-Free | 1 - -1       |  0.9859 |  295 | 0.325  |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.5378 |   0 | 193 |
| Non-Free | 0.5582 |   0 | 296 |

