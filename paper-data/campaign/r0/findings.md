# R0: every paper case with the quasi-monolithic coupling at the branch head

Code: solids4foam `feature-petsc-snes-quasi-monolithic` at `85b0c1de6`
(`v2.2-1713-g85b0c1de6`). Built on MeluXina by Slurm job 5375410 (`qm-head`,
OpenFOAM v2512, PETSc 3.22.0, HYPRE 2.31.0, GCC 13.3.0, `-O2
-fno-tree-vectorize -march=znver2`); the build log reports no build errors.

Files:
- set-up: `scripts/r0_setup.py`;
- job: `jobs/r0_farm.sh`;
- per-run post-processing: `scripts/r0_post.py`, which uses
  `campaign/scripts/parse_log.py` and the cases' own verification-script
  functions;
- tables: `scripts/r0_collect.py`, which writes `runs.csv`, `qois.csv` and
  `provenance/<run_id>.json`.

All jobs ran on MeluXina, account p201136, partition `cpu`.

Question: does every paper case run to its end time with the
quasi-monolithic coupling at the branch head? Each case runs at tutorial
(coarsest) resolution, with fluid `ddt(U) backward` and the tutorial PETSc
options. The exception is 3dTube, whose solid block uses B1 S1 BoomerAMG.

## What ran

Farm job 5375489 took one exclusive 128-core node. Each case ran in the
background on its own core range (`taskset -c`, MPI binding off). The core
range of each run is in the `cores` column of `runs.csv`. Timings are
indicative only: the cases shared the node.

- ringAddedMass, womersleyTube, cavityFlexibleBottom and blobInTreacle ran
  serially, with `./Allrun monolithic`.
- 3dTube ran through its verification driver: `Allverify --coupling
  monolithic --levels 1 --cores 8`. The driver sets `backward`.
- TurekHron2006 ran through its driver on the conformal monolithic meshes at
  1x:
  - FSI3: `Allverify --coupling monolithic --levels 1 --cores 4`;
  - FSI1: the same with `--benchmark fsi1`, serial.
- collapsibleChannel (`r0-coll-backward-c`) ran serially with `./Allrun
  monolithic`, as an `srun --overlap` step in the same allocation, after a
  set-up fix (see Deviations).
- foilInWind ran on its own node (jobs 5375494 and 5375613): 128 ranks,
  `Allrun monolithic parallel`, `decomposeParMonolithic` with scotch. It
  used Δt = 0.0025 s, with `system/controlDict.monolithic` taken verbatim
  from `b157ecaf3`. That commit is PR #602, which is not on the head yet.

## Results

Newton = Newton iterations per step, mean (max); Krylov = Krylov
iterations per Newton iteration; mem = peak resident memory, summed over
ranks. Each source is the run's row in `runs.csv` and `qois.csv`.

| Case | Run | Status | t reached | Steps | Newton (max) | Krylov | Ranks | Mem (GB) | QoI | Value | Compared with | Diff. |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|
| ringAddedMass | r0-ram-backward-a | completed | 14 | 400 | 2.00 (2) | 18.6 | 1 | 0.20 | ω (rad/s) | 2.17691 | exact 1.80451 | +20.6% |
| womersleyTube | r0-wom-backward-a | completed | 100 | 200 | 2.00 (2) | 23.3 | 1 | 0.21 | profile error | 4.69e-3 | README m2,n100 4.70e-3 | see notes |
| collapsibleChannel | r0-coll-backward-c | completed | 3.5 | 140 | 3.04 (4) | 189 | 1 | 0.25 | first trough (m) | −0.196027 | oomph-lib, same Δt, −0.212956 | −7.95% |
| cavityFlexibleBottom | r0-cav-backward-a | completed | 200 | 400 | 2.01 (5) | 32.1 | 1 | 0.21 | u_y, underside (m) | −0.201575 | README L1 at 200 s: −0.201552 | +0.011% |
| | | | | | | | | | F_y (N) | −5.12351 | README L1: −5.12258 | +0.018% |
| blobInTreacle | r0-blob-backward-a | completed | 10 | 1000 | 1.42 (3) | 24.5 | 1 | 0.19 | steady u_x (m) | 0.116854 | README monolithic x1: 0.116851 | +0.003% |
| TurekHron2006 FSI1 | r0-fsi1-backward-a | completed | 30 | 1120 | 1.38 (2) | 21.3 | 1 | 0.23 | u_y(A) error vs Featflow | 34.96% | README conformal 1x: −35.0% | same |
| TurekHron2006 FSI3 | r0-fsi3-backward-a | completed | 7 | 5000 | 2.00 (3) | 20.3 | 4 | 0.79 | u_y amplitude (m) | 0.020915 | Featflow 0.03499 | −40.2% |
| 3dTube | r0-tube-backward-a | completed | 0.02 | 800 | 2.00 (2) | 11.1 | 8 | 2.11 | u_r,max(A) (m) | 1.59490e-4 | README monolithic L1: 1.5949e-4 | 0.0% |
| foilInWind | r0-foil-backward-e | **diverged** (processor-patch mismatch) | 0.95 of 12 | 380 | 2.44 (4) | 34.1 | 128 | 40.8 | peak trailing-edge u_x, first 0.01 s (m) | 7.67e-8 | README (`b157ecaf3`): 7.7e-8 | −0.4% |

