# Suspected solver issue: a quasi-monolithic FSI3 restart does not reproduce the continuous run (newtonIcoFluid `backward` history not written)

Status: **causes found; fix in solids4foam PR #624**
(https://github.com/solids4foam/solids4foam/pull/624, branch
`fix/monolithic-restart-backward-fluid`, commits d11ccbc38 and b96e1e6ff on
18a24427f, into `feature-petsc-snes-quasi-monolithic`; not merged). The
missing backward history in the hypothesis below is **not** a cause: a
restart needs only `U` and `U_0`, and `fvMesh` sets up `V00` when it reads
`V0`. There were three defects:

1. **The fluid `U` lost its registry name to the mesh-motion solid's `U`
   (the viscous force jump).** On a restart with `restart yes`, the
   mesh-motion solid (built with the fluid mesh, before the fluid fields)
   creates its velocity `"U"` in its constructor (#555). That field reads
   the fluid's `U` file and registers `"U"`/`"U_0"` first, so the fluid's U
   is not registered. As a result:
   - `forces` computed the viscous force from the mesh-motion velocity
     (internal field 0, wall values set). The pressure force and the
     dynamics were right.
   - Every `U`/`U_0` written after a restart is the mesh-motion velocity.
     `r4-fsi3-mono-1x-rs5/5.05/fluid/U` on MeluXina has
     `internalField uniform (0 0 0)`.
   - A restart of a restarted run starts from zero fluid velocity: the SNES
     fails within 2-4 steps (below).
2. **Stiffness scale factor recomputed on the deformed mesh.** FSI3 sets
   `diffusivity quadratic inverseDistance (plate cylinder)`. The mesh-motion
   stiffness factor is computed once, from the mesh at construction: on a
   restart that is the deformed mesh of the start time. This is the main
   cause of the first-step norm difference. The cavity `.monolithic`
   variant has no diffusivity, which is why the #616 check passed.
3. **`impK`/`interpolate(impK)` of the mesh-motion solid frozen at
   construction.** The interpolation weights come from the deformed mesh on
   a restart. They enter the stabilisation term of the residual.

Fix: `fluidModel` makes its `U`, `p` and their old-time levels the
registered objects. With `restart yes`, `stiffnessScaleFactor`, `impK` and
`interpolate(impK)` are written, and they are read back on a restart.

The cavityFlexibleBottom check of #616 had used Euler (the tutorial's
`.monolithic` schemes). The B1 re-check used backward. Both had defect 1
(viscous force wrong after a restart) but not 2, because the cavity sets no
diffusivity. The #616 check compared only displacements and norms.

What remains after the fix is solver state that a restart cannot restore:

- The mesh-motion solid's stabilisation Jacobian
  (`diffStencilLaplacianStab::vectorJacobian`) is cached at its first use,
  on the undeformed mesh in a continuous run and on the deformed mesh after
  a restart.
- The `snes_lag_preconditioner -2 persists` preconditioner of the mesh
  motion behaves the same way.

Both change only the preconditioner. After the first step, the restart then
differs from the continuous run at the level of the solver tolerances.

## Verification (fix build; scripts `pair.sh`/`cmp.py` in the run dirs below)

XenoSim `~/OpenFOAM/philipc-v2512-qmrs2/runs/<name>/{cont,rs}`; MeluXina
`/project/home/p201287/philip/qm-rs2/runs/<name>/{cont,rs}` (MeluXina
run dirs deleted after the check; the numbers are from `cmp.py`). FSI3
monolithic, fluid ddt backward, binary output, `writePrecision 12`. Early
restarts: 1x at 0.015 (60 steps), 2x (Δt 5e-4) at 0.02 (100 steps). Large
deformation: continuous 4 -> 4.08 from the R4 campaign's t = 4, restart at
4.03 (50 steps at 1x, 100 at 2x).

