# sim_intent | AVG stats

## Response variable: `correct`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 73.899  | 0.6766 | 35.3231 |  192 | 0      |
| Free         | b_inc  |  0.1554 | 0.2214 |  0.7019 |  192 | 0.4836 |
| Free         | b_abs  |  0.1295 | 0.4093 |  0.3164 |  192 | 0.752  |
| Non-Free     | b0     | 74.0933 | 0.3288 | 73.2686 |  192 | 0      |
| Non-Free     | b_inc  | -0.1166 | 0.2494 | -0.4675 |  192 | 0.6407 |
| Non-Free     | b_abs  |  0.3562 | 0.4096 |  0.8696 |  192 | 0.3856 |


### Between-group tests (pairwise Welch)

| pair            | coef   |    mean |     se |       t |      df |      p |
|:----------------|:-------|--------:|-------:|--------:|--------:|-------:|
| Non-Free - Free | b0     |  0.1943 | 0.7523 |  0.2583 | 277.914 | 0.7964 |
| Non-Free - Free | b_inc  | -0.272  | 0.3335 | -0.8156 | 378.709 | 0.4152 |
| Non-Free - Free | b_abs  |  0.2267 | 0.5791 |  0.3914 | 384     | 0.6957 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  0.5985 |  192 | 0.5502 |
| Free     | -1 - 0       | -0.057  |  192 | 0.9546 |
| Free     | 1 - -1       |  0.7019 |  192 | 0.4836 |
| Non-Free | 1 - 0        |  0.503  |  192 | 0.6155 |
| Non-Free | -1 - 0       |  0.9793 |  192 | 0.3286 |
| Non-Free | 1 - -1       | -0.4675 |  192 | 0.6407 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |   p |   n |
|:---------|-------:|----:|----:|
| Free     | 0.5478 |   0 | 193 |
| Non-Free | 0.4593 |   0 | 193 |

