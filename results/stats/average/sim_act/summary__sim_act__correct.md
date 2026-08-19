# sim_act | AVG stats

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
| Non-Free     | b0     | 74.5013 | 0.3195 | 76.6965 |  192 | 0      |
| Non-Free     | b_inc  | -0.4275 | 0.2522 | -1.6949 |  192 | 0.0917 |
| Non-Free     | b_abs  | -0.0907 | 0.3852 | -0.2354 |  192 | 0.8142 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |   df |      p | test   |
|:----------------|:-------|--------:|-------:|--------:|-----:|-------:|:-------|
| Non-Free - Free | b0     |  0.0202 | 0.7549 |  0.0268 |  192 | 0.9787 | paired |
| Non-Free - Free | b_inc  | -0.1474 | 0.3215 | -0.4586 |  192 | 0.6471 | paired |
| Non-Free - Free | b_abs  | -0.9986 | 0.5845 | -1.7086 |  192 | 0.0891 | paired |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  1.3472 |  192 | 0.1795 |
| Free     | -1 - 0       |  2.777  |  192 | 0.006  |
| Free     | 1 - -1       | -1.2994 |  192 | 0.1954 |
| Non-Free | 1 - 0        | -1.0784 |  192 | 0.2822 |
| Non-Free | -1 - 0       |  0.7664 |  192 | 0.4444 |
| Non-Free | 1 - -1       | -1.6949 |  192 | 0.0917 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.5378 |   0 | 193 |
| Non-Free | 0.4015 |   0 | 193 |

