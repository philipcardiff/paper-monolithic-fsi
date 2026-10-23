# WP0 findings: `viscousStressTranspose` (0b blobInTreacle, 0c womersleyTube)

Run on 23 October 2026 on the mac-studio (MS, Apple M1 Ultra, shared
workstation; at most 8 ranks in use). Code: head of
`feature-petsc-snes-quasi-monolithic`, `85b0c1de6` (`git describe`
`v2.2-1713-g85b0c1de6`; the same commit describes as `v2.4-1103-g85b0c1de6`
with `--tags`), OpenFOAM v2512, PETSc 3.22.2, HYPRE 2.31.0, Apple clang 21,
`-O3`. No solver code was changed. Timings are indicative only (shared
machine). The whole package took 3.1 core-hours.

Every run is a fresh copy of the tutorial. Only case files were edited, by
`scripts/wp0_run.py`, which reuses the tutorials' verification drivers for
the set-up and, for Womersley, the analysis:

- **QM:** `./Allrun monolithic`; `viscousStressTranspose yes|no` set
  explicitly in `newtonIcoFluidCoeffs`; fluid `ddt(U) backward` (the blob
  tutorial's `fvSchemes.monolithic` says Euler; `ddt(dU)` stays Euler, as it
  enters only the approximate Jacobian, as in the Womersley and ring
  tutorials); solid `backward`. Solid block `redundant` + LU.
- **Partitioned:** strict test `requireAllResidualMeasures yes`,
  `outerCorrTolerance 1e-6`, IQN-ILS `couplingReuse 0` (head default).
  blobInTreacle also uses `outerCorrAbsoluteTolerance 1e-9` m, because near
  the steady state the strict relative test would otherwise run every step to
  `nOuterCorr` (fluidSolidInterfaces README). Robin–Neumann uses the
  tutorial's Robin tolerances.
- **blobInTreacle:** levels x1/x2/x4 (480/1 920/7 680 fluid cells), `Δt` 0.01,
  0.01 and 0.005 s, to `t = 3` s, on 1/2/4 ranks; QoI is the steady top-point
  displacement. Every run is steady (`u_x` changes by at most 2.4e-4 of its
  value over the last 0.5 s; criterion 1e-3).
- **womersleyTube:** m2 (tutorial mesh), 50 steps per period, six periods,
  last two analysed against the exact linear solution by the tutorial driver.

The partitioned blob rows in the registry were IQN-ILS with the legacy test
on `dev` code, so the partitioned arm was rerun at the head with the strict
test (`wp0-blob-iqn-x*`). Its x4 `u_x`, 0.120206 m, lies between the README's
Linux (0.120152) and macOS (0.120224) values.

## Result: QM minus partitioned

blobInTreacle: relative difference of the steady top-point displacement,
(QM − IQN-ILS)/|IQN-ILS|, same level and machine (`qois.csv`, `rel_error`).
womersleyTube: QM error minus partitioned error, both relative to the exact
solution (phases in rad). RN = Robin–Neumann.

| Case, quantity | Level | vST no | vST yes | Partitioned value |
|---|---|---:|---:|---:|
| blob `u_x` | x1 | −0.33% | −2.34% | 0.117231 m |
| blob `u_x` | x2 | −0.29% | −1.04% | 0.119691 m |
| blob `u_x` | x4 | **−0.16%** | −0.44% | 0.120206 m |
| blob `u_x` | extrapolated | −0.06% | −0.08% | 0.120343 m |
| blob `u_y` | x4 | −0.56% | **−0.13%** | −0.014027 m |
| Womersley `wallMid_amp` − RN | m2 n50 | −3.4e-4 | **−1.8e-4** | RN error 5.28e-3 |
| Womersley `wallMid_amp` − IQN | m2 n50 | −5.3e-4 | **−3.6e-4** | IQN error 5.47e-3 |
| Womersley `wallMid_phase` − RN | m2 n50 | −4.8e-4 | **+1.6e-5** | RN error −6.12e-3 |
| Womersley `attenuation` − RN | m2 n50 | −4.1e-4 | **+4.5e-5** | RN error −1.31e-2 |
| Womersley `speed` − RN | m2 n50 | −7.2e-5 | **−1.7e-5** | RN error 1.41e-3 |
| Womersley `flow_amp` − RN | m2 n50 | −4.4e-5 | −4.4e-5 | RN error −1.23e-3 |
| Womersley `profile` − RN | m2 n50 | +4.0e-5 | **+5.4e-6** | RN error 6.18e-3 |

