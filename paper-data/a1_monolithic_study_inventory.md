# A1: inventory of recorded quasi-monolithic (NewtonQuasiMonolithic) results in solids4foam

Evidence note for the solver paper (M). It lists every quasi-monolithic
result recorded in solids4foam, where it is recorded, which code produced it,
and whether it must be rerun from the tagged release. No `.tex` file is
changed by this note.

All sources were read from the local clone `/home/user/solids4foam` with
`git show <ref>:<path>` / `git log`; nothing was fetched or run. Unless stated
otherwise the ref is the solver branch
`origin/feature-petsc-snes-quasi-monolithic` at `257b2e564` (2026-10-19 21:27
+0100, merge of #599). Paths are relative to the solids4foam root.
`<case>` stands for `tutorials/fluidSolidInteraction/<case>`.

## 0. Code milestones used to classify the results

Commit dates are author/commit dates from `git log`; ancestry was checked with
`git merge-base --is-ancestor`.

| Commit | Date | Change | Effect on monolithic results |
|---|---|---|---|
| `c008e8dd1` | 2026-10-15 20:16 | velocity solid: BDF2 displacement, stress/traction at new time (removes one-step force lag) | changes all transient results |
| `3e93daef6` | 2026-10-15 22:14 | interface pressure `fixedGradient` from normal momentum equation | changes all results |
| `dbfda65ba` | 2026-10-16 02:19 | interface traction = momentum equation's wall flux (`rho*nuEff*snGrad(U)`), not `n & devReff` | changes all results with viscous traction |
| `2b22b9893` (#589) | 2026-10-18 13:26 | remove `quasiMonolithicInterfaceFluxMode` | not assessed (option removal) |
| `0ed9c2a77` / merge `eebf12bf6` (#594) | 2026-10-18 17:44 / 17:45 UTC | wall pressure gradient set only for a plain `fixedGradient` | expected **result-neutral** for every monolithic variant (see below) |
| `5a03c7ad8` / merge `597cc6317` (#597) | 2026-10-18 23:20 / 2026-10-19 11:02 | continuity residual from the convecting face flux `interpolate(U) & Sf` instead of `fvc::div(U)` | changes all results (see below) |
| `41687c58c` | 2026-10-19 15:03 | foam-extend build fix of #597 | none on OpenFOAM.com |
| `a15366784`, `873a8d0e4`, merge `257b2e564` (#599) | 2026-10-19 | Rhie-Chow stencil inserted as scalar entries; faster PETSc options for `beamInCrossFlow` and `3dTube` | cost only; commit messages state "the same results" (to within solver tolerances for `873a8d0e4`) |

`0ed9c2a77` is an ancestor of `5a03c7ad8`, so every #597 result also has #594.

**Why #594 is expected to be result-neutral for the monolithic variants.**
Its commit message states that the wall-momentum estimate is now applied only
to a pressure of type exactly `fixedGradient`, "which all the monolithic
tutorial variants use"; derived types keep their given gradient. The pressure
files of all twelve monolithic variants (`<case>/0/fluid/p.monolithic`,
`3dTube/0/fluid.monolithic/p`, `foilInWind/0.orig/fluid/p.monolithic`)
contain only `fixedGradient`, `fixedValue`, `uniformFixedValue`,
`codedFixedValue`, `zeroGradient`, `symmetry`, `wedge` and `empty`; no
`fixedGradient`-derived type. #594 also changed the coupling's pressure-type
test (`newtonQuasiMonolithicCouplingInterface.C`), which for these files
selects the same patches. This is an inference from the source, not a rerun.

**Why #597 matters for every monolithic variant.** All twelve
`system/fluid/fvSchemes.monolithic` files set `div(U) Gauss linear` and
`interpolate(U) skewCorrected linear`, the case named in the #597 commit
message as making the convecting flux non-solenoidal. The difference vanishes
only where the skew correction is zero (orthogonal, unskewed faces), so its
size is case-dependent: from the reruns, `blobInTreacle` moved by up to 0.5%
(coarse mesh; `835f81a4e`), `cavityFlexibleBottom` by up to 0.15% in `uy` and
0.20% in `Fy` (`f356c3242`), and the rigid Hron-Turek plate (CFD3-like, a
fluid-only comparison against `pimpleFluid`) by about 10 points in lift
amplitude (13% below `pimpleFluid` before, 3% after, on the 2x mesh;
`5a03c7ad8` message and `CHANGELOG.md` line 608-610). The CFD3-like comparison
itself is not recorded in any README or case.

**Classification rule used below.**
CURRENT = produced by code containing `5a03c7ad8` (#597) and recorded with the
commit or at a commit that contains it. STALE = produced before #597 (and in
several cases also before `c008e8dd1`/`3e93daef6`/`dbfda65ba`, which is worse
and noted). UNKNOWN = commit cannot be established. "Recorded" commit = the
commit that last changed the numbers (`git log -L` on the README lines); where
no build commit is stated, the README commit is an upper bound for the code
used, since the numbers were committed after they were produced.

No tag contains `597cc6317` (`git tag --contains` is empty; newest tag
`v2.4`), so no "tagged release" with the fixes exists yet.

## 1. Per-case inventory

### 1.1 ringAddedMass (M Sec. 4)

- **Study: quasi-monolithic Newton against IQN-ILS, time-step refinement.**
  Source: `ringAddedMass/verification/README.md`, section "Quasi-monolithic
  Newton against IQN-ILS" (lines 319-371). Refinement-factor-2 mesh, three
  added-mass levels (weak, moderate, strong), 25/50/100 steps per period,
  standard solid, plus the dry ring. QoIs: frequency ω, wet/dry ratio error
  against the exact value, amplitude loss per period, mean Newton (monolithic)
  or coupling (IQN-ILS) iterations per step, wall time per run.
  Key numbers: monolithic Newton iterations 2.00 at every level and step;
  ratio error within 0.007% at every level; amplitude loss 2.57%, 0.36%,
  0.045% per period at 25/50/100 steps (= dry ring 2.57%, 0.36%, 0.046%);
  frequency order 1.88-1.89; IQN-ILS loss up to 1.15% per period (strong,
  100 steps). Times 23-91 s (monolithic), 18-120 s (IQN-ILS).
- **Study: mesh at 100 steps per period** (same section, "Mesh" bullet):
  monolithic ratio error -0.016%, -0.002%, -0.0001% (moderate) and -0.031%,
  -0.004%, -0.0004% (strong) on factors 1, 2, 4; IQN-ILS values "recorded
  separately; not part of the study".
- **Ablation history ("Defects found by this study", lines 373-404):**
  one-step force lag: loss 2.0%, 10.6%, 18.3% per period at 100 steps;
  `zeroGradient` interface pressure: ratio error -0.194%, -0.117%, -0.063%
  (moderate) and -0.355%, -0.213%, -0.115% (strong), first order in the mesh.
  These are the pre-fix numbers that support contribution 2 of M.
- Commits that last changed the section: `dcbe04505` (study added),
  `c008e8dd1`, `3e93daef6`, `0698d55cd` (all 2026-10-15). Hence the numbers
  are post-BDF2 and post-interface-pressure, but **pre-`dbfda65ba`
  (traction), pre-#594 and pre-#597**.
- Platform: OpenFOAM v2512, macOS (Apple M-series), 10 serial runs at a time,
  21 runs in about 2 minutes; README says the times are "only indicative".
  Mesh-study platform not stated separately.
- Cost recorded: wall time yes (indicative, concurrent runs); Newton yes
  (mean per step); Krylov no.
- Driver: `cd tutorials/fluidSolidInteraction/ringAddedMass/verification &&
  ./Allverify --study monolithic` (options `--levels`, `--cores`, `--reuse`,
  `--quick`; script `scripts/ring_added_mass_verification.py`). In the
  script (`build_specs`, lines 537-546) `--study monolithic` runs only the
  time steps on `timeStudyFactor`; the monolithic runs under mesh refinement
  are generated by `--study nonconformal` (lines 547-557: every mesh factor,
  with `solid_cells` 0, i.e. conformal, plus coarser/finer solid
  interfaces). The README's mesh numbers were therefore run either by hand
  or by an earlier form of the driver (not established).
- Also: `./Allverify --study nonconformal` (AMI coarser/finer solid
  interface faces) exists in the driver and is cited in the coupling README,
  but **no nonconformal results are recorded** in the verification README.
- Older record (superseded): commit message `63154296d` (2026-10-15 00:57):
  2.176 vs 2.179 rad/s, damping 6.5% per half period (pre-BDF2).
- **Status: STALE** (pre-#597; also pre-traction fix).

### 1.2 womersleyTube (M Sec. 4)

- **Study: mesh (m1, m2, m4 at 200 steps/period) and time step (m2 at 50,
  100, 200, 400 steps/period), plus comparison with IQN-ILS (m2, n100).**
  Sources: `womersleyTube/verification/README.md` section "Quasi-monolithic
  coupling" (lines 315-351) and the committed driver output
  `womersleyTube/verification/temporal/production/verification_summary_monolithic.md`
  and `womersleyTube_results_monolithic.csv`.
  QoIs: velocity profile error at L/2, flow-rate amplitude/phase, wall radial
  displacement amplitude/phase, wave speed, attenuation, periodicity, Newton
  iterations per step, run time. Key numbers: mesh orders 2.23 (profile),
  2.06 (flow rate), 1.98 (wall amplitude), 2.00 (wave speed); time orders
  1.94-2.07 over the finest three steps; agreement with IQN-ILS to 7.2e-4 or
  better; wall amplitude offset to Robin-Neumann 3.3-3.5e-4 (source not
  identified); 2 Newton iterations and 149 s (m2, n100) against 14.6
  coupling iterations and 524 s for IQN-ILS. Run times in the CSV: 76.69 s
  (m2 n50) to 1056 s (m4 n200).
- Commit: `54a5c6916` (2026-10-16 12:58, study added); `ff9aeb55e`
  (2026-10-18) only reformatted the summary (markdown lint). Post-traction
  fix, **pre-#594 and pre-#597**.
- Platform: not stated for the monolithic runs (the README's platform line
  252, "OpenFOAM-v2512 on Linux (x86_64)", belongs to the partitioned
  records); "The seven runs take 1.3 to 18 minutes each in serial".
- Cost recorded: wall time yes (per run, serial); Newton yes; Krylov no.
- Driver: `cd tutorials/fluidSolidInteraction/womersleyTube/verification &&
  ./Allverify --monolithic` (with `--study all|main|coupling`, `--cores`,
  `--reuse`, `--quick`); output suffix `_monolithic`.
- **Status: STALE** (pre-#597). Straight-tube wedge mesh, so the #597 skew
  correction may be small, but this is not measured.

### 1.3 cavityFlexibleBottom (M Sec. 5)

- **Study A (pre-#597): mesh levels 1-4, Δt = 0.5 s, steady state.**
  Source: `cavityFlexibleBottom/verification/README.md` section
  "Quasi-monolithic coupling" (lines 122-149) on the solver branch, commit
  `291aaa968` (2026-10-16 06:19). QoIs: steady `Uy` of the monitor point and
  interface force `Fy`. Level 1-4 `Uy` mono -0.201557, -0.228817,
  -0.235676, -0.237336 m; `Fy` -5.1225, -5.2381, -5.2576, -5.2606 N;
  observed orders 1.99, 2.05; extrapolated -0.23787 m; agreement with
  partitioned Aitken to 0.02% on level 3. OpenFOAM v2512, macOS, serial.
  The CSV on the verification branch dates these runs to
  "feature-ring-monolithic-verification ~0698d55cd, end time 200 s".
  **STALE.**
- **Study B (post-#597): rerun of the four levels.** Source: branch
  `origin/verification/cavityflexiblebottom-partitioned-fine`, commit
  `f356c3242` (2026-10-20 00:44), README section "Rerun with the
  newtonIcoFluid continuity fix (solids4foam PR #597, recorded 20 Oct 2026)"
  and `verification/results/four_level_partitioned_monolithic.{csv,json}`
  (rows `monolithic_597`; old rows relabelled `monolithic_pre597`).
  Build stated: solver branch at `257b2e564` (contains `597cc6317`),
  OpenFOAM v2512 (OpenCFD) on xenosim (Ubuntu 22.04), gcc 11.4.0, `-O3`,
  PETSc 3.24.1 with MUMPS and HYPRE. Levels 1-3 serial; level 4 on 4 MPI
  ranks (`Allrun monolithic parallel`, scotch) with the fluid mesh-motion
  preconditioner changed from `bjacobi`+LU to `redundant`+LU. Δt = 0.5 s,
  inlet ramp 20 s, end time 300 s.
  Key numbers: `uy` (underside) -0.201546, -0.228468, -0.235448, -0.237187 m;
  `Fy` -5.12258, -5.22750, -5.25072, -5.25611 N; orders 1.95/2.01 (`uy`) and
  2.18/2.11 (`Fy`); Richardson (p = 2, levels 3-4) -0.23777 m against
  partitioned -0.23787 m (0.04%); monolithic-minus-partitioned `uy`
  3.3e-4, 1.8e-4, 1.2e-4 m on levels 2-4 (ratio 1.5-1.8 per halving, origin
  not established). Top and mid-thickness values also recorded.
  Cost: the `clock_s`, `iters_mean_last10` columns are **empty** for every
  monolithic row; no Newton or Krylov counts; no wall time. Level 4 serial
  "about 55 to 80 s per step" is mentioned only as the reason for running in
  parallel. **CURRENT** (post-#597, commit stated), but **not merged** into
  the solver branch.
- **Study C (very old campaign in this paper repo):**
  `simulationData/cavityFlexibleBottom/campaignSummary.tsv` (paper repo
  commit `8cb584e`, 2026-05-23): 20 `monolithic default` rows, meshes 1-3,
  Δt = 0.5-40 s, with `WallTime`, `MaxMemoryMb`, `SteadyTime`, `Uy`, `Fy`
  (e.g. m1 Δt 0.5: `Uy` -0.244682, `Fy` -5.12266, 133.51 s). Its `Uy` differs
  from Studies A/B by about 20% (different monitor point or definition, not
  checked) and the code predates every fix above, as do the PDFs in the same
  directory. **STALE**; do not reuse.
- Tutorial README (`cavityFlexibleBottom/README.md` line 70-72): final `Uy`
  -0.2017 m against -0.2025 m partitioned, last changed `58d1e314b`
  (2026-10-15 00:51, pre-BDF2). The regression test monolithic arm uses the
  partitioned references with a stated tolerance (7e-4 in displacement, 0.03
  in mean force; `regressionTest.sh` last changed `645c19aa3`, 2026-10-15).
  **STALE.**
- Driver: `cd tutorials/fluidSolidInteraction/cavityFlexibleBottom/verification
  && ./Allverify --variants monolithic --levels 1,2,3,4 --end-time 300`
  (options `--delta-t`, `--reuse`, `--keep-going`). The driver is serial; the
  Study B level-4 parallel run with `redundant`+LU mesh motion was done
  outside it.
- **Status: Study B CURRENT; A, C and tutorial README STALE.**

### 1.4 collapsibleChannel (M Sec. 6)

- **Study: combined mesh refinement (fluid levels 1, 2, 4 with solid 80x8,
  160x8, 320x8), time step on level 2 (Δt 0.0125, 0.00625, 0.003125 s), and
  density ratio ρs/ρf = 1 and 0 (massless wall).** Source:
  `collapsibleChannel/verification/README.md` section "Quasi-monolithic
  coupling" (lines 293-335), commit `e069b5119` (2026-10-16 12:02). QoI:
  first trough of the wall midpoint, error against oomph-lib at the same Δt,
  run time. Key numbers: trough -0.19619, -0.20691, -0.21063 m (errors
  -9.1%, -4.1%, -2.4%, order 1.5) at Δt = 0.00625; time-step order 1.7 on
  level 2; massless and ρs/ρf = 1 troughs within 0.2%; failure at
  Δt = 0.025 s on level 2 (fluid cell inversion at t = 0.25 s). Run times
  553-7901 s. Robustness claim: completes cases where IQN-ILS fails at every
  wall density and Robin-Neumann fails for ρs/ρf <= 0.1.
- Platform: OpenFOAM v2512, macOS, serial; run to t = 1.5 s.
- Cost recorded: wall time yes; Newton no; Krylov no.
- Driver: **none for monolithic**; "run separately ... with the driver's case
  set-up" (`./Allverify` has `--study static|solid|mesh|time`, `--list`, no
  coupling option). Tutorial: `./Allrun monolithic`.
- Tutorial README line 227-236 (`1688350ae`, 2026-10-16): first trough within
  1.4% of `./Allrun linear`.
- **Status: STALE** (pre-#594/#597).

### 1.5 mokLidDrivenCavity (M Sec. 5 or 6)

- **Study: mesh 16x16 to 128x128 with Δt halved per level (0.2 to 0.0125 s).**
  Source: `mokLidDrivenCavity/verification/README.md` section "Mesh study with
  the quasi-monolithic coupling" (lines 152-178), commits `c0c91c76b` and
  `22c123755` (2026-10-16 04:23 and 08:53). QoIs: peak, trough, mean
  displacement, run time. Key numbers: peak 0.2950 to 0.2860 m; trough
  mesh-independent to 0.1% from 32x32 at 0.2025 m; peak agrees with
  partitioned to 0.2% on the finest mesh; 128x128 completes (partitioned
  diverges). Times 16 s to 9109 s.
- Platform: OpenFOAM v2512, macOS, serial.
- Cost recorded: wall time yes; Newton no; Krylov no.
- Driver: `cd tutorials/fluidSolidInteraction/mokLidDrivenCavity/verification
  && ./Allverify --monolithic --study mesh` (writes `work/monolithic`,
  `postProcessing/monolithic`); the 128x128 level was "run separately, with
  the same members' settings".
- **Status: STALE** (pre-#594/#597).

### 1.6 blobInTreacle = Liu et al. (2014) elastic half-cylinder (M Sec. 7)

- **Study: mesh x1, x2, x4 to t = 3 s (Δt 0.01, 0.01, 0.005 s per the mesh
  study table), steady top-point `u_x`.** Source:
  `blobInTreacle/verification/README.md` section "Quasi-monolithic coupling"
  (lines 195-227). Rows: partitioned 0.117301, 0.119696, 0.120224 (order 2.2,
  extrapolated 0.12037); monolithic `devReff` traction (ablation) order 1.4,
  extrapolated 0.12003; monolithic `div(U)` (pre-#597) order 2.0, 0.12023;
  monolithic (face-flux continuity) 0.116851, 0.119346, 0.120020, order 1.9,
  extrapolated 0.12027 (within 0.08% of partitioned).
  The current row was recorded in `835f81a4e` (2026-10-19 00:53), on the #597
  branch; `5a03c7ad8` is its ancestor, so the code contains #597 (and #594).
  Platform: first rows "OpenFOAM v2512, macOS, serial"; the face-flux row
  "recorded on Linux" (no build commit stated).
- Tutorial README (`blobInTreacle/README.md` lines 80-87, `835f81a4e`):
  `u_x` 0.0566 m at t = 1 s and 0.1169 m at the end (partitioned 0.0566,
  0.1173); force within 0.8%; "about half the time of the partitioned one";
  serial and 4-rank results agree to seven significant figures.
  Regression references `MONO_REF_DISP_T1=0.0566067`,
  `MONO_REF_DISP_END=0.116853`, `MONO_REF_FORCE_END=15.7054` (v2512, serial,
  Linux; `regressionTest.sh`, `835f81a4e`).
- **The temporal-accuracy study of Liu et al. (Δt = 0.25 to 0.03125 s to
  t = 1 s, self-convergence of `u_x` and interface position) exists only for
  the partitioned coupling**; the driver "runs the partitioned coupling only".
- Cost recorded: no (only "about half the time" in prose); Newton no;
  Krylov no.
- Driver: **none for monolithic** (`./Allverify --study time|mesh`,
  `--levels`, `--cores`, `--reuse`, `--quick`; no coupling option).
  Tutorial: `./Allrun monolithic [parallel]`.
- **Status: CURRENT** for the mesh study (face-flux row) and tutorial values
  (code contains #597; recorded before the #597 merge and before #599, which
  is cost-only). The `devReff` and `div(U)` rows are deliberate ablation/
  history rows.

### 1.7 TurekHron2006 (M Sec. 7)

- **Study: FSI1 (steady) and FSI3 (periodic) mesh studies on the conformal
  monolithic meshes.** Source: `TurekHron2006/verification/README.md` section
  "Quasi-monolithic coupling" (lines 551-592), commit `a39da0f4e`
  (2026-10-17 21:36). The conformal meshes have a quarter of the tutorial's
  solid cells at each factor (5x30 on the plate at 1x). Δt follows the
  driver's level table (FSI3: 0.001, 0.0005, 0.00025 s at 1x/2x/4x; FSI1:
  0.025 s, 0.0125 s at 4x).
  FSI1 (serial; Featflow level 7+0): `u_x(A)` +16.4%, +0.37%, +0.09%;
  `u_y(A)` -38.4%, -15.0%, -4.75%; drag -0.51%, +0.05%, +0.11%; lift +15.3%,
  +6.0%, +1.7%; clock 146, 668, 6146 s.
  FSI3 (t = 7 s, last second; Featflow level 4): conformal 2x and 4x errors,
  e.g. lift amplitude 33.5% and 8.3% (IQN-ILS tutorial 2x: 13.3%), drag
  amplitude 10.7% and 3.4%, `u_y` amplitude 9.6% and 3.7%; conformal 4x on
  12 ranks in 3.6 h.
  Newton: "every step converged in 2 or 3 Newton iterations (FSI1: 1.3-1.4)".
- Platform: OpenFOAM v2512, Apple M1 Ultra "shared with other jobs".
- Cost recorded: wall time yes (FSI1 per level; FSI3 4x only), shared
  machine; Newton as a range; Krylov no.
- Driver: `cd tutorials/fluidSolidInteraction/TurekHron2006/verification &&
  ./Allverify --coupling monolithic --levels 1,2,4` (FSI3 default;
  `--benchmark fsi1` for FSI1; `--cores N|auto`, `--end-time`, `--window`).
  `--coupling` applies to the mesh study only (`--study mesh`).
- **Status: STALE** (pre-#594/#597). #597 is known to change the shedding
  lift by about 10 points on the rigid-plate case, so the FSI3 numbers,
  especially lift, are expected to move substantially.

### 1.8 beamInCrossFlow (M Sec. 7 or 8, cost)

- Tutorial README (`beamInCrossFlow/README.md` lines 185-202, `58d1e314b`,
  2026-10-15 00:51, pre-BDF2): Δt = 0.05 s to t = 4 s, max tip `Dx`
  2.69e-2 m (IQN-ILS 2.63e-2), final 1.066e-2 m (0.991e-2). **STALE**, and
  inconsistent with the regression references below.
- Regression references (`regressionTest.sh` lines 365-372, `dbfda65ba`,
  2026-10-16): `MONO_REF_MAX_DISP=0.0278474`, `MONO_REF_FINAL_DISP=0.0267971`,
  `MONO_REF_FINAL_FORCE=5.11391`; v2512, serial, macOS; "tip displacement
  6-8% and force 6.5% higher than the partitioned references"; "neither
  coupling has been refined in space". **STALE** (pre-#597).
- Cost (commit messages only): serial 278 s -> 149 s (`a15366784`) -> 64 s
  (`873a8d0e4`), partitioned IQN-ILS 94 s; both commits contain #597.
  Platform not stated in the messages.
- Driver: verification `Allverify` (`scripts/beam_in_cross_flow_verification.py`)
  has **no monolithic option**. Tutorial: `./Allrun monolithic [parallel]`.
- **Status: STALE** (displacements/forces); timing data post-#597 but only in
  commit messages.

### 1.9 3dTube (M Sec. 8)

- No monolithic result in `3dTube/README.md` or
  `3dTube/verification/README.md` (the word "monolithic" there refers only to
  the finite element references of Lozovskiy et al. 2019 and Eken 2016).
- Commit message `3fa7d5918` (2026-10-15 02:18, pre-BDF2): displacement
  history within 1.5% RMS of Robin-Neumann, maximum within 1.2%. **STALE.**
- Cost (commit messages only): serial 100 steps 503 s -> 299 s
  (`a15366784`) -> 103 s (`873a8d0e4`), partitioned Robin 153 s; post-#597.
  Platform not stated.
- No scaling study recorded anywhere.
- Driver: verification `Allverify` has **no monolithic option**. Tutorial:
  `./Allrun monolithic` (README/Allrun list no `parallel` for monolithic;
  `3dTube/Allrun` line 14 shows `./Allrun monolithic` only).
- **Status: no recorded study** (only STALE prose and cost-only commit
  messages).

### 1.10 foilInWind = 3D block with flexible flag (M Sec. 9)

- Case: rigid block 1 cm (x, y) x 3 cm (z), foil 4 cm long, 3 cm wide,
  0.6 mm thick, air 1 m/s, Re about 650 on the block side, St Venant-Kirchhoff
  foil (E = 2 MPa, ρs = 2000 kg/m³); 176 248 fluid cells, 32x6x24 solid
  cells (`foilInWind/README.md`). It is a 3D block-with-flexible-flap
  configuration, but the README cites no benchmark or reference solution; the
  flapping "has not been verified".
- Solver branch README (`a1aa222c8`, 2026-10-15 03:26, pre-BDF2): same
  Δt = 0.01 s for both couplings; trailing-edge displacement within 1%,
  drag within about 10%; first 0.2 s: 13 min IQN-ILS on 2 processes, 29 min
  monolithic on 2 processes (3-14 Newton iterations per step); Apple M1 Ultra.
  **STALE.**
- Branch `origin/fix/foilInWind-monolithic-timestep`, commit `b157ecaf3`
  (2026-10-19 19:03; based on `47209122d`, contains `597cc6317`, does not
  contain #599 `257b2e564`): new `system/controlDict.monolithic` with
  Δt = 0.0025 s. Finding: at Δt = 0.01 s the Newton method stagnates in the
  step to t = 0.05 s (serial and 2 processes, Clang/macOS and GCC/Linux;
  residual 646 -> 530, line search stalls at about 150); right
  preconditioning, unlimited convection and other matrix-free differencing
  parameters stall the same way. At 0.0025 s every step converges in 2-4
  Newton iterations. Results: peak streamwise trailing-edge displacement
  5.1e-8 m (partitioned) vs 7.7e-8 m (monolithic); agreement within about 25%
  between 0.05 and 0.1 s; first 0.2 s: about 55 min on 2 processes (80 steps)
  or 94 min serial, against 13 min for IQN-ILS on 2 processes; Apple M1 Ultra.
- Cost recorded: wall time yes (2 ranks and serial); Newton yes (range);
  Krylov no.
- Driver: none (tutorial only): `./Allrun monolithic [parallel]`, the parallel
  run uses `decomposeParMonolithic` with `system/decomposeParDict.monolithic`.
- **Status: CURRENT** (post-#597, on an unmerged branch; build commit not
  stated, inferred from the branch base). Pre-#599, so the cost would change.

### 1.11 membraneRoof

- Tutorial README (`membraneRoof/README.md` lines 134-152, `563521456`,
  2026-10-15 02:20, pre-BDF2): mean roof-centre displacement between 1 and
  4 s -0.37 m (partitioned -0.25 m default mesh, -0.35 m finer mesh,
  reference -0.36 m); serial monolithic about five times as long per step.
  Qualitative comparison only ("not a verification").
- No driver. Tutorial: `./Allrun monolithic [parallel]`.
- **Status: STALE.**

### 1.12 perpendicularFlap

- No recorded monolithic numbers in the README; only commit message
  `63154296d` (2026-10-15, pre-BDF2): maximum tip displacement within 3% of
  IQN-ILS, passes the regression reference (the regression test has no
  monolithic arm on the solver branch).
- No driver. Tutorial: `./Allrun monolithic [parallel]`.
- **Status: no recorded study (STALE prose in a commit message).**

### 1.13 channelLeaflet, hessenthalerFsi

No `*.monolithic` files on any origin branch checked, and no monolithic
results; "monolithic" appears only in reference titles. Nothing to rerun.

### 1.14 Benchmark cases asked about

- **Liu, Jaiman and Gurugubelli (2014) elastic half-cylinder in a channel**
  (the temporal-accuracy case): **exists as `blobInTreacle`**
  (`c38699361`, 2026-09-27; merged in #498). Partitioned time and mesh studies
  are in its `verification/`; the monolithic variant has only the mesh study
  and tutorial values (Section 1.6). A monolithic temporal study must be added.
- **Jaiman and Joshi (2022)**: cited by the `CHANGELOG.md` as the basis of the
  quasi-monolithic method (line 11-15). The branch history has
  `03e8426e4` "Initial progress on the Jaiman and Joshi quasi-monolithic
  algorithm" (2025-10-19); no tutorial is named after it and no case
  reproduces a Jaiman-Joshi benchmark beyond `blobInTreacle`.
- **2D block with flexible tail (cantilever behind a square block)**: **no
  case on any origin branch** (searched tutorial paths for
  `tail|squareCyl|wallRamm|blockFlex|flag|flap` on every `origin/` branch,
  and commit messages for "flexible tail", "Wall and Ramm", "square
  cylinder", "Hübner"). Only `perpendicularFlap(.jfnk)` and `TurekHron2006`
  are flap-type 2D cases.
- **3D block with flapping plate**: `foilInWind` is the only 3D
  block-plus-flag case (Section 1.10). Whether its parameters match a
  published 3D benchmark is not stated in the case and was not checked.

## 2. Observations relevant to the campaign

1. **No driver records Krylov iteration counts.** `hron_turek_verification.py`,
   `ring_added_mass_verification.py` and `womersley_tube_verification.py`
   parse Newton iterations from `log.solids4Foam`
   (`Nonlinear solve ... iterations N`); no script under
   `tutorials/fluidSolidInteraction/*/verification/scripts/` parses KSP/linear
   iterations. M's Newton/Krylov tables need a log parser (or
   `-snes_converged_reason -ksp_converged_reason` / `-log_view` capture).
2. Wall times, where recorded, are mostly from macOS serial runs with several
   runs in parallel or a shared machine (ring: "only indicative"; TurekHron:
   "shared with other jobs"). None is suitable as published cost data.
3. All recorded monolithic numbers predate #599. #599 states unchanged
   results, but its PETSc option changes (`ksp_rtol 1e-3`, lagged
   Jacobian/preconditioner, BoomerAMG mesh motion) apply only to
   `beamInCrossFlow` and `3dTube`; the other tutorials keep the common set-up
   (`redundant`+LU solid, LGMRES, Schur fieldsplit).
4. Ablations needed by M contribution 2: the `zeroGradient` interface pressure
   is still selectable (the coupling warns); the `devReff` traction and the
   force-lagged velocity solid have been removed from the code
   (`newtonIcoFluid.C` keeps only a commented `devReff` line; #589 removed the
   interface flux modes), so those two ablations can only be rerun from older
   commits or after re-adding a switch.
5. Two results that should be in the paper live on unmerged branches:
   `f356c3242` (cavity rerun) and `b157ecaf3` (foilInWind Δt/4).

## 3. Summary table

| Case | Study | Status | Driver invocation | Cost recorded? |
|---|---|---|---|---|
| ringAddedMass | Δt 25/50/100 per period, 3 added-mass levels, vs IQN-ILS | STALE (10-15; pre-traction, pre-#597) | `ringAddedMass/verification/Allverify --study monolithic` | time (indicative), Newton; no Krylov |
| ringAddedMass | mesh factors 1/2/4 at 100 steps | STALE | conformal arm of `Allverify --study nonconformal` | no |
| ringAddedMass | force-lag and `zeroGradient` ablations | STALE (by design; pre-fix code) | none (code switch removed for force lag) | no |
| ringAddedMass | non-conformal (AMI) | not recorded | `Allverify --study nonconformal` | – |
| womersleyTube | mesh m1/m2/m4, Δt n50-n400, vs IQN-ILS | STALE (10-16) | `womersleyTube/verification/Allverify --monolithic` | time, Newton; no Krylov |
| cavityFlexibleBottom | levels 1-4, Δt 0.5 (pre-#597) | STALE (10-16) | `cavityFlexibleBottom/verification/Allverify --variants monolithic` | no |
| cavityFlexibleBottom | levels 1-4, Δt 0.5, rerun at `257b2e564` | CURRENT (unmerged branch) | same, `--levels 1,2,3,4 --end-time 300`; level 4 parallel by hand | no (columns empty) |
| cavityFlexibleBottom | paper-repo campaign, meshes 1-3 × Δt 0.5-40 | STALE (2026-05) | none | wall time, memory |
| collapsibleChannel | mesh 1/2/4, Δt on level 2, ρs/ρf 1 and 0 | STALE (10-16) | none (`./Allrun monolithic` by hand) | time; no Newton/Krylov |
| mokLidDrivenCavity | mesh 16-128 with Δt halved | STALE (10-16) | `mokLidDrivenCavity/verification/Allverify --monolithic --study mesh` | time; no Newton/Krylov |
| blobInTreacle | mesh x1/x2/x4 (face-flux row) | CURRENT (contains #597) | none (`./Allrun monolithic` by hand) | no |
| blobInTreacle | Liu temporal study | missing (partitioned only) | none | – |
| TurekHron2006 | FSI1 mesh 1x/2x/4x | STALE (10-17) | `TurekHron2006/verification/Allverify --benchmark fsi1 --coupling monolithic --levels 1,2,4` | time (shared machine), Newton range |
| TurekHron2006 | FSI3 conformal 2x/4x | STALE (10-17; lift strongly affected by #597) | `TurekHron2006/verification/Allverify --coupling monolithic --levels 1,2,4` | 4x only (12 ranks, 3.6 h); Newton range |
| beamInCrossFlow | tutorial Δt 0.05 to 4 s; regression refs | STALE | none (`./Allrun monolithic`) | serial times in commit messages only |
| 3dTube | none; commit-message comparison and timings | STALE / no study | none (`./Allrun monolithic`) | serial 100-step times in commit messages |
| foilInWind | Δt 0.0025 vs partitioned 0.01, first 0.2 s | CURRENT (unmerged branch, pre-#599) | none (`./Allrun monolithic [parallel]`) | time, Newton range |
| membraneRoof | tutorial comparison, 1-4 s mean | STALE (pre-BDF2) | none | relative only ("five times") |
| perpendicularFlap | commit-message comparison | STALE / no study | none | no |
| channelLeaflet, hessenthalerFsi | – | no monolithic variant | – | – |

## 4. Prioritised rerun list for M (all from the tagged release, once tagged)

Every rerun should record: solids4foam commit, OpenFOAM/PETSc versions,
compiler and flags, machine, ranks, and per step the Newton and Krylov
counts and wall time, run one at a time on an unshared machine where cost is
reported.

1. **M Sec. 4, ringAddedMass** `--study monolithic` (Δt and mesh) and
   `--study nonconformal` (AMI, for contribution 3 including the force/power
   balance with `interfaceFluxDiagnostics yes`). Plus the `zeroGradient`
   pressure ablation (options only). Decide how to reproduce the force-lag
   and `devReff` ablations (older commit or a switch).
2. **M Sec. 4, womersleyTube** `./Allverify --monolithic` (all studies).
3. **M Sec. 5, cavityFlexibleBottom**: the four-level rerun at `257b2e564`
   is current for QoIs; rerun only to add Newton/Krylov counts and wall times,
   and to settle the level-4 serial/parallel question. Add the
   `newtonIcoFluid` vs `pimpleFluid` fluid-only comparison (CFD3-like rigid
   plate), which is currently only quoted in a commit message.
4. **M Sec. 6, robustness maps**: new density-ratio × Δt sweeps on
   ringAddedMass and collapsibleChannel (only two density ratios recorded for
   collapsibleChannel, none for the ring); rerun the collapsibleChannel
   monolithic table (no driver: script it or add `--coupling` to its driver).
   mokLidDrivenCavity `--monolithic --study mesh` if it is used in Sec. 5/6.
5. **M Sec. 7, TurekHron2006 FSI3** `--coupling monolithic --levels 1,2,4`
   (and FSI1), with a Δt sweep for the work-precision plot (the driver halves
   Δt with the mesh only; a separate Δt study is needed). High priority:
   #597 changes the lift.
6. **M Sec. 7, blobInTreacle**: rerun the monolithic mesh study and add the
   Liu temporal study for the monolithic coupling (Δt 0.25 to 0.03125 s);
   needs a monolithic option in the driver. The 2D block with flexible tail
   does not exist and would be new set-up work.
7. **M Sec. 8, 3dTube**: first monolithic verification against the
   partitioned levels and the scaling study (strong scaling over ranks,
   `decomposeParMonolithic`), with the #599 PETSc options; nothing recorded
   now.
8. **M Sec. 9, foilInWind**: rerun from the tag with Δt = 0.0025 s (after
   merging `b157ecaf3`), and record the Δt = 0.01 s stagnation log as the
   limitation evidence.
9. Low priority (tutorial README/regression values, not paper data):
   beamInCrossFlow, membraneRoof, perpendicularFlap, cavityFlexibleBottom
   tutorial README.

## 5. Open questions

1. Which commit will be tagged for the paper, and will it include
   `f356c3242` (cavity rerun) and `b157ecaf3` (foilInWind Δt/4)? No tag
   contains #597 yet.
2. Is #594 accepted as result-neutral for the monolithic variants (all use a
   plain `fixedGradient`), or should one case be rerun across it to show this?
3. How should the removed ablations (one-step force lag; `devReff` traction)
   be reproduced for M: rerun at the old commits (`c008e8dd1^`,
   `dbfda65ba^`) or add a debug switch?
4. The ring mesh-sweep numbers in the README (factors 1/2/4) are not
   produced by `--study monolithic` in the current driver; the conformal arm
   of `--study nonconformal` covers them. Which command produced the
   recorded values?
5. The cavity monolithic-minus-partitioned `uy` difference after #597 shrinks
   by only 1.5-1.8 per halving; is a level-5 or Δt check planned before M
   reports it?
6. The womersleyTube monolithic wall amplitude is 3.3-3.5e-4 below the
   partitioned one with an unidentified source; is this to be investigated
   for M Sec. 4?
7. Is `foilInWind` meant to reproduce a published 3D benchmark? Its README
   cites none, and the 2D block with flexible tail has no case at all.
8. Platform for cost: the recorded times mix macOS (M1 Ultra, shared) and
   xenosim; which machine will be the reference for M's work-precision and
   scaling data?
