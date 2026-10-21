# A4: Can the planned ablations be run from the current solver code?

Solver tag examined: `origin/feature-petsc-snes-quasi-monolithic` at
`257b2e5640bbef69a6876d27aa9ccfde584a1dcf` (2026-10-19), local clone
`/home/user/solids4foam`. Everything below was read with `git show`, `git log`
and `git grep`. Nothing was run, because OpenFOAM is not installed here.
File:line references are to that tag unless a commit is named.

Abbreviations:

- `Coupler` = `src/solids4FoamModels/fluidSolidInterfaces/newtonQuasiMonolithicCouplingInterface/newtonQuasiMonolithicCouplingInterface.C`
- `NIF` = `src/solids4FoamModels/fluidModels/newtonIcoFluid/newtonIcoFluid.C`
- `RAM` = `tutorials/fluidSolidInteraction/ringAddedMass`
- `RAM-README` = `RAM/verification/README.md`
- `BIT-README` = `tutorials/fluidSolidInteraction/blobInTreacle/verification/README.md`

Routes: (A) an option on the tag; (B) a rerun from a named old commit;
(C) cite numbers already recorded; (D) a small code change.

## Summary

| # | Ablation | Runtime switch on tag? | Recommended route | New runs (minimum) |
|---|---|---|---|---|
| 1 | Interface pressure: fixedGradient vs zeroGradient | Yes (BC type of `p` on the interface) | **A**, plus C for the historical numbers | 3 to 6 RAM runs |
| 2 | Traction: wall flux vs `devReff` | No | **C** (BIT-README table). D (~10 lines) only if a same-code rerun is required | 0 |
| 3a | Solid one-step force lag vs lag-free BDF2 | No | **C** (RAM-README and commit messages). B at `dcbe04505` if a rerun is wanted | 0 |
| 3b | Lag-free centred solid vs BDF2 | No. The variant was never committed | **C** (qualitative only). D on `dcbe04505` if a figure is needed | 0 (or 1 to 2) |
| 4 | Face-flux vs `div(U)` continuity | No | **C** (BIT-README). **B** at `98211d90e`, where `fvSchemes` alone may give both arms | 0 (or 2 to 6) |
| 5 | `snes_mf_operator` vs assembled Jacobian | Yes (PETSc option) | **A**. There are no recorded numbers | 4 |
| 6 | Preconditioner variants and lagging | Yes (PETSc options) | **A**. Old screening numbers are stale and only motivate the choice | about 10 short runs |
| 7 | Conservative vs interpolated AMI traction | Yes (`conservativeTractionTransfer`) | **A**. There are no recorded numbers | 2 × the RAM nonconformal study |
| 8 | Stiffened vs uniform mesh motion | Yes (`diffusivity` entry) | **C** (TurekHron2006 README). A if a figure is wanted | 0 (or 1) |

Ablations 1, 5, 6, 7 and 8 need dictionary or option changes only.
Ablations 2, 3 and 4 have no switch left on the tag. For these, the recorded
before/after numbers are the cheapest route, and they come from the commits
that made the change.

## 1. Interface pressure: fixedGradient (normal momentum) vs zeroGradient

**Code history.**

- `3e93daef6` (2026-10-15) introduced the momentum-based gradient. Before it, the
  monolithic tutorials used `zeroGradient`.