### Notes per case

- **ringAddedMass.** The ω error of +20.6% is the bending stiffness of the
  standard second-order velocity solid on the tutorial mesh. The README
  states 20.7% for the standard solid on that mesh, and the paper uses the
  wet/dry ratio, which cancels it. Newton count: 2.00 per step, as in B0.
  The amplitude loss is 0.023% per period. The README's monolithic table
  gives 0.040%, but for the factor-2 mesh.
- **womersleyTube.** The tutorial runs 2 periods and samples the last one,
  and the errors here are taken over that period. The README table analyses
  the last 2 of 6 periods. Errors against the exact solution (this run;
  README m2,n100):

  | Error | This run | README m2,n100 |
  |---|---:|---:|
  | profile | 4.69e-3 | 4.70e-3 |
  | flow-rate amplitude | 3.7e-4 | 4.7e-4 |
  | wall phase | −2.66e-3 | −2.82e-3 |
  | attenuation | −4.59e-3 | −4.64e-3 |
  | wall amplitude | −5.4e-4 | −1.0e-3 |
  | speed | +2.4e-5 | −1.4e-4 |

  The last two are small differences of small numbers.
- **collapsibleChannel.** The comparison is with the oomph-lib trace at the
  tutorial Δt = 0.025 s (`collapsibleChannel_oomph_dt40.csv`). The two
  troughs are at the same time, t = 0.475 s. The README's monolithic rows
  are at Δt = 0.00625 (level 1: −9.1%). The error comes from the linear
  solid on the 80 × 8 mesh (B2).
  - Krylov iterations: 189 per Newton iteration, the most of any case. This
    is consistent with B2 (272–286 at fluid level 2).
- **cavityFlexibleBottom.** The tutorial monitor point `(4 -1 0.5)` resolves
  to the plate underside (README), so the comparison is with the README's
  underside value at level 1 and 200 s. The README's #597 rerun used Euler.
  - At 200 s the response is still slowly decaying, so the time scheme acts
    through the transient: the change here is 1e-4 (relative).
  - B0 (Euler) gave −0.201546 and −5.122611.
- **blobInTreacle.** The README value was recorded with Euler to t = 3 s.
  The steady value does not depend on the time scheme. The partitioned x1
  value is 0.117301, 0.38% away.
- **FSI1** reproduces the README conformal 1x errors to three digits:
  u_x +15.3%, u_y −35.0%, drag 0.44%, lift +15.1%. The driver reports
  |error|.
- **FSI3, conformal 1x.** The README has no conformal 1x FSI3 row (only 2x
  and 4x). Errors against Featflow:
  - u_x mean −54%, u_x amplitude −51%, u_y amplitude −40%;
  - frequency +8.4%;
  - drag mean +11.6%, drag amplitude −14%;
  - lift amplitude +152%.

  The plate has 5 × 30 cells, a quarter of the tutorial's 1x plate. The
  solution is periodic: the amplitude change over the window is at most
  0.23%. The steps counted are the 5000 coupled steps after
  `couplingStartTime` 2 s; the first 2 s are fluid-only.
- **3dTube** reproduces the README monolithic level-1 row to every printed
  digit:
  - u_r,max = 0.15949 mm at 7.225 ms;
  - u_z,min = −0.08896 mm;
  - t_arr = 5.876 ms;
  - c_p = 4.666 m/s.

  This run used the B1 S1 solid block; the README used the driver's shorter
  BoomerAMG set. Every step took 2 Newton iterations.
