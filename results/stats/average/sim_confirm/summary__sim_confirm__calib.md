# sim_confirm | AVG stats

## Response variable: `calib`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |     mean |     se |        t |   df |      p |
|:-------------|:-------|---------:|-------:|---------:|-----:|-------:|
| Free         | b0     |   0.9279 | 1.1082 |   0.8373 |  192 | 0.4035 |
| Free         | b_inc  |   2.9244 | 0.4048 |   7.2242 |  192 | 0      |
| Free         | b_abs  |  -1.4539 | 0.4592 |  -3.1663 |  192 | 0.0018 |
| Non-Free     | b0     | -11.667  | 0.6894 | -16.9236 |  192 | 0      |
| Non-Free     | b_inc  |   1.6126 | 0.3009 |   5.3592 |  192 | 0      |
| Non-Free     | b_abs  |  -0.2895 | 0.4015 |  -0.7211 |  192 | 0.4717 |


### Between-group tests (pairwise Welch)

| pair            | coef   |     mean |     se |        t |   df |      p | test   |
|:----------------|:-------|---------:|-------:|---------:|-----:|-------:|:-------|
| Non-Free - Free | b0     | -12.595  | 0.9414 | -13.3796 |  192 | 0      | paired |
| Non-Free - Free | b_inc  |  -1.3118 | 0.2993 |  -4.3825 |  192 | 0      | paired |
| Non-Free - Free | b_abs  |   1.1644 | 0.5178 |   2.2487 |  192 | 0.0257 | paired |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |       t |   df |      p |
|:---------|:-------------|--------:|-----:|-------:|
| Free     | 1 - 0        |  2.78   |  192 | 0.006  |
| Free     | -1 - 0       | -6.3893 |  192 | 0      |
| Free     | 1 - -1       |  7.2242 |  192 | 0      |
| Non-Free | 1 - 0        |  3.014  |  192 | 0.0029 |
| Non-Free | -1 - 0       | -3.4124 |  192 | 0.0008 |
| Non-Free | 1 - -1       |  5.3592 |  192 | 0      |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |      p |   n |
|:---------|-------:|-------:|----:|
| Free     | 0.1296 | 0.0725 | 193 |
| Non-Free | 0.2886 | 0      | 193 |