| run (XenoSim/MeluXina dir) | first-step initial norm, motion / Up | max rel. diff, pressure force | max rel. diff, viscous force | max abs. displacement diff |
|---|---|---|---|---|
| 1x serial, before (X `base-fsi3`) | 3.0e-4 / 5.2e-7 | 5.3e-7 | 1.03 | 4.3e-10 m |
| 1x serial, after (X `final-fsi3`) | identical / identical | 5.4e-7 | 1.1e-8 | 4.1e-10 m |
| 1x 4 ranks, after (X `prodp-fsi3`) | identical / 9e-13 | 3.3e-7 | 1.9e-8 | 2.5e-10 m |
| 2x serial, before (M `base-2x-s`) | 1.8e-4 / 9.8e-8 | 4.7e-7 | 1.07 | 1.2e-10 m |
| 2x serial, after (M `fix-2x-s`) | identical / 3e-13 | 3.7e-7 | 6.4e-9 | 6.4e-11 m |
| 2x 4 ranks, after (M `fix-2x-p4`) | identical / 3e-13 | 4.1e-7 | 1.4e-8 | 1.1e-10 m |
| 1x large def. serial, before (M `base-1x-late-s`) | restart of a restart: Up 1.01e6 vs 4.45e5, SNES fails at step 4 | | | |
| 2x large def. 4 ranks, before (M `base-2x-late-p4`) | Up 7.24e5 vs 3.43e5, SNES fails at step 2 | | | |
| 1x large def. serial, after (M `fix-1x-late-s`) | identical / 3.0e-8 | 3.1e-8 | 2.8e-8 | 1.5e-10 m |
| 1x large def. 4 ranks, after (M `fix-1x-late-p4`) | identical / 2.5e-7 | 1.4e-7 | 1.0e-7 | 3.2e-10 m |
| 2x large def. 4 ranks, after (M `fix-2x-late-p4`) | identical / 1.7e-8 | 1.3e-7 | 1.8e-8 | 7.5e-11 m |
| cavity Euler, before (X `base-cav`) | identical / 3e-13 | 9.5e-11 | 1.02 | 3e-12 m |
| cavity Euler, after (X `final-cav`) | identical / 3e-13 | 8.4e-11 | 1.0e-10 | 3e-12 m |
| cavity backward, after (X `final-cavbw`) | identical / 1.6e-10 | 7.1e-8 | 6.9e-8 | 1.9e-8 m |
| cavity backward 4 ranks, after (X `prodp-cavbw`) | identical / 1.5e-9 | 2.7e-10 | 1.8e-10 | 9e-12 m |

("identical" means all 13 printed digits. The cavity backward serial
difference of 1e-7 appears at t = 20 s, where one Up solve takes one more
Newton iteration in the restart. Before that the differences are about
1e-10.)

Mechanism check (diagnostic build, not in the PR): the stabilisation
Jacobian was rebuilt on every call and the preconditioner lag removed, in
both runs. Then the early 1x restart is **bit for bit identical** to the
continuous run over 60 steps in serial and with 4 ranks (X `diag-fsi3`,
`diagp-fsi3`): every SNES norm, every force (pressure and viscous) and
every displacement.

In the large-deformation 1x serial case (X `diag-1x-late-s`), every norm is
identical for 47 steps. A round-off difference (6e-10) appears at step 49.
With 4 ranks (X `diag-1x-late-p4`) the first Up norm differs by 4e-12. The
cavity norms agree to ≤ 5e-12 at every step (X `diag-cav`, `diag-cavbw`).
These round-off seeds were not traced.

Continuous runs unchanged bit for bit (fix vs 18a24427f): 1x 75 steps (X
`base-fsi3/cont` vs `final-fsi3/cont`) and 2x 140 steps (M `base-2x-s/cont`
vs `fix-2x-s/cont`). Every solve has identical norms and Krylov counts,
`force.dat` and displacement output are identical, and all written fields
are byte-identical. The only additions are the three restart files.

Consequences for R4/R5 data written before the fix:

- Viscous forces from any restarted monolithic run are wrong (pressure
  forces and displacements are not affected by this).
- Every `fluid/U` and `fluid/U_0` written by a restarted run is the
  mesh-motion velocity, so do not restart again from those times.
- The first steps after a restart also used a mesh-motion stiffness factor
  computed on the deformed mesh. This changes the mesh motion, not the
  physics, but it is not the continuous run.
- A restart from a time written before the fix still recomputes the
  stiffness factor (the fixed code warns), so an exact restart needs a run
  made with the fix.

---

Original report (R4, 25 Oct 2026) below.

Status (original): open; reported to the coordinator (R4, 25 Oct 2026). Not worked
around. Results that start from a restart are flagged in `runs.csv` until
Philip decides.

## Code and machine

