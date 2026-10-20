# B1: preconditioner of the solid block (partial: ringAddedMass only)

Code `257b2e564`, MeluXina (AMD EPYC 7H12), one exclusive node per case,
runs one after another, ranks mapped and bound to cores. Set-up:
`campaign/scripts/b1_setup.py`; job: `campaign/jobs/b1.sh`; analysis:
`campaign/scripts/b1_analyse.py` → `b1_windows.csv`; per-run status:
`status.txt`; provenance: `provenance/<run_id>.json`.

Configurations of the `UpU` solid block: S0 `redundant` + LU (tutorial
default); S1 BoomerAMG with the membraneRoof solid settings; S2 `bjacobi` +
LU per rank; S0tight = S0 with `snes_rtol` and `snes_stol` 1e-6 → 1e-8.
All other options are the tutorial's (`ksp_rtol 1e-4`, LGMRES, Schur
fieldsplit for the fluid).

## ringAddedMass

Moderate added mass (ρf = 140), mesh factor 2, standard solid, 50 steps per
period, 2 periods (100 steps) from t = 0. Job 5364389.

QoI difference = largest difference over the 100 steps of the monitored
displacement components (x and y at the ring point), relative to their
largest magnitude (3.84e-4 m), against S0tight at the same rank count.

| Config | Ranks | Newton/step | Krylov/Newton | Clock (s) | QoI diff vs S0tight |
|---|---:|---:|---:|---:|---:|
| S0 | 1 | 2.00 | 23.9 | 39 | 9.4e-7 |
| S1 | 1 | 2.00 | 47.4 | 54 | 1.7e-5 |
| S0tight | 1 | 2.99 | 28.9 | 56 | – |
| S0 | 4 | 2.00 | 24.5 | 17 | 1.8e-6 |
| S1 | 4 | 2.00 | 53.4 | 33 | 5.5e-5 |
| S2 | 4 | 2.00 | 56.6 | 32 | 6.9e-6 |
| S0tight | 4 | 3.00 | 29.5 | 30 | – |

(Source: `b1_windows.csv`.)

- **Iterative floor of S0:** 9.4e-7 (serial) and 1.8e-6 (4 ranks) of the
  displacement amplitude.
- **S1 (BoomerAMG) fails the acceptance test.** Its QoIs differ from the
  tight reference by 1.7e-5 and 5.5e-5, 18 and 30 times the S0 floor, on all
  four monitored components alike (not a near-zero component). It also costs
  more: twice the Krylov iterations per Newton iteration and 1.4 to 1.9 times
  the clock time.
- **S2 (bjacobi + LU) also exceeds the floor**, by a factor of 4 (6.9e-6 at
  4 ranks), and costs 1.9 times S0.
- All configurations converge in 2 Newton iterations per step; the SNES
  test (`snes_rtol 1e-6` relative to the initial residual) is met by all of
  them, but with a different iterative error, because the Newton step is
  only solved to `ksp_rtol 1e-4` and the error left after two Newton
  iterations depends on the preconditioner. The S0 floor therefore measures
  S0's iterative error only; other preconditioners at the same SNES tolerance
  have a larger one.
- Size in context: 5.5e-5 of the amplitude is small in absolute terms but of
  the same order as the ring's recorded wet/dry ratio errors
  (0.002–0.005%, ringAddedMass verification README), so for this case the
  preconditioner choice is not negligible at the tutorial tolerance.

**Handoff Section 8 trigger:** "A preconditioner or rank count changes a
converged QoI by more than the iterative floor." Reported; S1 and S2 are not
adopted on this evidence. Rank count alone (S0, 1 against 4 ranks) changes
the QoI by the same order as the floor itself (both at most 1.8e-6 from the
tight runs).

## Not yet run

- cavityFlexibleBottom L3: spin-up to t = 100 s completed (job 5364387,
  25 min serial, 2.25 Newton/step, `status.txt`); windows job 5364390 is
  **held** (project budget, see the progress log).
- 3dTube L2: serial spin-up 5364388 **cancelled** after 3 min (MeluXina
  bills a whole node for a 1-core job; with the budget nearly exhausted, the
  spin-up should run in parallel); windows job 5364391 held.

## Open questions for Philip

1. Should the acceptance test compare each configuration with its own tight
   run (its own floor) rather than S0's floor? At the tutorial tolerances,
   any preconditioner other than S0 will fail S0's floor on the ring.
2. Alternatively, tighten `ksp_rtol` (or `snes_rtol`) campaign-wide so that
   the converged QoIs become preconditioner-independent; this changes cost
   numbers.
