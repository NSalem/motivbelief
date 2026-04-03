# sim_confirm | AVG stats

## Response variable: `confSym`

### Model used for participant coefficients

- `y ~ 1 + incentive + |incentive|`
- Incentive levels: -1.0, 0.0, 1.0

### Within-group tests (participant coefficients vs 0)

| choiceType   | coef   |    mean |     se |       t |   df |      p |
|:-------------|:-------|--------:|-------:|--------:|-----:|-------:|
| Free         | b0     | 78.5296 | 0.4931 | 57.8592 |  192 | 0      |
| Free         | b_inc  |  3.1486 | 0.1076 | 29.2752 |  192 | 0      |
| Free         | b_abs  | -0.2079 | 0.142  | -1.4643 |  192 | 0.1447 |
| Non-Free     | b0     | 63.55   | 0.3931 | 34.4728 |  192 | 0      |
| Non-Free     | b_inc  |  2.1015 | 0.1478 | 14.2188 |  192 | 0      |
| Non-Free     | b_abs  |  0.1057 | 0.2539 |  0.4164 |  192 | 0.6776 |


### Between-group tests (pairwise Welch)

| pair            | coef   |     mean |     se |        t |      df |      p |
|:----------------|:-------|---------:|-------:|---------:|--------:|-------:|
| Non-Free - Free | b0     | -14.9796 | 0.6306 | -23.7553 | 365.823 | 0      |
| Non-Free - Free | b_inc  |  -1.0471 | 0.1828 |  -5.7284 | 350.81  | 0      |
| Non-Free - Free | b_abs  |   0.3136 | 0.2909 |   1.0783 | 301.444 | 0.2818 |


### Paired t-tests between incentive conditions (within group)

| group    | comparison   |        t |   df |   p |
|:---------|:-------------|---------:|-----:|----:|
| Free     | 1 - 0        |  16.246  |  192 |   0 |
| Free     | -1 - 0       | -19.1569 |  192 |   0 |
| Free     | 1 - -1       |  29.2752 |  192 |   0 |
| Non-Free | 1 - 0        |   7.7072 |  192 |   0 |
| Non-Free | -1 - 0       |  -6.6325 |  192 |   0 |
| Non-Free | 1 - -1       |  14.2188 |  192 |   0 |


### Gain/Loss correlation (gain = y(1)-y(0), loss = y(-1)-y(0))

| group    |      r |      p |   n |
|:---------|-------:|-------:|----:|
| Free     | 0.2711 | 0.0001 | 193 |
| Non-Free | 0.4943 | 0      | 193 |

