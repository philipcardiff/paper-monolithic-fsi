# WP3 robustness maps (3a ringAddedMass, 3b collapsibleChannel)

Run agent B, from 23 October 2026. Code: head of
`feature-petsc-snes-quasi-monolithic`, `85b0c1de6`
(`v2.2-1713-g85b0c1de6`), the R0 build on MeluXina
(`/project/home/p201287/philip/qm-head`). No solver code changed. Every run
is a fresh copy of the tutorial, configured with the tutorial's own
verification driver; only case files are edited (`scripts/wp3_setup.py`).

## Failure criterion (fixed before the runs, 23 Oct)

Identical for all four couplings and both maps; applied by
`scripts/wp3_post.py` in this order:

| Status | Meaning |
|---|---|
| `nan` | a non-finite value in the solver log or the monitored displacement history |
| `cap` | a step reached the coupling cap: partitioned, 200 coupling iterations (`nOuterCorr 200`; the solver stops with "FSI coupling did not converge"); quasi-monolithic, the coupled Newton solve did not converge (`snes_max_it 20`, or any other negative SNES reason) |
| `newton` | a solid Newton (SNES) failure in a partitioned step, or a mesh-motion SNES failure, that ended the run |
| `diverged` | ring: ovalling displacement above 10 times its first peak; collapsibleChannel: wall displacement above the channel height (1 m) |
| `timeout` | the run reached its wall-clock limit (recorded, not counted as a coupling failure) |
| `crash` | any other abnormal end |
| `pass` | reached the end time with none of the above |

The time of failure (`t_reached`) and the mean and maximum iterations per
step (coupling iterations for partitioned runs, Newton iterations of the
coupled system for QM) are recorded for every run.

## Common settings

- Partitioned: strict coupling test (`requireAllResidualMeasures yes`),
  `nOuterCorr 200`, the tutorial's `outerCorrTolerance` (ring 1e-6,
  collapsibleChannel 1e-4; Robin–Neumann also its Robin tolerances),
  IQN-ILS `couplingReuse 0`. Aitken uses the IQN-ILS file's predictor and
  initial relaxation (ring 0.05; collapsibleChannel the driver's value scaled
  with Δt², as for IQN-ILS).
- Quasi-monolithic (QM): `viscousStressTranspose no` (explicit), tutorial
  PETSc options (`snes_rtol`/`snes_stol` 1e-6, `ksp_rtol` 1e-4, solid block
  `redundant` + LU), `snes_max_it 20`.
- Schemes: fluid and solid `backward`; no limiters; gradient `leastSquares`
  and `div(phi,U) Gauss linear` in both arms (decision of 23 Oct; for the
  collapsibleChannel the partitioned fluid file's `Gauss linear` gradient is
  changed to `leastSquares`). Recorded per run in `wp3_case.json` and in the
  `runs.csv` notes.
- MeluXina, project p201136, one exclusive node per map with the serial runs
  packed as a task farm (`jobs/wp3_farm.sh`); wall times are indicative (runs
  share the node).

## 3a ringAddedMass

{Aitken, IQN-ILS, RN, QM} × {12, 25, 50, 100, 200 steps per period} ×
{weak, moderate, strong, extended}, two periods, standard solid,
refinement-factor-2 mesh, conformal (`directMap`). The extended level (Philip,
23 Oct) is ρf = 14 000 kg/m³, mass ratio μ = 100.8, exact ω = 0.253616 rad/s
(from `ring_exact_frequencies.py`), ten times the strong level.

## 3b collapsibleChannel

{Aitken, IQN-ILS, RN, QM} × Δt {0.025, 0.0125, 0.00625, 0.003125} ×
ρs/ρf {10, 1, 0.1, 0.01, 0}, to t = 0.75 s (end of the first-trough window
0.3–0.75 s), fluid level 2, solid 640 × 8 through AMI (B2: trough −1.91% at
fluid level 2, −1.83% at level 4); QM with conservative traction transfer as
in B2. ρf = 1, so ρs/ρf is set by the wall density.
