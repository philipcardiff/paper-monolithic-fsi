# Computational campaign for the quasi-monolithic FSI paper: coordinator handoff

You are the **coordinator agent** for the computational campaign behind the
solver paper (repository `philipcardiff/paper-monolithic-fsi`, target CMAME).
You run on Philip Cardiff's hardware, where OpenFOAM, PETSc and HYPRE are
available, and you may use the cluster (ICHEC, UCD Sonic) through its batch
system. Read this whole file before doing anything.

## 0. Ground rules

1. **No solver development.** You may edit case dictionaries, PETSc options,
   `Allrun`/`Allverify` drivers, job scripts, post-processing scripts and case
   set-ups. You do not change C++ source. If a run exposes a solver defect,
   stop that stream and write it up (Section 9). Philip decides.
2. **Two gates need Philip's approval:** G1 (the final campaign specification,
   after the pre-campaign checks B1 to B3) and G2 (PR #233 merged into
   `development` and a release tag made). Stop at each gate and report. Do
   not run the main campaign (R1 to R7) before G2. Every run in the paper
   comes from the tag.
3. **Token budget (5-hour limit):**
   - At most **two subagents at a time**.
   - Never watch a running simulation from the model. Submit jobs with
     scripts, then check them with one summary script that prints one line
     per run (`campaign/scripts/status.py`, which you write). Look at a raw
     log only to diagnose a failure, and then only `tail -n 40` or a `grep`.
   - Parse logs with committed Python scripts, never by reading them.
   - Give subagents short, self-contained prompts. Ask for reports of at
     most 300 words, with paths to the files they wrote.
   - Prefer few long batch jobs to many interactive steps.
4. **Provenance for every run** (Section 6): commit, OpenFOAM version, PETSc
   and HYPRE versions, compiler and flags, host, CPU model, rank count, and
   exclusive or shared node. A result without provenance does not count.
