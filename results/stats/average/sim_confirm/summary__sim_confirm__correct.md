# sim_confirm | AVG stats

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
| Non-Free     | b0     | 74.5661 | 0.3662 | 67.0902 |  192 | 0      |
| Non-Free     | b_inc  |  0.0097 | 0.2088 |  0.0465 |  192 | 0.9629 |
| Non-Free     | b_abs  | -0.1328 | 0.4649 | -0.2856 |  192 | 0.7755 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |   df |      p | test   |
|:----------------|:-------|--------:|-------:|--------:|-----:|-------:|:-------|
| Non-Free - Free | b0     |  0.085  | 0.7803 |  0.1089 |  192 | 0.9134 | paired |
| Non-Free - Free | b_inc  |  0.2898 | 0.3076 |  0.9421 |  192 | 0.3473 | paired |
| Non-Free - Free | b_abs  | -1.0407 | 0.5752 | -1.8093 |  192 | 0.072  | paired |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  1.3472 |  192 | 0.1795 |
| Free     | -1 - 0       |  2.777  |  192 | 0.006  |
| Free     | 1 - -1       | -1.2994 |  192 | 0.1954 |
| Non-Free | 1 - 0        | -0.2376 |  192 | 0.8125 |
| Non-Free | -1 - 0       | -0.2843 |  192 | 0.7765 |
| Non-Free | 1 - -1       |  0.0465 |  192 | 0.9629 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.5378 |   0 | 193 |
| Non-Free | 0.6645 |   0 | 193 |

