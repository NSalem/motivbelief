# Calibration mixed-effects (merged data)

Model: `conf ~ acc_c * incentive + (RE | participant)`
Cells: subject × coherence × incentive (pooled correct/error).
`acc_c` = accuracy centered within Free / Non-Free.
`incentive` coded linearly (−1, 0, +1).

## Free

- Subjects: 193
- Cells: 2895
- RE formula used: `~ acc_c * incentive`
- Converged: True
- LLF: -10306.19

| term | estimate | SE | z | p |
|---|---:|---:|---:|---:|
| `Intercept` | 72.4203 | 0.8487 | 85.33 | 0 |
| `acc_c` | 39.2463 | 1.9687 | 19.93 | 2.028e-88 |
| `incentive` | 3.3269 | 0.3302 | 10.08 | 7.047e-24 |
| `acc_c:incentive` | -4.8941 | 0.9533 | -5.13 | 2.842e-07 |

## Non-Free

- Subjects: 296
- Cells: 4440
- RE formula used: `~ acc_c + incentive`
- Converged: True
- LLF: -16421.97

| term | estimate | SE | z | p |
|---|---:|---:|---:|---:|
| `Intercept` | 66.0699 | 0.3905 | 169.20 | 0 |
| `acc_c` | 52.5621 | 1.2127 | 43.34 | 0 |
| `incentive` | 1.2049 | 0.1933 | 6.23 | 4.606e-10 |
| `acc_c:incentive` | -0.0493 | 0.8904 | -0.06 | 0.9559 |

