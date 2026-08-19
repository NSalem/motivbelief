# sim_intent | AVG stats

## Response variable: `conf`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 75.4098 | 1.0282 | 24.7141 |  192 | 0      |
| Free         | b_inc  |  2.6348 | 0.3625 |  7.2676 |  192 | 0      |
| Free         | b_abs  | -0.5466 | 0.2376 | -2.3002 |  192 | 0.0225 |
| Non-Free     | b0     | 62.3394 | 0.4305 | 28.6633 |  192 | 0      |
| Non-Free     | b_inc  |  0.8037 | 0.1543 |  5.2072 |  192 | 0      |
| Non-Free     | b_abs  | -0.3517 | 0.1668 | -2.108  |  192 | 0.0363 |


### Between-group tests (pairwise Welch)

| pair            | coef   |     mean |     se |        t |   df |      p | test   |
|:----------------|:-------|---------:|-------:|---------:|-----:|-------:|:-------|
| Non-Free - Free | b0     | -13.0705 | 0.722  | -18.1022 |  192 | 0      | paired |
| Non-Free - Free | b_inc  |  -1.831  | 0.2638 |  -6.9405 |  192 | 0      | paired |
| Non-Free - Free | b_abs  |   0.195  | 0.2356 |   0.8276 |  192 | 0.4089 | paired |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |     p |
|:---------|:-------------|--------:|-----:|------:|
| Free     | 1 - 0        |  7.1431 |  192 | 0     |
| Free     | -1 - 0       | -5.9041 |  192 | 0     |
| Free     | 1 - -1       |  7.2676 |  192 | 0     |
| Non-Free | 1 - 0        |  2.2441 |  192 | 0.026 |
| Non-Free | -1 - 0       | -4.6133 |  192 | 0     |
| Non-Free | 1 - -1       |  5.2072 |  192 | 0     |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |       r |      p |   n |
|:---------|--------:|-------:|----:|
| Free     | -0.4759 | 0      | 193 |
| Non-Free |  0.0794 | 0.2726 | 193 |

