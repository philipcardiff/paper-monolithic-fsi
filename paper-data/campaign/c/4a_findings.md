# 4a findings: FSI3 QM-AMI on the tutorial meshes (option b)

Code: solids4foam `v2.4-1115-g1252bd2e5` (#618 transpose fix, #617
tutorial schemes; tutorial files unchanged). Driver
`./verification/Allverify --coupling monolithicAMI --levels N`, BDF2,
Δt 1/0.5/0.25 ms, t = 7 s, last 1 s analysed, as in the verification
paper. MeluXina, p201136. IQN-ILS: verification paper, tutorial meshes,
`paper-data/hronturek_fsi3_4x_findings.md` (main), its QoI table.

| QoI | QM 1x | QM 2x* | QM 4x | IQN 4x | Featflow L4 |
|---|---:|---:|---:|---:|---:|
| `u_x` mean (mm) | −2.089 | −2.579 | −2.800 | −3.085 | −2.880 |
| `u_x` amplitude (mm) | 2.017 | – | 2.651 | 2.917 | 2.720 |
| `u_y` amplitude (mm) | 28.47 | 32.81 | 34.46 | 36.23 | 34.99 |
| `u_y` frequency (Hz) | 5.600 | – | 5.500 | – | 5.46 |
| drag mean (N/m) | 453.6 | 458.8 | 460.5 | 462.1 | 460.5 |
| drag amplitude (N/m) | 21.67 | – | 27.07 | 32.76 | 27.74 |
| lift amplitude (N/m) | 219.0 | 169.1 | 159.0 | 177.0 | 153.9 |

\* 2x: agent A's PR #618 review run (8f36c7025, same solver source),
reconstructed from its published differences to IQN-ILS 2x (rounded to
0.1%); not a production row.

QM minus IQN-ILS on the same meshes (`u_x` mean, sign of the value):

| QoI | 1x | 2x* | 4x |
|---|---:|---:|---:|
| `u_x` mean | +6.4% | +7.5% | +9.2% |
| `u_y` amplitude | −4.6% | −4.0% | −4.9% |
| drag mean | −0.6% | −0.2% | −0.4% |
| lift amplitude | −4.4% | −2.9% | −10.1% |

Against Featflow level 4 at 4x:

| QoI | QM-AMI 4x | IQN-ILS 4x |
|---|---:|---:|
| `u_x` mean | magnitude −2.8% | magnitude +7.1% |
| `u_x` amplitude | −2.6% | +7.2% |
| `u_y` amplitude | −1.5% | +3.5% |
| `u_y` frequency | +0.7% | – |
| drag mean | 0.0% | +0.3% |
| drag amplitude | −2.4% | +18.1% (smoothed +10.4%) |
| lift amplitude | +3.3% | +15.0% (smoothed +7.6%) |

- **QM approaches Featflow monotonically from below** in the
  displacements (`u_y` amplitude −18.6% → −6.2% → −1.5% over 1x/2x*/4x)
  and the lift amplitude falls towards it. IQN-ILS overshoots on 4x.
- **The QM − IQN-ILS gap does not close with refinement** (`u_y`
  amplitude −4.6/−4.0/−4.9%): on 4x the IQN-ILS overshoot is the larger
  part of it. The verification paper already notes the IQN-ILS 4x is not
  asymptotic and its force amplitudes are noise-inflated; QM extrema are
  not smoothed here.
- **4d, observed order of the QM `u_x` mean** over 1x/2x*/4x: ratio of
  successive changes 0.45, order ≈ 1.15 (`u_y` amplitude: 0.38, ≈ 1.4).
  With the 2x reconstructed from rounded percentages, take it as ≈ 1, not
  as a measured order; a fixed-build QM-AMI 2x would make it firm.
- **Cost (not timing rows):** 4x 99 022 s on 32 ranks (27.5 h, 880 core-h,
  1.77 Newton per solve, max 6, no failed solve); 1x 2144 s on 8 ranks.
  IQN-ILS 4x took 40.8 h on 32 xenosim ranks.
