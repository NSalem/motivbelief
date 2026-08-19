# sim_intent | AVG stats

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
| Non-Free     | b0     | 74.7215 | 0.3271 | 75.5784 |  192 | 0      |
| Non-Free     | b_inc  | -0.0972 | 0.2397 | -0.4053 |  192 | 0.6857 |
| Non-Free     | b_abs  | -0.1036 | 0.3922 | -0.2642 |  192 | 0.7919 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |   df |      p | test   |
|:----------------|:-------|--------:|-------:|--------:|-----:|-------:|:-------|
| Non-Free - Free | b0     |  0.2404 | 0.7501 |  0.3205 |  192 | 0.7489 | paired |
| Non-Free - Free | b_inc  |  0.1829 | 0.3264 |  0.5603 |  192 | 0.5759 | paired |
| Non-Free - Free | b_abs  | -1.0116 | 0.564  | -1.7935 |  192 | 0.0745 | paired |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  1.3472 |  192 | 0.1795 |
| Free     | -1 - 0       |  2.777  |  192 | 0.006  |
| Free     | 1 - -1       | -1.2994 |  192 | 0.1954 |
| Non-Free | 1 - 0        | -0.4507 |  192 | 0.6527 |
| Non-Free | -1 - 0       | -0.0137 |  192 | 0.9891 |
| Non-Free | 1 - -1       | -0.4053 |  192 | 0.6857 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.5378 |   0 | 193 |
| Non-Free | 0.4569 |   0 | 193 |