solids4foam `feature-petsc-snes-quasi-monolithic` at `v2.2-1734-g18a24427f`
(includes the restart fix #616), OpenFOAM v2512, PETSc 3.22.0, MeluXina
(`/project/home/p201287/philip/qm-final`), serial, farm job 5384147.

## Minimal case and commands

TurekHron2006 FSI3, conformal 1x mesh (`Allverify --coupling monolithic`
set-up via the driver's `configure_case()`), Δt = 0.001 s, fluid
`ddt(U)`, `ddt(dU)`, `ddt(p)` `backward` (tutorial), `restart yes` in the
coefficients of both the plate solid and the fluid mesh-motion solid,
`writeFormat binary`, fields every 1000 steps.

```bash
python3.12 qm_setup.py fsi3 r4-fsi3-mono-1x --coupling mono --level 1 --ranks 1 \
    --tol snes_rtol=1e-6,snes_stol=1e-6,ksp_rtol=1e-4      # continuous 0 -> 7 s
python3.12 qm_setup.py restart r4-fsi3-mono-1x r4-fsi3-mono-1x-rs5 --from 5 --end 5.05
# each run: run_task.sh (Allrun monolithic set-up, then solids4Foam)
```

## Expected and observed

Expected (as for the cavity check of #616): the first restarted step has the
same SNES norms as the continuous run.

Observed, first step after t = 5 s (`log.solids4Foam` of each run, the
mesh-motion `D` solve then the coupled `Up` solve):

```
continuous (r4-fsi3-mono-1x)            restart (r4-fsi3-mono-1x-rs5)
D   0 SNES Function norm 1.441124461318e-03   1.463739361663e-03
D   1 SNES Function norm 1.388168115170e-05   1.467798387035e-05
Up  0 SNES Function norm 4.133160357315e+05   4.205576897436e+05
Up  1 SNES Function norm 1.371309725306e+02   1.257456547446e+02
Up  2 SNES Function norm 2.894259536906e-02   3.694935979689e-02
```

The first residuals differ by 1.6-1.8%. Over the 50 restarted steps the
point-A displacement differs by up to 2.5e-6 m (u_y amplitude about
0.024 m at this level) and the force on plate and cylinder by up to 0.17 N
(lift amplitude about 5.8 N for the 0.015 m depth).

## What the time directory holds

`5/fluid` has `U`, `U_0`, `p`, `p_0`, `phi`, `meshPhi`, `V0`, `polyMesh/points`
and the mesh-motion solid's `D`, `D_0`, `D_0_0`, `DD*`, `pointD*`; it has no
`U_0_0`, `p_0_0`, `phi_0` or `V00`. `5/solid` has the full solid history
(`D_0_0_0`, `U_0`, ...). `newtonIcoFluid` has no restart handling (no
`restart` switch; nothing sets the old-old fields to be written).

## Hypothesis

With `backward` for `ddt(U)`, `ddt(dU)` and `ddt(p)`, the first restarted
step lacks U^(n-2) and p^(n-2) (and the old-old cell volumes of the moving
mesh) and so is not the step of the continuous run. The #616 check on
cavityFlexibleBottom may not have exercised this (its first restarted step
matched to 11 digits). A fix would write the fluid old-old fields
(`U_0_0`, `p_0_0`, and `V00`/`meshPhi` history) when `restart yes` is set,
as the solid models do.

## Impact on R4/R5

- Accuracy runs: none (continuous from t = 0).
- Tolerance sweep and timing windows start from restarts. All variants of
  the sweep start from the same restarted state and the QoIs are taken after
  1 s (about 6 periods) on the self-excited limit cycle; the sweep includes
  a restart at the production tolerance (`r4-fsi3-mono-2x-s1e-6`) whose QoIs
  are compared with the continuous run to show whether the restart
  perturbation matters. Timing windows measure cost only.
- 3dTube (a transient, not a limit cycle) is more sensitive: R5 scaling and
  ablation windows from restarts would compare variants from the same
  restarted state only.

## Addendum (25 Oct, 18:50): the viscous force output changes after a restart

The 2x tolerance-sweep run at the production tolerance
(`r4-fsi3-mono-2x-s1e-6`, restart from `r4-fsi3-mono-2x` at t = 5 s, same
settings) reproduces the continuous run's displacement QoIs over 6-7 s to
1e-4 (u_x mean +2.7e-4, u_y amplitude -1.1e-4, frequency +5e-5), but not
the forces: drag mean -5.9%, drag amplitude +4.9%, lift amplitude -28%
(`qois.csv`). In `postProcessing/fluid/forces/*/force.dat` (N, divided here
by the 0.015 m depth) the PRESSURE force agrees to 0.1 N/m at every compared
time, while the VISCOUS force jumps at the first restarted step and stays
different:

```
t        continuous: pressure (x, y)   viscous (x, y)    restart: pressure (x, y)   viscous (x, y)
5.0005   443.16  -111.31               30.58   1.54      443.47  -111.37            7.50   38.91
5.01     433.26  -162.23               26.67   0.15      433.26  -162.22            0.53   54.84
6.0      433.25   217.80               21.12   0.62      433.31   217.91          -11.45  -65.69
6.9      457.37   215.56               23.65   0.52      457.53   215.23          -10.56  -54.18
```

So the dynamics are the same (pressure, displacements) but the viscous
stress used by the `forces` function object differs after a restart
(plausibly a field it looks up, e.g. the effective viscosity or velocity
gradient registered by `newtonIcoFluid`, is read from the time directory or
not recreated). Which output is correct is not established here; the
continuous run's small viscous lift (about 1 N/m) is the plausible one.
Consequence: force QoIs from restarted monolithic runs are not usable;
displacement QoIs are. Accuracy runs are continuous and unaffected.
