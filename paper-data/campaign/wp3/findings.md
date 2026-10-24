# WP3 findings: robustness maps (3a, 3b)

Settings, failure criterion and caps: `README.md`. Data: `3a/` and `3b/`
(`runs.csv`, `qois.csv`, `provenance/`, draft maps `map_3a.pdf`,
`map_3b.pdf`). Code `85b0c1de6`; QM rows are `pre-vST-fix` (to be rerun
with the fixed build).

## 3a ringAddedMass (MeluXina 5377695)

79/80 pass. The only failure is Robin–Neumann at the strong level with 12
steps per period (200-iteration cap at step 10). Mean iterations per step:
QM 2.0 everywhere, IQN-ILS 3.0–6.1, Aitken 3.2–10.2, RN 3.0–42. All
couplings agree on ω to ~0.1% (`qois.csv`); the +6.3% error at 200 steps
is the standard solid at mesh 2, the same for every coupling. On this case
the partitioned couplings (with predictor and the strict test) survive even
μ ≈ 100: the map separates them by iterations, not by failure.

## 3b collapsibleChannel (XenoSim 13279, 4.6 h, 55.7 core-hours CPU)

| Coupling | Passes (of 20) | Failures |
|---|---:|---|
| QM | 15 | Δt 0.025: all five densities stop at t = 0.275 s in the fluid mesh-motion SNES (`mesh`, `DIVERGED_LINEAR_SOLVE` of the pseudo-solid motion solver; the coupled Newton solve converged in 3 iterations per step up to then) |
| RN | 11 | ρs/ρf 0: floating-point exception on the first coupling iteration at every Δt (the Robin coefficient ∝ wall density vanishes; `nan`); ρs/ρf 0.01: cap at Δt 0.025, 0.00625, 0.003125 |
| IQN-ILS | 9 | cap at ρs/ρf ≤ 0.1 for Δt ≤ 0.00625 (ρs/ρf 0: Δt ≤ 0.0125), and at ρs/ρf 1, Δt 0.003125 (t = 0.23 s), as in the verification README |
| Aitken | 7 | cap at every Δt for ρs/ρf ≤ 0.1, except ρs/ρf 0 at Δt 0.025 |

QM needs 2.0–3.0 Newton iterations per step in every passing cell,
independent of the density; the partitioned couplings need 8–98 coupling
iterations per step where they pass. Partitioned failures come within the
first few steps (cap at the 200-iteration limit); the smaller the time
step, the earlier the failure, the classical added-mass trend.

Trough of the wall midpoint (ρs/ρf 1, against oomph-lib): partitioned
−1.79/−0.78/−0.51/−0.43% at Δt 0.025/0.0125/0.00625/0.003125; QM
−0.97/−0.71/−0.65% (Δt 0.0125 → 0.003125). QM and partitioned differ by
about 0.2 points at the small steps (different solid formulation —
velocity TL vs displacement TL with linear reconstruction — and the
conservative AMI traction; QM `pre-vST-fix`). ρs/ρf 0 against the massless
reference: QM −0.95/−0.70/−0.64%.

## Open points

- The QM Δt 0.025 failures are mesh motion, not coupling; a more robust
  mesh-motion set-up (or Euler start) might remove them. Not investigated
  (no QM runs until the vST fix).
- RN is undefined at ρs = 0 with the secant Robin coefficient; the map
  should say "not applicable" rather than "failed" if Philip prefers.

## QM failure at Δt 0.025 (collapsibleChannel): mesh motion, not coupling

Diagnostic copy on the #618 build (`wp3-coll-qm-dt0.025-rho1-r618-diag`,
same set-up, fields written every step; nothing tuned). Files:
`3b/meshdiag_dt0.025/` (from `scripts/wp3_meshdiag.sh`).

- The run stops at t = 0.275 s, as before #618 and for every density, in
  the first linear solve of the fluid mesh-motion problem (pseudo-solid,
  `solids4foamSolidModel` motion solver, neo-Hookean, PETSc SNES with a
  matrix-free operator, `lgmres` + block-Jacobi/LU,
  `snes_lag_preconditioner -2` persisting, i.e. the preconditioner is
  built once and then frozen): `DIVERGED_ITS` after 10 000 Krylov
  iterations, SNES reason `DIVERGED_LINEAR_SOLVE`.
- Mesh-motion history (`d_history.csv`): initial residual per step
  1.1e-3, 3.8e-3, 1.1e-2, 2.3e-2, 4.3e-2, 7.4e-2, 0.13, 0.23, 0.52, then
  5.6 at t = 0.275 s; Krylov iterations of the first linear solve 14, 14,
  14, 15, 16, 18, 21, 29, 49, then 10 000.