- Nothing was removed. On the tag, the coupler checks the BC type and only
  warns for `zeroGradient` (Coupler:2093-2112, "...are only first-order
  accurate in space").
- The gradient is set in `newtonIcoFluid::updatePressureGradientBoundary` (NIF:1055-1099).
- `0ed9c2a77` (#594) restricts this to a plain `fixedGradient` with a
  `fixedValue` velocity (NIF:1061-1070).

**Runtime switch.** Yes. Set the interface entry of `RAM/0/fluid/p.monolithic`
(lines 25-30, `type fixedGradient; gradient uniform 0;`) to `type zeroGradient;`.

**Caveat.** `3e93daef6` also changed the solid interface velocity passed to the
fluid: it is now extrapolated to the faces with the gradient, where it used to
be the cell value. That change stays on the tag. An A-route run therefore
isolates the pressure BC alone. The historical "before" numbers mix both
changes.

**Recorded numbers (C).**

- Source: RAM-README, "Defects found by this study". The same numbers are in
  the `3e93daef6` commit message.
- Wet/dry ratio error at 100 steps per period, meshes 1/2/4, zeroGradient state
  of `c008e8dd1`:
  - moderate: −0.194/−0.117/−0.063 %
  - strong: −0.355/−0.213/−0.115 % (first order)
- After the change (RAM-README, "Mesh"):
  - moderate: −0.016/−0.002/−0.0001 %
  - strong: −0.031/−0.004/−0.0004 %
- Amplitude loss per period at 100 steps per period, weak/moderate/strong
  (factor-2 mesh):
  - BDF2 solid with zeroGradient (`c008e8dd1` commit message): 0.17/0.71/1.26 %
  - tag (RAM-README table): 0.045/0.040/0.049 %
  - dry ring: 0.046 %
  - So the zeroGradient state also added coupling damping, close to that of
    IQN-ILS (0.16/0.65/1.15 %). This is worth stating: the pressure treatment
    affects the damping as well as the added-mass frequency.

**Recommended.** Route A on the tag, with RAM and the driver
`RAM/verification/Allverify`. The driver copies the tutorial, so edit
`p.monolithic` in a copy of the tutorial tree, or add a one-line `replace_entry`
to the driver. The driver's damping and ratio checks may "fail" for the
zeroGradient arm. That is expected, but confirm that it still writes the
results table.

**Minimal run set.**

- Mesh series: the conformal arm (`solidCells 0`) of `--study nonconformal`,
  factors 1/2/4 at 100 steps per period. Run it with `--levels moderate,strong`,
  zeroGradient arm only, because the fixedGradient arm is already recorded.
  That is 6 wet runs plus the dry runs.
- If budget is tight: factors 1 and 2 at the strong level only (2 wet runs).
  This shows the first-order slope.

## 2. Interface traction: wall flux `nuEff*snGrad(U)` vs `devReff`

**Code history.**

- Before `2894f2c0a`, `patchViscousForce` returned
  `rho*(nf & -devReff)` (or `devTau` on OpenFOAM.org): see `0698d55cd:NIF:518-541`.
- `2894f2c0a` (2026-10-15) replaced this with a quadratic wall-shear estimate.
- `dbfda65ba` (2026-10-16) replaced the quadratic with the wall flux
  `rho*nuEff*snGrad(U)` (NIF:505-526).
- Only a commented-out `devReff` line remains, in the deformed-mesh overload
  (NIF:568-573).

**Runtime switch.** None.

**Recorded numbers (C).**

Source: BIT-README:203-208, steady `u_x` (m) of the top point, x1/x2/x4.
These were recorded on macOS, OpenFOAM v2512.

| Variant | x1 | x2 | x4 | Order | Extrapolated |
|---|---:|---:|---:|---:|---:|
| `devReff` + `div(U)` continuity (state `0698d55cd`) | 0.115467 | 0.118301 | 0.119376 | 1.4 | 0.12003 |
| wall flux + `div(U)` continuity (state `dbfda65ba`) | 0.117429 | 0.119524 | 0.120053 | 2.0 | 0.12023 |
| partitioned | 0.117301 | 0.119696 | 0.120224 | 2.2 | 0.12037 |

- The first two rows differ only in the traction, so this is a clean one-factor
  ablation.
- The x1/x2/x4 `devReff` values also appear in the `2894f2c0a` message, and the
  wall-flux values in the `dbfda65ba` message.
- The intermediate quadratic is documented as rejected: it made the partitioned
  coupling first order (`dbfda65ba` message, issue #583). It is not needed for
  the paper.
- Note: the brief's "order 1.4 vs 1.9" mixes rows. 1.4 → 2.0 is the
  traction-only change. The 1.9 belongs to the tag (wall flux + face-flux
  continuity), BIT-README:208.

**Recommended.** Route C.

- If a rerun on today's code is needed, use route D: a `Switch` in
  `newtonIcoFluid` (for example `interfaceTractionDevReff`, default `no`) that
  restores the 8-line `devReff` body in `patchViscousForce(label)`. That is
  about 10 to 15 lines.
- Route B (`0698d55cd`) would also roll back every later fix, including #594
  and #597.

**Tutorial.** blobInTreacle, `./Allrun monolithic` at x1/x2/x4 to t = 3 s. Its
driver runs only the partitioned coupling (BIT-README:197).

## 3a. Solid one-step force lag vs lag-free BDF2

**Code history.**

- `c008e8dd1` (2026-10-15) "Velocity solid: integrate the displacement with the
  backward scheme".
  - Before: the centred scheme averaged `forceCurrentTime_.oldTime()` and
    `forceFutureTime_` (`dcbe04505`: `nonLinGeomTotalLagVelocitySolid.C:904-912`,
    956, 1014).
  - The old-time half was the traction from two steps back.
- It removed `extrapolateTractionBoundaries`, `DFutureTime`, `forceCurrentTime`
  and `forceFutureTime`, with their tutorial entries and initial fields.

**Runtime switch.** None.

**Recorded numbers (C).**

Source: RAM-README "Defects found by this study" and the `dcbe04505` and
`c008e8dd1` commit messages. All runs were at 100 steps per period on the
factor-2 mesh, with a zeroGradient interface pressure in both states.

| State | Amplitude loss per period, weak/moderate/strong |
|---|---|
| lag (`dcbe04505`) | 2.0/10.6/18.3 % |
| predicted (π (m_a/M) ω Δt, RAM-README) | 1.8/9.9/17.9 % |
| BDF2, lag-free (`c008e8dd1`) | 0.17/0.71/1.26 % |
| tag (BDF2 + fixedGradient) | 0.045/0.040/0.049 % |

In the lag state, the loss also "fell at first order in the time-step".

**Route B, if a rerun is wanted.** `dcbe04505` has the driver
(`./Allverify --study monolithic`) and the lagged solid. Its parent tutorial
state uses `DFutureTime.monolithic` and the `extrapolateTractionBoundaries`
entries, which `c008e8dd1` deleted. Record the hash `dcbe04505` and a full
build of that commit. Any run there also lacks every later fix (#594, #597,
`dbfda65ba`), so compare it only with `c008e8dd1`, not with the tag.

## 3b. Lag-free centred solid vs BDF2 (high-frequency mode in blobInTreacle)

**Code history.** The lag-free centred variant was an intermediate state during
the diagnosis of `c008e8dd1` and was never committed. `git log -S` finds no
commit that fixes the old-time write.

**Evidence.** The only evidence is qualitative. The `c008e8dd1` message says
"With the lag removed, the centred scheme dissipated nothing at any frequency,
and a high-frequency mode grew in blobInTreacle after it reached its steady
state". RAM-README repeats this.

**Recommended.** Route C, as a sentence.

- For a figure, use route D on top of `dcbe04505`: write the old-time traction
  correctly, so the centred average uses step n. That is a few lines in
  `nonLinGeomTotalLagVelocitySolid.C` around 904-912.
- Then run blobInTreacle x1 monolithic past its steady state, centred vs BDF2:
  2 runs.

This is new (temporary) development on an old commit. Agree it with Philip
first.

## 4. Continuity: face-flux (#597) vs `div(U)`

**Code history.**

- `5a03c7ad8` (2026-10-18) was merged as #597 in `597cc6317`. Its parent on the
  solver branch is `98211d90e`.
  - Old: `scalarField pressureResidual(- fvc::div(U));` (`98211d90e:NIF:1234`).
  - New: `-fvc::div(fvc::interpolate(U) & mesh.Sf())` (NIF:1233-1243).
- `41687c58c` only fixes the foam-extend build.

**Runtime switch.** None on the tag.

- Setting `interpolate(U)` to `linear` on the tag makes the momentum flux
  consistent. It does not reproduce the defect.
- The defect exists only when the `div(U)` and `interpolate(U)` interpolations
  differ. The monolithic tutorials have `div(U) Gauss linear` and
  `interpolate(U) skewCorrected linear` (for example
  `RAM/system/fluid/fvSchemes.monolithic:49,60`). On a mesh with no skewness the
  two arms coincide.

**Recorded numbers (C).**

- blobInTreacle: BIT-README:207-208 and :219-224.
  - wall flux + `div(U)`: 0.117429/0.119524/0.120053, order 2.0, extrapolated 0.12023
  - tag: 0.116851/0.119346/0.120020, order 1.9, extrapolated 0.12027
  - "moves the coarse-mesh values by up to 0.5 % and the extrapolated value to
    within 0.08 % of the partitioned one"
- Rigid Hron–Turek plate (CFD3-like, Re = 200), from the `5a03c7ad8` commit
  message only. The lift amplitude was 13 % below `pimpleFluid` on the 2x mesh
  before the change and 3 % below after it, and the shedding decayed on the 1x
  mesh. That case is not a tutorial on the tag, and I found no README record of
  it.

**Route B, cheapest.** Use `98211d90e`.

- With the old code, `div(U) Gauss skewCorrected linear;` in `fvSchemes` should
  make `fvc::div(U)` the divergence of the same face flux as `interpolate(U)`.
  Gauss divergence is `surfaceIntegrate(Sf & interpolate(U))`, so this
  reproduces the fixed residual.
- Both arms would then come from one build, by `fvSchemes` only. Confirm this
  equivalence with one run against the tag before relying on it.
- Alternative (D on the tag): a `Switch` around NIF:1242. About 5 lines.

**Tutorial.**

- For a pure-fluid demonstration of the damping: the CFD3-like rigid plate
  (ask Philip where this case lives; the source is the commit message).
- For FSI: blobInTreacle x1/x2.

## 5. Jacobian: `snes_mf_operator` vs the assembled approximate Jacobian

**Runtime switch.** Yes: remove `snes_mf_operator;` from `solvers/UpU/options`
(`RAM/system/fvSolution.monolithic:35`).

**Why removing the option is enough.**

- `foamPetscSnesHelper::initialiseSnes` sets `SNESSetJacobian(snes, A, A, ...)`
  with the assembled MatNest (`src/solids4FoamModels/numerics/foamPetscSnesHelper/foamPetscSnesHelper.C:690-695`).
- The coupler keeps that Amat and replaces only the Pmat with the AIJ copy
  (Coupler:3205-3219).
- Without `snes_mf_operator`, the Krylov operator is therefore the assembled,
  scaled approximate Jacobian.
- No code path depends on the option, and it was never removed.

**Recorded numbers.** None.

- The claim "Newton then converges only linearly" appears only as prose, in
  `newtonQuasiMonolithicCouplingInterface/README.md:187-189` (added in
  `13749a6e1`/`873a8d0e4`).
- No iteration counts were found in any README or commit message. This
  ablation needs new runs.

**Minimal run set (A).**

- RAM, moderate level, factor 2, 100 steps per period, mf vs assembled.
  - The problem is linear: mf converges in 2 Newton iterations per step
    (RAM-README).
  - The assembled Jacobian is approximate (for example the upwind
    `jacobian-div(phi,U)`), so its contraction rate is visible.
  - 2 runs.
- One nonlinear case, mf vs assembled, a few steps: blobInTreacle x1 or
  TurekHron2006 FSI1 conformal 1x. 2 runs.
- Report Newton iterations per step and the `snes_monitor` residual history.
- Set `snes_max_it` high enough (for example 50) that the linear case finishes.

## 6. Preconditioner variants and lagging

**Runtime switch.** Yes, all of them are PETSc options in `solvers/UpU`.

- Solid block (RAM fvSolution.monolithic:48-50):
  - `fieldsplit_solid_pc_type redundant` + `fieldsplit_solid_redundant_pc_type lu`
  - → `bjacobi` + `fieldsplit_solid_sub_pc_type lu`
  - → `hypre` + `fieldsplit_solid_pc_hypre_type boomeramg`
- Constraints on the solid block:
  - In parallel, the coupler stops with a fatal error if the solid PC itself is
    `lu`/`cholesky` (Coupler:3274-3330). `bjacobi`+LU and `hypre` pass the
    check.
  - In serial, `bjacobi`+LU is one block, which is the same as LU. The
    `bjacobi` arm is meaningful only in parallel.
- Schur factorisation: `fieldsplit_fluid_pc_fieldsplit_schur_fact_type` (RAM:56).
  `upper` is the tutorial default. `full` is used in 3dTube/beamInCrossFlow
  (3dTube fvSolution.monolithic:67). `lower` and `diag` are also available.
- Fluid velocity block: `fieldsplit_fluid_fieldsplit_0_pc_type` (RAM:63-66,
  `bjacobi` + ILU(0)) → `hypre`.
- Lagging: `snes_lag_jacobian`, `snes_lag_preconditioner`, and the
  `..._persists` options. These are already used in 3dTube fvSolution.monolithic:40-43.
  With the Jacobian lagged, `snes_mf_operator` must stay on.

**Existing numbers (C).** These are only partly usable.

- `873a8d0e4` message and the coupler README:169-185 give the serial run times
  for the *combined* change (ksp_rtol 1e-3 + lag 8 + full Schur + basic line
  search + AMG mesh motion):
  - beamInCrossFlow 149 s → 64 s
  - 3dTube (100 steps) 299 s → 103 s
  - These are not isolated per option.
- Historical screening from April 2026 (`2f99ea065`, `9da408595`, `2dd38915b`;
  the notes file `MONOLITHIC_PETSC_RESULTS.md` was deleted in `c11807494`):
  - upper vs lower Schur: 24 % fewer KSP iterations on foilInWind
  - `bjacobi`+LU solid at 8 ranks gave a wrong solid response (sigmaEq 2.12 vs
    4.994 with `redundant`+LU)
  - BoomerAMG on the whole system did not converge
  - These predate the BDF2 solid, the interface fixes and #597. Use them only
    to motivate the default, not as results.

**Minimal run set (A).**

- One representative case, a short window, reporting KSP iterations per Newton
  step and the wall time. Use 3dTube (3-D, the scaling case) or beamInCrossFlow.
- One arm per variant, against the tutorial default:
  - Schur lower/full
  - velocity AMG
  - solid BoomerAMG
  - solid `bjacobi`+LU in parallel only, at 4 to 8 ranks
  - lag 1 vs 8
- That is about 6 to 8 runs, plus 2 parallel runs.
- The solid BoomerAMG test is already planned on Philip's hardware (context
  file).

## 7. Conservative vs interpolated traction transfer on AMI interfaces

**Code history.** `aae583301` (2026-10-17) added the option. It is still present.

**Runtime switch.**

- `conservativeTractionTransfer` in `fsiProperties` `NewtonQuasiMonolithicCoeffs`,
  read with `lookupOrDefault<Switch>(..., false)` (Coupler:2020-2026, used at
  2114-2139 and 2891).
- A nonlinear-geometry solid also needs `useUndeformedArea yes` on its interface
  `solidTraction` patch. Otherwise the run stops with a fatal error
  (Coupler:2117-2137).
- RAM uses `linearGeometryVelocity` (`RAM/constant/solid/solidProperties.monolithic:19`),
  so it needs no extra entry.
- `interfaceFluxDiagnostics yes` (Coupler:2028-2033) logs
  `Interface force balance: ... rel_imbalance=`.

**Recorded numbers.** None found. RAM-README has no nonconformal results table,
although `3a956571f` added `--study nonconformal`.

**Minimal run set (A).**

- `RAM/verification/Allverify --study nonconformal --levels moderate` (or
  strong), twice: interpolated and conservative.
- The driver sets `interfaceTransferMethod AMI` itself. Add the two switches to
  `constant/fsiProperties.monolithic` in the copied tutorial.
- Each study is factors 1/2/4 × solid cells {conformal, 32·f, 72·f} at 100 steps
  per period. That is 9 wet runs per arm; the dry runs are shared with
  `--reuse`.
- Report:
  - the wet/dry ratio error and the amplitude loss
  - `rel_imbalance` (expected to be round-off for conservative, discretisation
    error for interpolated)

## 8. Mesh motion: stiffened vs uniform pseudo-solid

**Code history.**

- `c4c4383ac` added the stiffness scale factor to the `solids4foamSolidModel`
  mesh-motion solver.
- `415ee9a6d` set it in TurekHron2006 monolithic.

**Runtime switch.** Yes. The `diffusivity` entry is optional: without it no
scale factor is made
(`src/solids4FoamModels/fluidModels/fluidModel/meshMotionSolidModel/meshMotionSolidModelFvMotionSolver.C:62-65`).

- Remove `diffusivity quadratic inverseDistance 2(plate cylinder);` from
  `TurekHron2006/constant/fluid/dynamicMeshDict.monolithic:27`.
- For a "linear" uniform pseudo-solid, also switch `diffusionHyperElastic` to
  `diffusionElastic` in `constant/fluid/mechanicalProperties.monolithic:25`.

**Recorded (C).**

- TurekHron2006 verification README:557-562: "With a uniform pseudo-solid,
  linear or neo-Hookean, the fluid mesh inverts at `t = 2.76 s` in the FSI3
  start-up overshoot to about 40 mm, which IQN-ILS shows on the same meshes
  too". The `415ee9a6d` message says the same.
- The mesh level is not stated.

**Recommended.** Route C.

- The failure is shared by IQN-ILS, so it is a property of the mesh motion, not
  of the coupling. It belongs in the FSI3 set-up description or in the
  limitations, not in an ablation figure.
- If a figure is wanted: `./Allrun fsi3 monolithic` (or
  `hron_turek_verification.py --coupling monolithic --end-time 3`) at one
  level, without `diffusivity`. 1 run.

## Other removed options with recorded numbers (C only, in case they are useful)

- `a87692e31` "remove unused and inferior options" (parent `a435b7ee6`). No
  tutorial set these options. Values are from RAM, strong added mass, 50 steps
  per period, from the commit message:
  - `liuInterfaceCondition`: fatal with fixedGradient. With zeroGradient, the
    ratio error is −0.41 % vs −0.16 % and damping is added.
  - `extrapolateSolidInterfaceDisplacement no`: ratio error −0.058 % vs −0.038 %.
  - `zeroPressureStabilisationFluxOnFsiInterface`: changes the solution by
    5e-7 relative, with 4 % more linear iterations.
  - Default results are bitwise unchanged.
- `a435b7ee6` "remove quasiMonolithicInterfaceFluxMode" (parent `aae583301`,
  #588):
  - The three modes gave the same solution.
  - Applying the selected flux in the continuity residual diverged for
    added-mass ratios 1 and 10 on RAM, and added damping at 0.1.
  - This supports the choice of the interface velocity flux in the continuity
    equation, if the paper discusses it.

## Caveats for any old-commit (B) rerun

The commits that change results on the solver branch, in order:

1. `c008e8dd1` (BDF2 solid)
2. `3e93daef6` (fixedGradient pressure + face-extrapolated solid velocity)
3. `2894f2c0a` / `dbfda65ba` (traction)
4. `aae583301` / `a435b7ee6` / `a87692e31` (bitwise unchanged for the defaults)
5. `11b7b471a` (fluid normals in the Asf block, which affects the preconditioner only)
6. `0ed9c2a77` (#594)
7. `5a03c7ad8` (#597)

A B-route arm differs from the tag in every change after its commit. Compare it
only with its immediate successor commit, or cite the recorded pairs as above.

## Open questions for Philip

1. Ablation 4: where is the rigid Hron–Turek CFD3-like case behind the
   13 % → 3 % lift numbers in `5a03c7ad8`? It is not a tutorial on the tag.
   Should the paper show this pure-fluid case, or blobInTreacle?
2. Ablation 3b: is a sentence enough for the centred-scheme instability, or do
   you want a D-route figure on `dcbe04505`? That is temporary new code on an
   old commit.
3. Ablation 2: is citing the recorded `devReff` row (state `0698d55cd`)
   acceptable, or should there be a same-code switch (route D, about 10 lines)?
4. Ablation 8: at which mesh level did the inversion at 2.76 s occur? The README
   does not say.
