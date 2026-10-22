# Suspected solver issue: quasi-monolithic run does not restart consistently (fluid mesh motion)

Status: reported under handoff Section 9; not worked around in code. The
campaign avoids restarts instead (B1 windows run from t = 0).

## Code and machine

solids4foam `v2.2-1692-g257b2e564`, OpenFOAM v2512, PETSc 3.24.1, XenoSim,
serial. Case: `cavityFlexibleBottom`, `./Allrun monolithic` set-up, mesh
factor 4 (B1 level 3), Δt = 0.5 s, `ddt(U) backward`, inlet ramp 20 s.

## What happens

1. Spin-up from t = 0 to t = 100 s (200 steps) completes normally: 2.23
   Newton iterations per step; at the last step the fluid mesh-motion SNES
   (`Solving the momentum equation for D`) starts at function norm
   3.27e-3 and converges in 2 iterations, 19 and 18 Krylov iterations.
2. Restarting from t = 100 (`startFrom latestTime`, same set-up, S0 solid
   PC, 1 rank), the first mesh-motion SNES at t = 100.5 starts at function
   norm **3.413470681598e+00**, about 1000 times larger, and its first
   linear solve does not converge (`DIVERGED_ITS iterations 10000`;
   `DIVERGED_LINEAR_SOLVE`), so the run stops ("Stopping because of the
   PETSc SNES error").
3. The same initial norm, to all printed digits, is obtained
   - with `restart no` in the mesh-motion solid's coefficients (spin-up
     wrote only the solid region's restart fields), and
   - with `restart yes` in both the solid and the mesh-motion solid during
     the spin-up, so that `D_0_0`, `DD`, `DD_0`, `grad(D)_0`, `pointD_0`,
     `pointDD` etc. are present in `100/fluid`.

   So the missing restart fields are not the cause.

Interface offset at the start of the restart: max 1.33e-6 m (normal).
Mesh-motion model: `nonLinearGeometryTotalLagrangianTotalDisplacement`,
neo-Hookean (μ = 1, K = 3), via `meshMotionSolidModelFvMotionSolver`
(`curPoints = points0 + pointD`).

## Suspicion (not verified)

On restart the mesh-motion total-Lagrangian solid is constructed on the
fluid mesh read from `100/fluid/polyMesh` (deformed points), while its
displacement `D` is measured from `points0`. If the model takes the current
mesh as its reference configuration, the stored total displacement is
applied a second time, which would give an O(1) residual. 3dTube's mesh
motion (`linearGeometryTotalDisplacement`) likely behaves the same way (not
tested).

## Evidence (XenoSim)

- Spin-up: `~/OpenFOAM/philipc-v2512-qmpaper/runs/b1/spin-cav/log.solids4Foam`
  (job 13039); earlier spin-up with solid-only restart fields:
  `runs/b1/spin-cav-v1-solidrestart/` (job 13027).
- Restart with `restart no` on the mesh motion: `runs/b1/failed-20261022/
  b1-cav-S0-p1-restartno/log.solids4Foam` (job 13036, cancelled while
  stuck in the first linear solve).
- Restart with all restart fields: job 13042, log in the session scratchpad
  (`rtest-cav/log.solids4Foam`), FOAM FATAL at
  `foamPetscSnesHelper.C:2457`.

## Impact on the campaign

None on paper results (no paper run restarts). B1 windows now run from
t = 0 to t0 + 50 Δt and are analysed over the last 50 steps
(`b1_setup.py window` default; `b1_analyse.py` window filter). Long R
runs that would need a restart (Slurm time limits) are affected; worth
fixing before the tag.

## Reproduce

```bash
python3 campaign/scripts/b1_setup.py spinup cav spin-cav    # then ./Allrun monolithic in spin-cav
python3 campaign/scripts/b1_setup.py window spin-cav w --config S0 --ranks 1 --steps 3 --restart
cd w && solids4Foam    # fails at t = 100.5 in the mesh-motion SNES
```