- Mesh at the last state before the failure (t = 0.25 s): `checkMesh`
  OK, max skewness 0.015, min volume 1.84e-4 (max 1.95e-4);
  J = V/V0 min 0.941, no cell below 0.1 (`jacobian.json`). The state at
  the failed solve itself is not written (the solve aborts).
- The coupled problem is regular up to then: 3 Newton iterations per step,
  wall midpoint −0.0013 → −0.0586 m smooth and monotonic.
- Reading: the mesh is not tangled; the mesh-motion linear solver fails as
  the pseudo-solid departs from the configuration of its frozen
  preconditioner, with per-step increments that are four times those at
  Δt 0.00625 (which passes). The failure belongs to the mesh-motion
  solver set-up, not to the quasi-monolithic coupling.

RN at ρs/ρf = 0 is now recorded as `n/a` (not applicable: the Robin
coefficient scales with the wall density), grey marker in the map.

## QM arms rerun on the #618 build (4ae081609 + #617 schemes in the copies)

XenoSim job 13357, 40 runs (`3a/qm618/`, `3b/qm618/`; side-by-side table
`qm618_comparison.txt`). The maps (`map_3a`, `map_3b`) now show these
rows; the pre-#618 QM rows stay in `3a/runs.csv` and `3b/runs.csv`,
marked superseded.

- No status changes: 3a QM passes all 20 cells; 3b QM passes the 15 cells
  with Δt ≤ 0.0125 and fails `mesh` at t = 0.275 s for all five densities
  at Δt 0.025, as before.
- Newton iterations per step unchanged (ring 2.00 everywhere; collapsible
  2.0–3.0, within ±0.05 of the pre-#618 means).
- QoIs move by at most 5e-6 relative: ring ω (≤ 4.9e-6), collapsible
  trough (≤ 2.8e-6). #618 and the #617 scheme alignment do not affect
  these two cases (inviscid ring; Re = 50 channel, where the transpose
  term is small). In particular, the ~0.2-point QM–partitioned trough gap
  in 3b (−0.65% against −0.43% at Δt 0.003125) is not a transpose-term
  effect.

## QM Δt 0.025 failure: debugging (24 Oct, Philip via coordinator)

Runs on the #618 build, fluid L2, AMI 640×8, ρs/ρf 1 (`3b/meshmotion_debug/`).

1. **Diffusion mesh motion does not fix it.** `diffusionHyperElastic` with
   `diffusivity quadratic inverseDistance (interface)` (as TurekHron2006,
   same solid model, same lagged block-Jacobi/LU) passes t = 0.275 s but
   fails the same way one step later (t = 0.3 s, `DIVERGED_LINEAR_SOLVE`).
   Mesh-motion Krylov counts of the first linear solve per step: 18 (to
   t = 0.15), 23, 28, 36, 53, 114, then failure; initial residual roughly
   doubles each step (5.3, 8.7, 14, 25, 51, 133).
2. **GMRES stagnates, it is not just slow.** With the neo-Hookean law and
   `ksp_monitor_true_residual` on D: at t = 0.275 s the true residual falls
   to 1.4e-3 of its initial value within ~300 iterations and then stays
   there to 10 000 (rtol not reached). Earlier steps converge in 14–49.
3. **Not mesh quality, not the interface data.** At t = 0.25 s J_min = 0.94,
   skewness 0.015 (`checkMesh` OK); interface displacement and velocity
   profiles are smooth (relative second difference ≤ 0.2%).
4. **The degradation tracks displacement × increment** (all at ρs/ρf 1):
   the step's initial mesh-motion residual and the Krylov count rise with
   the wall deflection, scale with Δt (Δt 0.0125 ≈ ½, Δt 0.00625 ≈ ¼ of
   the Δt 0.025 values at the same time), peak near the trough (Δt 0.0125:
   36 iterations at t = 0.35 s) and fall again on the rebound.
5. **Candidate root cause (code, not tested).** The mesh-motion pseudo-solid
   (`solids4foamSolidModel` → `nonLinGeomTotalLagTotalDispSolid`, region
   `fluid`) is built on the fluid mesh that it moves:
   `meshMotionSolidModelFvMotionSolver::solve()` calls `movePoints` with the
   current points and then `evolve()`, and the total-Lagrangian residual
   uses `mesh().Sf()`, `mesh().magSf()` and `fvc::interpolate(J*Finv.T()) &
   mesh().Sf()` on that moved mesh, while `D` is the total displacement from
   `points0`. If so, the deformation is counted twice, the operator departs
   from the frozen compact preconditioner (built on the first geometry) as
   the total displacement grows, independent of the law — consistent with
   1, 2 and 4. Testing it needs a solver change (e.g. evaluate the
   pseudo-solid on `points0`), which is outside the run agent's remit.