Extrapolated blob values use the observed order of each series: IQN-ILS 2.26,
QM vST no 1.89, QM vST yes 1.67. The two partitioned couplings on Womersley
differ from each other by up to 1.9e-4 (`wallMid_amp`), the same size as the
QM vST yes difference.

## Reading

1. **The two cases point in opposite directions at a fixed mesh.** On
   blobInTreacle (steady, viscous, large wall shear), vST `no` is closer to
   the partitioned result on every level: −0.16% at x4 against −0.44%. The
   vST `yes` difference roughly halves with each refinement (2.34 → 1.04 →
   0.44%): a first-order wall error, as suspected when the default was set to
   `no` (`021affbc4`). On womersleyTube, vST `yes` is closer to both
   partitioned couplings on the wall quantities, the wave speed and the
   attenuation, by a factor of 2–30, and its difference from RN falls to the
   level of the RN/IQN-ILS spread.
2. **Both settings converge to the partitioned limit.** The extrapolated
   blob `u_x` agrees with the partitioned one to 0.06% (no) and 0.08% (yes).
   On Womersley every QM difference (at most 5.3e-4) is a tenth or less of the
   discretisation error at this level (5e-3 to 1.3e-2). Neither setting
   changes the verification conclusions.
3. **Suggested default: keep `no`.** On the case where the setting matters
   at a practical mesh (blob, 2.3% at x1), `no` is the better choice and
   converges at second order. On Womersley the gain from `yes` is below the
   discretisation error. This is for the coordinator and Philip to decide.
4. **Iterative error (B1 rule).** Tightening QM from `snes_rtol`/`snes_stol`
   1e-6, `ksp_rtol` 1e-4 to 1e-8/1e-8/1e-6 changed no QoI in any printed
   digit, on blob x1 (`u_x` 0.11685033 in both) and Womersley m2 n50 (all
   metrics). The quadratic Newton step overshoots the tolerance, and both
   settings stop after the same two iterations. The tutorial tolerances meet
   the 5% rule for these two cases.

## Cost (indicative, MS)

| Run | Iterations/step (mean/max) | Wall (s) |
|---|---:|---:|
| blob x1 / x2 / x4, IQN-ILS strict | 12.4/15, 14.8/19, 17.6/24 | 100, 288, 1506 (1/2/4 ranks) |
| blob x1 / x2 / x4, QM vST no | 2.0/3, 2.1/3, 2.6/3 | 17, 50, 386 (1/2/4 ranks) |
| Womersley m2 n50: RN, IQN-ILS, QM (no), QM (yes) | 12.2/22, 13.0/14, 2/2, 2/2 | 194, 280, 142, 144 |

## Files

- `runs.csv`, `qois.csv` (HANDOFF §6 columns), `provenance/<run_id>.json`
  (from `campaign/scripts/provenance.py`, plus the case settings).
- `scripts/wp0_run.py` (set-up and runs), `scripts/wp0_collect.py` (CSVs).
- Run directories: `MS:/Volumes/OpenFOAM/philipc-v2512/claude-runs/m-wp0/runs/`.

## Notes and open points

- The blob tutorial's `fvSchemes.monolithic` still uses Euler for `ddt(U)`.
  These runs changed it in the copies only.
- Womersley RN m2 n50 at the head reproduces the README's pre-#546 RN m2 n50
  row (`profile` 6.18e-3, `flow_amp` −1.23e-3, `wallMid_amp` 5.28e-3,
  `attenuation` −1.31e-2), so #546 does not change RN on the wedge at this
  level. This is the one A/B check the registry asked for.
- These rows also serve the verification paper's pending QM reruns (#13).
