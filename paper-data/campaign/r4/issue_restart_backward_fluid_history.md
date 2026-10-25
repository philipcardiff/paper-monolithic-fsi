# Suspected solver issue: a quasi-monolithic FSI3 restart does not reproduce the continuous run (newtonIcoFluid `backward` history not written)

Status: open; reported to the coordinator (R4, 25 Oct 2026). Not worked
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