- **foilInWind.**
  - **Agreement with the README.** The start-up matches `b157ecaf3`: the
    peak trailing-edge u_x is 7.67e-8 m against 7.7e-8 m.
  - **Convergence.** Every step converged, in 2–4 Newton iterations.
  - **Failure.** At t = 0.9525 s, right after the mesh-motion solve, ranks 42
    and 116 disagree on a shared processor face near the flag, and the run
    aborts with `processorPolyPatch::calcGeometry: face area does not match
    neighbour by 0.0068%`.
  - **Size of the mismatch.** The two copies differ by about 1e-7 m. This
    is the size of the flag displacement then (|u| up to 4.3e-7 m at
    t = 0.925 s), and far above round-off.
  - **Suspected defect.** See `issue_foilInWind_processor_point_mismatch.md`.
  - **Cost of the full run.** At 16 s per step on 128 ranks, the remaining
    run to t = 12 s would take about 21 h.

## Deviations and incidents

- **Fluid `ddt(U)`.** Euler was switched to `backward` in the run copy's
  `system/fluid/fvSchemes.monolithic` for collapsibleChannel,
  cavityFlexibleBottom and blobInTreacle; 3dTube got it from its driver's
  default. ringAddedMass, womersleyTube, TurekHron2006 and foilInWind
  already use `backward`. `ddt(p)` and `ddt(dU)` stay as in the tutorial.
  Every `backward` run completed or, for foilInWind, failed for a reason
  unrelated to the time scheme. No Euler fallback was needed.
- **r0-tube-Euler-a (extra).** The job script reruns with Euler when the
  `backward` run's driver exits non-zero. The 3dTube, FSI3 and FSI1
  drivers exit 1 for any single-level study, on the check "at least two
  levels are required", although every run completed. So 3dTube also ran
  with Euler. This run is kept for information: u_r,max is 4.4% lower and
  t_arr 2.5% earlier than with `backward` (`qois.csv`).
- **collapsibleChannel set-up fix.** `setPoiseuilleFlow/Make/options`
  looks for the solids4foam root by searching upwards from the case. In a
  copy outside the tree it finds nothing, the utility does not build, and
  `Allrun` goes on to the solver without the Poiseuille initial field. That
  first attempt is `r0-coll-backward-a.setupfail`: it was stopped by hand
  and has no results. The copy now points `SOLIDS4FOAM_ROOT` at the built
  tree. The tutorial would benefit from an explicit root, or from `Allrun`
  stopping when the utility fails.
- **foilInWind attempts.**
  1. `r0-foil-backward-a.aborted`: 96 ranks in the farm, about 19 s per step.
     I stopped it at t = 0.03 s because it could not reach t = 12 s within
     the 24 h farm.
  2. `r0-foil-backward-d`: 128 ranks, dedicated node. It aborted at
     t = 0.14 s with `Couldn't create directory processor*/0.14`: the file
     quota of `/project/home/p201287` (1 000 000 inodes, shared with other
     data) was full, at 996 416 files. Every step had converged.
  3. `r0-foil-backward-e`: before this attempt I deleted the processor
     directories of attempts 1 and 2 (about 79 000 files), and set
     `writeInterval` 0.01 → 1 s and `purgeWrite` 100 → 2. The QoIs come
     from the function objects, which write every step. This attempt hit
     the defect above.
- **Not done.** No restarts were used.
- **Solver defect.** One suspected defect was found (foilInWind, above);
  there is an issue file for it.

## Node-hours (p201136)

| Job | Use | Elapsed | Node-hours |
|---|---|---:|---:|
| 5375489 | farm (all cases but foilInWind) | 15.5 min | 0.26 |
| 5375494 | foilInWind attempt 2 | 20.1 min | 0.33 |
| 5375613 | foilInWind attempt 3 | 1 h 42 min | 1.71 |
| total | | | 2.30 |

## Open questions for Philip

1. **foilInWind processor-patch mismatch.** The issue file has the details.
   It needs a code fix, or a check at a lower rank count to see whether it
   depends on the decomposition, before foilInWind can run to 12 s.
2. **FSI3 conformal 1x.** Its errors against Featflow are 40–54% in the
   displacements and +152% in the lift amplitude, and the README has no
   value to compare with. Should R4 include 1x, or start at 2x?
3. **Project file quota.** `/project/home/p201287` is close to its file
   limit (0.92 M of 1 M), mostly from other data. Long parallel runs there
   must write little, or use another project's space.
4. **Fixes for the head.** #602 (the foilInWind Δt) and the
   collapsibleChannel `Make/options` lookup should be on the head before
   the consistent-version reruns.