5. **Git:**
   - Commit run drivers and verification notes to solids4foam on branches
     named `verification/qm-paper-<stream>`, starting from the tag (from the
     PR #233 head before G2).
   - Commit tables, figure data and findings to `paper-monolithic-fsi` on
     branches named `evidence/<stream>`, under `paper-data/`.
   - Push your branches. Open a PR only when a stream is complete. Never
     push to `development` or `main`, and never force-push.
   - End every commit message with the attribution lines your harness gives
     you, if any. Do not put model names in files.
6. **Report honestly.** A failed or stalled run is a result. Record it with
   its status and do not silently rerun it with different settings. When you
   change a setting, record the change and the reason.
7. **Never state a number without a source file.** Every number in a findings
   file points to a CSV row or log.

## 1. Context in one page

There are two companion papers:

- **Verification paper (V)**, `philipcardiff/paper-fsi-verification`. It is
  solver-neutral, uses only partitioned results, and establishes reference
  values with their uncertainty. It also establishes the **strict coupling
  convergence test**: `requireAllResidualMeasures yes`, which requires
  max(r1, r2) to be below the tolerance. The legacy test, min(r1, r2), can
  accept unconverged steps (solids4foam issue #552).
- **Solver paper (M)**, this campaign. It presents a quasi-monolithic
  cell-centred finite volume FSI method: the `NewtonQuasiMonolithic`
  coupling, the `newtonIcoFluid` fluid, the velocity solids
  `nonLinearGeometryTotalLagrangianVelocity` and `linearGeometryVelocity`,
  PETSc SNES with JFNK (`snes_mf_operator`), and a fieldsplit preconditioner.
  The code is in draft PR solids4foam/solids4foam#233 (branch
  `feature-petsc-snes-quasi-monolithic`).

M must not repeat V. **M reports:**
- the monolithic-minus-partitioned difference as the mesh is refined;
- Newton and Krylov iteration counts;
- work–precision (error against cost) at equal verified accuracy;
- robustness maps;
- ablations of design choices;
- parallel scaling.

M uses V's reference values (with their uncertainties) as targets. It does
not present new reference-convergence tables.

M's sections and the streams that feed them:

| M section | Stream |
|---|---|
| 4. Verification against exact solutions (ringAddedMass, womersleyTube) and ablations | R1 |
| 5. Consistency with partitioned coupling (cavityFlexibleBottom) | R2 |
| 6. Robustness (density ratio × Δt maps) | R3 |
| 7. Accuracy and cost on benchmarks (Hron–Turek FSI3; Liu half-cylinder = blobInTreacle; block with tail if approved) | R4, R6 |
| 8. 3D performance and scaling (3dTube) | R5 |
| 9. Limitations (foilInWind time-step limit) | R7 |

**Documents to read first.** They are in `paper-monolithic-fsi` under
`paper-data/`; if they are not on `main` yet, look on the `evidence/a*`
branches.
- `a1_monolithic_study_inventory.md`: existing monolithic results, whether
  they predate #594/#597, driver invocations, and a rerun list.
- `a2_discretisation_differences.md`: `newtonIcoFluid` against `pimpleFluid`,
  candidate explanations of the monolithic–partitioned offsets, and the
  discriminating runs.
- `a3_pr233_merge_readiness.md`: what has to happen before the tag.
- `a4_ablation_reproducibility.md`: which ablations need only an option
  change on the tag, which need an older commit, and which can cite
  existing numbers.

Then read, on the solver branch:
- `src/solids4FoamModels/fluidSolidInterfaces/newtonQuasiMonolithicCouplingInterface/README.md`
- each case's `tutorials/fluidSolidInteraction/<case>/verification/README.md`

Where these documents contradict this handoff, they are more recent: follow
them and say so in your report.

## 2. Phase B0: environment and smoke test (before anything else)

1. Build solids4foam at the PR #233 head, with PETSc and HYPRE, on the
   machines you will use. Write `campaign/scripts/provenance.py`, which
   writes `provenance.json` into a case directory (fields in Section 6).
2. Smoke test in serial and on 4 ranks:
   `ringAddedMass` (`./Allrun monolithic`) and `cavityFlexibleBottom` level 1.
   Check the Newton counts against the READMEs: ringAddedMass should need
   exactly 2.00 Newton iterations per step.
3. Calibrate timing:
   - Run the same short job three times on an exclusive node.
   - Record the spread in wall time.
   - Use that spread to decide how many repeats the timings need (usually
     3, reporting the median).
   - Record the CPU pinning and binding options you used, and use them for
     every timing run.

## 3. Phase B: pre-campaign checks (these decide the specification)

### B1. Preconditioner for the solid block

Background: every monolithic tutorial uses `fieldsplit_solid_pc_type
redundant` with `redundant_pc_type lu`, which gathers the solid onto one rank
for an exact LU. In April, per-rank `bjacobi`+LU was replaced because the
solid response of foilInWind *changed with the rank count* (commit
`2f99ea065`). A preconditioner must never change a converged answer, so that
episode means the Newton tolerance was too loose at the time.

BoomerAMG works well for the partitioned JFNK solid but has never been tried
on the monolithic solid block. Copy the active settings in
`tutorials/fluidSolidInteraction/membraneRoof/system/solid/fvSolution` and
prefix every option with `fieldsplit_solid_`, keeping
`fieldsplit_solid_ksp_type preonly`.

Configurations:
- **S0**: `redundant`+LU (the baseline)
- **S1**: BoomerAMG (`fieldsplit_solid_pc_type hypre`,
  `fieldsplit_solid_pc_hypre_type boomeramg`, plus the copied settings)
- **S2**: `bjacobi`+LU (to reproduce the April issue; parallel only)

Cases, each run over a fixed window from a restart, not to the end time:

| Case | Window | Ranks |
|---|---|---|
| ringAddedMass, moderate added mass | 2 periods at 50 steps per period | 1, 4 |
| cavityFlexibleBottom level 3 | 50 steps from a developed state | 1, 4, 16 |
| 3dTube level 2 | 50 steps after start-up | 4, 16, 32 |

Measure for each run:
- the QoI at the end of the window;
- mean Newton iterations per step and mean Krylov iterations per Newton
  iteration;
- wall time per step and peak memory.

Also rerun S0 with `snes_rtol` and `snes_stol` 100 times tighter. This gives
the iterative-error floor of the QoIs.

Acceptance and decision:
- The QoIs of S1 and S2 must agree with S0 to within that floor. If one does
  not, that is a finding: report it and do not adopt that configuration.
- Adopt BoomerAMG as the campaign default if it meets the acceptance test
  and costs no more than S0 at 4 or more ranks.
- Otherwise keep S0, and record why the 3D scaling stream uses it.

If BoomerAMG converges poorly on the vector solid block, try one variant with
nodal coarsening (`fieldsplit_solid_pc_hypre_boomeramg_nodal_coarsen 1` with
the block size set). Do not go beyond that.

### B2. collapsibleChannel: solid resolution with a non-conformal interface

Background: the monolithic trough error against oomph-lib, at
ρs/ρf = 1 and Δt = 0.00625, is −9.1%, −4.1% and −2.4% on fluid levels 1, 2
and 4. The conformal solid meshes there are 80×8, 160×8 and 320×8.
- The case already uses the geometrically nonlinear velocity solid
  (`nonLinearGeometryTotalLagrangianVelocity`).
- The error comes from the standard second-order spatial discretisation on
  elongated solid cells: the partitioned static wall is 16.7%, 6.0% and 1.1%
  too stiff on the same meshes.
- The high-order solid is not available for velocity solids and will not be
  added for this paper.
- AMI interfaces now work in the monolithic coupling, so the solid can be
  refined along the wall independently of the fluid.

Steps:
1. Partitioned static wall (cheap): solid meshes 320×8, 640×8, 1280×8 and
   640×16, compared with the static reference already used in the case's
   verification README. Find the coarsest mesh within 1%.
2. Monolithic, fluid level 2, with that solid mesh through AMI:
   - `interfaceTransferMethod AMI`;
   - `conservativeTractionTransfer yes`;
   - `useUndeformedArea yes` on the solid `solidTraction` interface patch.
   Run at ρs/ρf = 1 and Δt = 0.00625 to t = 1.5 s. Report the first-trough
   error against oomph-lib and the cost, against the conformal level-2 result
   (−4.1%, 2008 s).
3. Decision for G1: if the trough error is at most 1% at acceptable cost, M
   Section 6 reports accuracy as well as robustness for this case, with AMI.
   Otherwise the case is robustness-only.

### B3. Jaiman/Liu cases (decided at G1; no new runs in phase B)

A1 found:
- The Liu, Jaiman and Gurugubelli (2014) elastic half-cylinder **is
  `blobInTreacle`**. Its temporal-accuracy study (Δt from 0.25 to
  0.03125 s) exists only for partitioned coupling. Adding the monolithic
  arm is cheap and needs no new case (stream R6).
- No 2D block-with-flexible-tail case exists on any branch. foilInWind is
  the only 3D block-with-flag case, and its README cites no benchmark.

For G1, estimate the cost of the blobInTreacle monolithic temporal study
and the effort of building the block-with-tail case from Jaiman and Joshi
(2022). Do not build the block-with-tail case unless Philip approves it.

### Gate G1

Write `campaign/G1_report.md` (at most about two pages) on branch
`evidence/campaign-g1`, with:
- the B0 to B2 results;
- the B3 estimate;
- the **proposed final run matrix**: Section 4, adjusted using A1 to A4 and
  B1 to B3, with the expected core-hours per stream and in total;
- the solver settings to freeze (the PETSc options of each case);
- open questions.

Push the branch, tell Philip, and **stop**.

## 4. Phase R: the main campaign (only after G2)

At G2, Philip merges PR #233 and creates a tag. The A3 audit found the
following; check them in the G1 report so Philip can act before tagging:
- The tag should contain `f356c3242` (the cavityFlexibleBottom rerun, on
  `verification/cavityflexiblebottom-partitioned-fine`) and `b157ecaf3`
  (foilInWind at Δt/4, on `fix/foilInWind-monolithic-timestep`). Neither is
  on the PR branch yet.
- The physics-preconditioner code and the "Physics PC inner solvers" blocks
  in the `fvSolution.monolithic` files should be removed before tagging.
- The existing tag v2.4 does not contain the coupling.
- The verification drivers record file hashes but not the git commit or the
  PETSc, HYPRE and MUMPS versions, so `provenance.py` is required.

1. Rebuild from the tag on every machine and record `git describe`.
2. Rerun the B0 smoke test and confirm the Newton counts are unchanged.

Every run below comes from the tag, with the settings frozen at G1.

**Common protocol:**
- *Equal tolerances.* Monolithic runs use `snes_rtol` and `snes_stol` as
  frozen at G1. Partitioned runs use the strict test
  (`requireAllResidualMeasures yes`) with a coupling tolerance whose
  iterative error is at or below the monolithic floor measured in B1.
  Record both.
- *Timing.* Use exclusive nodes and the pinning from B0. Report the median
  of the repeats. Time a fixed window started from a restart. Report
  core-hours per simulated second and wall time per step. Never compare
  timings from different machines or node types.
- *Accuracy.* Use full runs. Errors are measured against V's references:
  exact solutions, oomph-lib, or V's extrapolated values with their stated
  uncertainty. Do not invent new reference values.
- *Partitioned schemes:* Aitken, IQN-ILS and Robin–Neumann, as used by V for
  each case. Each case lists which ones are needed.
- *Failure statuses:* `completed`, `diverged` (NaN, inverted cell, solver
  failure), `stalled` (maximum iterations without convergence), `timeout`.
- *Stale results (A1).* Only three recorded monolithic results include the
  #597 continuity fix: the cavityFlexibleBottom rerun, the blobInTreacle mesh
  study and foilInWind at Δt = 0.0025 s. Treat everything else as needing a
  rerun from the tag: ringAddedMass, womersleyTube, collapsibleChannel,
  mokLidDrivenCavity, TurekHron2006 FSI1/FSI3, 3dTube, beamInCrossFlow,
  membraneRoof and perpendicularFlap. #597 moved the rigid-plate lift by
  about 10 percentage points, so FSI3 has priority.
- *Schemes.* Several monolithic tutorials use Euler for the fluid `ddt(U)`,
  and the convection schemes and solid stabilisation factor (0.1 or 0.5)
  differ between cases. Add the `ddt`, `div(phi,U)` and stabilisation
  settings of every case to its `runs.csv` notes. Use second-order time
  integration (`backward`) wherever a temporal order is claimed, and list
  any case that cannot in the G1 report.
- *Iteration counts.* No driver records Krylov counts, and only some record
  Newton counts. Extract both from the logs (`snes_monitor`,
  `ksp_converged_reason`) with your parsing scripts.
- *Drivers.* These cases have a monolithic option in their driver:
  - ringAddedMass: `--study monolithic` (time steps only) and
    `--study nonconformal` (refined meshes);
  - womersleyTube and mokLidDrivenCavity: `--monolithic`;
  - cavityFlexibleBottom: `--variants monolithic`;
  - TurekHron2006: `--coupling monolithic --levels 1,2,4`, adding
    `--benchmark fsi1` for FSI1.

  collapsibleChannel, blobInTreacle, beamInCrossFlow, 3dTube, foilInWind,
  membraneRoof and perpendicularFlap have none, so write job scripts for
  them.

### R4. Hron–Turek FSI3 work–precision (longest; submit first)

- **Meshes.** Use the *same conformal* meshes for both couplings, 1x/2x/4x
  as in the `TurekHron2006` verification README (`--coupling monolithic`).
  That set-up uses a quarter of the tutorial's solid cells. Also run
  partitioned IQN-ILS (strict test) on these meshes, so that differences
  measure the coupling, not the mesh.
- **Accuracy runs.** Run both couplings on all three levels to the end time
  in the README.
- **QoIs.** u_x mean and amplitude, u_y amplitude and frequency, drag mean
  and amplitude, lift amplitude (smoothed as in V). Compute the error against
  Featflow and V's values, with the 3–5% reference uncertainty stated in V.
- **Order check for V.** Confirm, after #597, the observed order of the
  monolithic u_x mean on 2x→4x. Before the fix the error was 11.5% then
  5.9%, about order 1. V will cite one sentence on this: it tells whether
  V's order-1 FSI3 sequence comes from the discretisation and set-up rather
  than the coupling.
- **Timing.** Start from a periodic-state restart and time 2 oscillation
  periods, with the same rank count for both couplings at each level.
- **Tolerance sweep on 2x.** Monolithic `snes_rtol` at 1e-4, 1e-6 and 1e-8;
  partitioned strict tolerance at 1e-4, 1e-5 and 1e-6. Report the cost and
  the QoI change. This is the iterative-error side of work–precision.
- **Output.** A work–precision figure (error against core-hours per
  simulated second) for each displacement and force QoI.

### R5. 3dTube scaling and preconditioner ablation (submit with R4)

- **Consistency.** Run the monolithic coupling to the end time on levels 1 to
  3. Compare u_r,max, u_z,min, t_arr and c_p with V's partitioned three
  levels (Robin–Neumann, IQN-ILS). Report the differences per level.
- **Strong scaling.** Level 2 at 1, 2, 4, 8, 16, 32 and 64 ranks, and level 3
  at 16, 32, 64 and 128 ranks if the allocation allows. Run both the
  monolithic coupling and partitioned Robin–Neumann over a fixed window of
  50 steps. Report wall time per step, parallel efficiency, Newton and
  Krylov counts, and memory. Use `decomposeParMonolithic` and record the
  decomposition method.
- **Preconditioner ablation** on level 2 at 8 ranks, over the same window:
  - Schur factorisation: upper against full;
  - Jacobian and preconditioner lagging: 1 against 8;
  - `ksp_rtol`: 1e-4 against 1e-3;
  - solid block: the B1 choice against the alternative;
  - fluid velocity block: ILU(0) against BoomerAMG;
  - the assembled Jacobian as the operator (no `snes_mf_operator`): expect
    linear Newton convergence, and record the Newton residual histories.
  Each variant must reproduce the baseline QoIs to within the iterative
  floor. Report any that do not.

### R3. Robustness maps (many small runs; use an array job)

- **ringAddedMass:** ρs/ρf from the weak to the strong added-mass settings of
  the existing study, extended down to the smallest ratio that runs, crossed
  with 12, 25, 50, 100 and 200 steps per period.
- **collapsibleChannel**, fluid level 2: ρs/ρf of 10, 1, 0.1, 0.01 and 0
  (massless; use the case's own switch), crossed with Δt of 0.025, 0.0125,
  0.00625 and 0.003125. Run to the first trough, or t = 1.5 s. Use the
  existing density-sweep driver in its verification README.
- **cavityFlexibleBottom** level 3 (optional, cheap): Δt of 0.0625, 0.125,
  0.25, 0.5 and 1.0.
- **Schemes:** Aitken, IQN-ILS, Robin–Neumann (strict test, maximum 100
  coupling iterations) and quasi-monolithic.
- **Recorded per cell:** status, mean iterations per step, wall time, and
  the QoI error against the exact or oomph-lib reference.
- **Output:** a map per case (status as colour, iterations as the label) and
  a CSV.

### R1. Exact solutions and ablations

- **Reruns.** `ringAddedMass/verification/Allverify --study monolithic` and
  `--study nonconformal`, and `womersleyTube/verification/Allverify
  --monolithic`, if A1 marks them stale or their commit differs from the tag
  in code they use.
- **Timings** on the same node: the monolithic coupling against IQN-ILS and
  Robin–Neumann.
- **Ablations, following A4's routes** (details and file:line references
  in `a4_ablation_reproducibility.md`). Route A is an option on the tag;
  route B is an older commit built in a separate install, with its hash
  recorded; route C cites the recorded before/after numbers.

  | Ablation | Route | How |
  |---|---|---|
  | Interface pressure: zero gradient against normal-momentum gradient | A | ringAddedMass: change the interface `type` in `0/fluid/p.monolithic`. The coupler only warns. Report the frequency error and the amplitude loss per period: the zero-gradient state also adds coupling damping. The historical numbers in `3e93daef6` mix this with solid-velocity extrapolation, so use the rerun |
  | Traction: `devReff` against wall flux | C | blobInTreacle README. The traction-only change is order 1.4 → 2.0; the current 1.9 also includes #597 |
  | Solid force lag | C | 2.0, 10.6, 18.3% → 0.17, 0.71, 1.26% loss per period (`dcbe04505` → `c008e8dd1`). Use route B at `dcbe04505` only if Philip asks |
  | Continuity: `div(U)` against face flux (#597) | B | At `98211d90e`, two arms in one build. First confirm that `div(U) Gauss skewCorrected linear` reproduces the current code on one run |
  | Jacobian: matrix-free against assembled | A | Remove `snes_mf_operator`. No numbers are recorded, so record the Newton residual histories (part of R5) |
  | Preconditioner and lagging | A | PETSc options (R5) |
  | Conservative against interpolated AMI traction | A | `ringAddedMass --study nonconformal`, once with each `conservativeTractionTransfer` setting, with `interfaceFluxDiagnostics yes` |
  | Mesh-motion stiffening | C | TurekHron2006 README. Ask Philip which level inverted at t = 2.76 s |

### R2. cavityFlexibleBottom consistency

- **Runs.** Levels 1 to 4 for the monolithic coupling and for partitioned
  Aitken (strict test) from the tag, unless A1 shows that the
  `verification/cavityflexiblebottom-partitioned-fine` reruns
  (20 October 2026) used code identical to the tag for this case. In that
  case, only time them.
- **Records.** Newton counts and wall time; these columns are blank in the
  existing CSV.
- **Discriminating runs** (from `a2_discretisation_differences.md`):
  - *Cavity offset* (0.14%, 0.08%, 0.05% on levels 2 to 4; this is the #597
    shift itself, since before #597 the couplings agreed to 0.008–0.02%).
    The leading candidate is the continuity-flux interpolation: the
    monolithic coupling uses `skewCorrected linear`, `pimpleFluid` uses
    `linear`. Run the monolithic coupling on levels 2 and 3 with
    `interpolate(U) linear`. Also run `checkMesh` on the existing final
    states of both couplings to compare skewness; the two couplings use
    different mesh-motion solvers.
  - *Womersley offset* (wall radial amplitude −3.3e-4 against
    Robin–Neumann; fluid quantities agree to within 7e-5). The leading
    candidate is the interface viscous traction:
    - the monolithic coupling passes `nuEff*snGrad(U)`, the partitioned one
      `n & devReff`;
    - on a deforming wall they differ by a physical term, μ grad(u·n), which
      is not a discretisation error and does not refine away.

    First redo the Fourier analysis over periods 4–5 to rule out a start-up
    transient; this needs no new run. A run that confirms the cause needs a
    traction variant in the code, so **raise it at G1. Philip decides
    whether a traction change is in scope.** Until then, the claim that the
    `devReff` traction is first order applies to stationary walls
    (blobInTreacle) only.

### R6. Liu half-cylinder (blobInTreacle) and, if approved, block with tail

- **blobInTreacle, monolithic:**
  - Rerun the mesh study at x1, x2 and x4 from the tag.
  - Add the Liu et al. (2014) temporal-accuracy study with the monolithic
    coupling: Δt from 0.25 to 0.03125 s, with the same error metric and
    reference Δt as the partitioned study in its verification README.
  - Time both couplings.
  - This is M's direct comparison with the finite element formulation the
    solver is based on. In V, the same case only appears as a spatial
    self-convergence study.
- **Block with flexible tail:** only if Philip approves it at G1.

### R7. foilInWind time-step limit (supplementary)

- Run the monolithic coupling at Δt = 0.01, 0.005 and 0.0025 to t = 0.2 s.
- Record where Newton stalls: the residual history and the line-search
  behaviour, as in commit `b157ecaf3`.
- Record the cost at the working Δt against partitioned IQN-ILS at
  Δt = 0.01.
- One run per Δt. This documents a limitation; do not try to fix it.

## 5. Execution order and subagents

```
B0 ─► B1 ┐
     B2 ┼─► G1 report ─► [Philip approves] ─► [Philip merges #233, tags] ─► rebuild + smoke
     B3 ┘
After G2:
  submit R4 accuracy runs and R5 L3 runs first (longest queue time)
  then R3 array jobs, R1, R2, R7 (short) while R4/R5 are queued or running
  then R4/R5 timing windows (need restarts from the accuracy runs)
  R6 blobInTreacle with the short runs; block with tail only if approved
```

Suggested subagent use (two at a time at most):

- **Subagent α (heavy cases):** R4 and then R5. Case preparation, job
  scripts and post-processing scripts; it submits and leaves. A later
  invocation runs the analysis.
- **Subagent β (many small runs):** B2, then R3, then R1, R2, R6 and R7.
- **You (the coordinator):** B0 and B1 yourself, since they decide the
  settings; queue submission and `status.py`; merging results into the
  CSVs; the gate reports and the final summary.

Between steps, end your turn instead of polling. If your harness supports
scheduled wake-ups, check job status every few hours with `status.py`.

## 6. Data formats (all streams)

Put each stream's output in `paper-monolithic-fsi/paper-data/campaign/<stream>/`:

- `runs.csv`, one row per run, with these columns:
  `run_id, stream, case, study, coupling, scheme, level, fluid_cells,
  solid_cells, interface, dt, rho_ratio, ranks, nodes, node_type, exclusive,
  code_commit, tag, of_version, petsc_version, hypre_version, compiler,
  compile_flags, snes_rtol, snes_stol, ksp_rtol, coupling_tol,
  convergence_test, solid_pc, status, t_end, n_steps, iters_mean, iters_max,
  ksp_per_newton_mean, wall_s, wall_s_per_step, core_h, core_h_per_sim_s,
  peak_mem_gb, window, repeats, notes`

  `iters_*` means Newton iterations for the monolithic coupling and coupling
  iterations for partitioned runs; the `coupling` column says which.
- `qois.csv`: `run_id, qoi, value, reference, reference_source, rel_error,
  uncertainty_of_reference, notes`
- `provenance/<run_id>.json`, written by `provenance.py`: the output of
  `git describe --always --dirty` (and the commit hash), `foamVersion` /
  `$WM_PROJECT_VERSION`, PETSc version (from `petscversion.h`), HYPRE
  version, `$WM_CC --version`, `$WM_COMPILE_OPTION`, compile flags,
  hostname, CPU model (`lscpu`), rank count, date, and the full
  `fvSolution` PETSc options block.
- `findings.md`: what was run, results with references to CSV rows,
  deviations from this plan with their reasons, and open questions. Write
  it in the style of the existing `paper-fsi-verification/paper-data/*.md`
  files.
- `scripts/`: post-processing and plotting scripts that produce every table
  and figure from the CSVs, so the manuscript can be regenerated.

## 7. Definition of done for each stream

A stream is done when:
- every planned run has a row with a status;
- every completed run has QoIs, provenance and timing;
- the figures and tables are generated by script from the CSVs;
- `findings.md` is written;
- both branches are pushed;
- a PR is open in each repository;
- Philip has a summary of no more than 300 words.

## 8. Things that would change the plan (report at once; do not work around them)

- A preconditioner or rank count changes a converged QoI by more than the
  iterative floor.
- The tag gives Newton counts or QoIs different from the PR #233 head in B0.
- A run that previously completed now fails.
- The monolithic and partitioned couplings on the same meshes do not get
  closer under refinement.
- The FSI3 order after #597 differs clearly from about 1.
- The cost would exceed the core-hours stated in the G1 report by more than
  50%.

## 9. Reporting a suspected solver defect

Write `paper-data/campaign/<stream>/issue_<short-name>.md` containing:
- the minimal case and commands;
- the expected and observed behaviour, with log excerpts of no more than
  40 lines;
- the commit;
- your hypothesis.

Stop that stream and tell Philip. Do not open GitHub issues yourself; Philip
decides.

## 10. Decisions log (read again before the G1 report)

**20 October 2026 (Philip):**

- **Interface viscous traction:** this will be fixed in a solids4foam PR into
  `feature-petsc-snes-quasi-monolithic` (branch
  `fix/monolithic-deforming-wall-traction`). The fix changes every
  monolithic result on a deforming wall. Do not start the R-stream reruns
  that use moving walls until the tag includes it. B1 and B2 may run before
  then; for B2, say in the G1 report which code you used.
- **Ablations:** do not show an older, poorer option for completeness. Keep
  an ablation only if it is cheap (an option on the tag) and insightful:
  - keep: interface pressure, conservative AMI traction, matrix-free
    against assembled Jacobian, and the preconditioner and lagging
    settings;
  - drop route B reruns from old commits (the continuity arm at
    `98211d90e`, the force lag at `dcbe04505`);
  - the recorded before/after numbers may be cited in a sentence; they need
    no runs.
- **PR #581** (the `foamPetscSnesHelper` split) will be merged into the
  solver branch before the tag. Also pending: #602 (foilInWind Δt/4), #609
  (the cavity rerun), the PR removing the coupler's physics preconditioner
  (branch `chore/monolithic-pr233-cleanup`), #604 (3dTube) and #608
  (TurekHron2006 on the tutorial meshes). The tag comes after these.
- **Release:** a named tag plus Zenodo, decided near submission. Record the
  commit hash for every run in the meantime.

**20 October 2026, later (Philip):**

- **Fluid time scheme:** use `backward` for the fluid `ddt(U)` in every case
  that reports a temporal order or a time-step study, and preferably in all
  paper cases. At 257b2e564, blobInTreacle, 3dTube, collapsibleChannel and
  cavityFlexibleBottom use Euler. Add a `ddt_U` column (or note) to
  `runs.csv`.
- **blobInTreacle parameters:** the tutorial has radius 0.5, λ = 500 and
  μ = 50. An older draft of the paper had radius 0.1 and E = 1e5. Use the
  tutorial values, and record the radius, λ, μ, density and inlet profile
  in the R6 findings, so the paper and its geometry figure can be checked
  against them.
- **All paper results come from one code version with every fix in it,**
  including the long cases run to the end. Fixes to wait for:
  - solids4foam#611 (viscous traction on deforming walls);
  - the dedicated mesh-motion solid model (`meshMotionTotalDisplacement`,
    branch `feature/fsi-displacement-mesh-motion`) and `diffusionElastic`.
    These avoid the FSI3 mesh inversion, so the mesh-motion stiffening
    ablation is dropped;
  - any similar fix found before the tag.

  B1 and B2 are only checks and may use the current build. Do not start any
  R stream until G2.
- **Solid-block preconditioner:** in Philip's experience BoomerAMG is
  usually better than `bjacobi`. In B1, treat BoomerAMG as the expected
  default, and keep `bjacobi`+LU only as the parallel answer-invariance
  check.
- **Cases not used in M Sections 4–9** (mokLidDrivenCavity, beamInCrossFlow,
  membraneRoof, perpendicularFlap) go to an appendix for the first full
  draft. Give them no campaign runs beyond what is already recorded, unless
  Philip asks.

**21 October 2026 (Philip): no release lock; get every case running first.**

This **replaces** the earlier rules that no R stream may start before G2 and
that all paper results must come from one tag.

- **Current goal:** get every paper case running with the quasi-monolithic
  solver and fix every monolithic issue found on the way. Run from the head of
  `feature-petsc-snes-quasi-monolithic` (rebuild when it moves). Record the
  commit of every run, as before.
- **Consistent version later:** once it is clear that every case runs,
  Philip will fix the version, and the cases whose results are affected by
  later fixes are rerun. No tag or release is made before then.
- **G2 is dropped as a gate.** G1 (the campaign specification, B1/B2
  answers) still applies to decisions, not to running cases.
- **viscousStressTranspose:** #611 was merged, then its default was set to
  `no` on the solver branch (`021affbc4`), because the term moved the steady
  blobInTreacle result 2% away from the partitioned one (suspected
  first-order wall error). Runs use the default. The blobInTreacle (x1/x2/x4)
  and womersleyTube (m2) comparisons with `viscousStressTranspose yes` and
  `no` are still wanted; see solids4foam#611.
- **Budget:** run correctness work wherever capacity exists (XenoSim, Sonic,
  MeluXina when the budget allows). Keep timing runs to one machine with
  exclusive nodes, and leave them until the cases run.

**21 October 2026, later: answer to the B1 question (Section 8 trigger on ringAddedMass).**

Philip asked the coordinating session to decide, and the decision is as follows.

- **Revised acceptance test.** The trigger came from the test, not the
  solvers. At the tutorial tolerances (`snes_rtol` 1e-6, `ksp_rtol` 1e-4)
  each preconditioner leaves a different iterative error after two Newton
  iterations, so "within S0's floor" is a test only S0 can pass. Instead:
  - compare every configuration with a **tightly converged reference**
    (`snes_rtol` and `snes_stol` 1e-10, `ksp_rtol` 1e-8; preconditioner
    irrelevant at that tolerance; check that S0tight and S1tight agree to
    round-off level);
  - **accept** a configuration if its QoI difference from that reference is
    at most **5% of the case's discretisation error** (for the ring: of the
    finest-level wet/dry error in the verification README; for cases without
    an exact solution: of the finest-level change between the two finest
    meshes).
- **Per-case solver tolerances.** For every paper case, set `snes_rtol`
  (and `ksp_rtol` where needed) so that the default configuration meets the
  5% rule. Record the tolerance in `runs.csv`. Expect tighter values for
  ringAddedMass and womersleyTube (about `snes_rtol` 1e-8, about +40% cost)
  and the tutorial values elsewhere. Timing comparisons with partitioned
  coupling use these tolerances, with the strict coupling test on the
  partitioned side, so that both run at equal verified accuracy.
- **Solid-block preconditioner.** Do not choose it on the ring: a small 2-D
  solid block is where an exact LU is cheapest. Decide on 3dTube (and the
  cavity) from cost at equal accuracy under the rule above, and per case if
  needed: LU for small 2-D solid blocks, BoomerAMG where it is cheaper. The
  ring result (S1 BoomerAMG about 2× Krylov iterations, 1.4–1.9× time) is
  reported as such.
- **Not a defect.** No issue file is needed. The rank-count difference for
  S0 (at the floor) is fine.
- **Code version.** Rebuild from the current head of
  `feature-petsc-snes-quasi-monolithic` before the B1 cavity/tube analysis
  is reused for the paper. It now includes #609–#611, the physics-PC
  removal and `viscousStressTranspose no`.

**22 October 2026 (Philip): road to submission.**

Read `paper-data/submission_plan.md` (branch `manuscript/submission-plan`).
It replaces the R1–R7 list with work packages WP0–WP8, sorted by paper
section. Main points:

- **Approved to start now:**
  - **WP0:** rebuild at the solver branch head; finish B1 and B2; runs 0b/0c,
    which decide the `viscousStressTranspose` default.
  - **8a:** the coarse-mesh layers of the geometry figures, from
    `figures/scripts/mesh_layer.py`. Commit the PDFs and JSONs to
    `figures/mesh/`.
  - The other work packages wait for Philip's go-ahead on how many run
    agents to launch.
- **MeluXina:**
  - use the **Amir/Colm project** first, from today;
  - the "xenosim" project only if needed;
  - **never** the project running Hron–Turek x8 (Petar and Simon).

  Confirm the project IDs with `myquota` before submitting jobs. MeluXina
  is also the timing machine.
- **ParaView on XenoSim:** render on the NVIDIA GPU. Check with
  `nvidia-smi`; use an EGL/headless build if available.
- **Field images:** next to each case, from a medium or fine level (coarse
  only as placeholders).
- **Animations:** for the transient cases, as supplementary material, using
  `pvbatch` scripts under `campaign/scripts/animations/` in this
  repository. Show Philip a cheap sample first.
- **Block with flexible tail:** dropped (solids4foam#615).
