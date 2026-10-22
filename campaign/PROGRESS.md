# Quasi-monolithic paper campaign: progress log

Maintained by the coordinator agent. Plan: `paper-fsi-verification/HANDOFF.md`.
Newest entries first in the log; the status table is always current.

Last updated: 2026-10-22

## Current phase

**Phase B complete** (B0–B3 done; B1 cav and tube on XenoSim, windows from
t = 0 because restarts fail: `paper-data/campaign/b1/issue_mesh_motion_restart.md`).
B1 result: S0 (`redundant` + LU) cheapest for ring and cav; S1 (BoomerAMG)
cheapest for 3dTube, 4–12× faster than S0. **Applying the revised B1
acceptance test** (HANDOFF §10, 21 Oct, later): tight-reference runs S0ref
and S1ref (`snes_rtol`/`snes_stol` 1e-10, `ksp_rtol` 1e-8) for cav (13051)
and tube (13052 S1ref 16 ranks, 13053 S0ref 4 ranks) on XenoSim. Then the
G1 report (`campaign/G1_report.md`, run-matrix costs being collected).
Gate G1 not reached. No main-campaign (R1–R7) runs.

## Status by stream

| Stream | State | Jobs (MeluXina unless noted) | Next action |
|---|---|---|---|
| B0 build | done on MeluXina and XenoSim | MeluXina 5364171 COMPLETED; XenoSim 12759 completed (no build errors, `v2.2-1692-g257b2e564`) | – |
| B0 smoke | **done, passed** (`paper-data/campaign/b0/findings.md`) | 5364272 COMPLETED | – |
| B1 solid PC | **done** (`paper-data/campaign/b1/findings.md`): S0 for ring/cav, S1 BoomerAMG for 3dTube | 5364389 COMPLETED; XenoSim spin-ups 13039 (cav), 13029 (tube); windows 13044 (cav), 13045–13049 (tube) completed, all rc 0; earlier restart-based attempts failed (see log) | – |
| B2 collapsibleChannel AMI | **done** (`paper-data/campaign/b2/findings.md`): AMI 640×8 trough error −1.91% vs conformal 160×8 −4.28%, Newton 2.59 vs 2.70/step, +6% clock (indicative) | 5364293 COMPLETED; XenoSim 13024, 13025 COMPLETED | – |
| B3 Jaiman/Liu estimate | **done** (`paper-data/campaign/b3/estimate.md`): blobInTreacle monolithic temporal study < 0.1 core-h, R6 total 2–12 core-h; block with tail 3–3.5 person-days + ~20–60 core-h (unverified guess) | – | decision at G1 |
| G1 report | in progress | – | write, push, stop |

## Results so far (each number has its source)

| Run | Ranks | Status | Steps | Newton/step | Krylov/Newton | Source |
|---|---:|---|---:|---:|---:|---|
| b0-ram-s1 (ringAddedMass, monolithic) | 1 | completed | 400 | 2.00 (max 2) | 18.6 | `status.py runs/b0` on MeluXina |
| b0-ram-p4 | 4 | completed | 400 | 2.00 (max 2) | 19.0 | same |
| b0-cav-s1 (cavity L1) | 1 | completed | 400 | 2.025 (max 5) | 35.2 | `paper-data/campaign/b0/status.txt` |
| b0-cav-p4 | 4 | completed | 400 | 2.03 (max 5) | 36.8 | same |

ringAddedMass matches the README's expected 2.00 Newton iterations per step.
Cavity L1 Dy = −0.201546 m, Fy = −5.122611 N in serial, 4 ranks and all
repeats, equal to the post-#597 XenoSim value (`paper-data/campaign/b0/b0_compare.csv`).
Timing spread over 3 repeats: solver ExecutionTime ≤ 0.8%, ClockTime 4–7%,
Allrun 7–8%. Decision: 3 repeats, median, wall time over a fixed in-solver
window from a restart.

B2 step 1, partitioned static wall, linear solid, wall-midpoint error against
the README reference −0.14362832 m (source:
`runs/b2/<run_id>/static_result.json` on MeluXina, job 5364293):

| Solid mesh | wallMid (m) | Error | wallQuarter error | Clock (s) |
|---|---:|---:|---:|---:|
| 320×8 | −0.1420235 | −1.12% | −2.51% | 20 |
| 640×8 | −0.1433111 | −0.22% | −0.58% | 48 |
| 1280×8 | −0.1434100 | −0.15% | −0.42% | 98 |
| 640×16 | −0.1432258 | −0.28% | −0.72% | 99 |

Coarsest mesh within 1%: **640×8** (320×8 is just outside, consistent with
the 1.1% recorded in the case README). The error stalls at about −0.15% to
−0.2% from 640×8 to 1280×8, and doubling the cells through the thickness does
not reduce it (640×16 is −0.28%), so the remaining 0.2% is not wall-length
resolution.

B1 ringAddedMass (moderate, factor 2, 100 steps; `paper-data/campaign/b1/b1_windows.csv`):

| Config | Ranks | Newton/step | Krylov/Newton | Clock (s) | QoI diff vs S0tight |
|---|---:|---:|---:|---:|---:|
| S0 redundant LU | 1 / 4 | 2.00 / 2.00 | 23.9 / 24.5 | 39 / 17 | 9.4e-7 / 1.8e-6 (floor) |
| S1 BoomerAMG | 1 / 4 | 2.00 / 2.00 | 47.4 / 53.4 | 54 / 33 | 1.7e-5 / 5.5e-5 |
| S2 bjacobi LU | 4 | 2.00 | 56.6 | 32 | 6.9e-6 |

S1 is 18–30× the S0 floor and costs 1.4–1.9× more. S2 is 4× the floor.

B1 cav (L3, 50-step window, XenoSim) and tube (L2, 50-step window, XenoSim),
clock in s over the window (`paper-data/campaign/b1/b1_windows.csv`):

| Case | Ranks | S0 | S1 | S2 | S0 memory / S1 memory (GB) |
|---|---:|---:|---:|---:|---|
| cav | 1 | **352** | 386 | – | 0.60 / 0.60 |
| cav | 4 | **99** | 109 | 137 | 0.93 / 0.92 |
| cav | 16 | **42** | 48 | 59 | 2.23 / 2.14 |
| tube | 4 | 1 194 | **279** | 337 | 9.2 / 4.6 |
| tube | 16 | 1 296 | **108** | 132 | 24.8 / 6.0 |

All 2.00 Newton/step. QoI differences vs S0tight: cav S0/S1 ≤ 1.1e-5
(1–2 output digits), S2 up to 1.2e-4; tube all 5.5e-5–1.0e-4, S0 itself
7e-5 (tutorial `snes_rtol 1e-4`).

## Environment

| Machine | Tree | Commit | OpenFOAM | PETSc / HYPRE / MUMPS | Flags |
|---|---|---|---|---|---|
| MeluXina | `/project/home/p201287/philip/qm-paper` (`env.sh`) | `257b2e564` (`v2.2-1692-g257b2e564`, PR #233 head) | v2512 (self-built) | 3.22.0 / 2.31.0 / 5.7.3 | `-O2 -fno-tree-vectorize -march=znver2` |
| XenoSim | `~/OpenFOAM/philipc-v2512-qmpaper` (`env.sh`, isolated lib/bin) | `257b2e564` | v2512 | 3.24.1 / 2.33.0 / 5.8.1 | `-O3` |

- Runs: `/project/home/p201287/philip/qm-paper/runs/<stream>/<run_id>/`, each
  with `provenance.json` and `run_meta.json`.
- MPI placement for every run: `OMPI_MCA_rmaps_base_mapping_policy=core`,
  `OMPI_MCA_hwloc_base_binding_policy=core`, bindings reported in the log.
- Status of all runs: on MeluXina,
  `cd /project/home/p201287/philip/qm-paper && python3 -I campaign/scripts/status.py runs/*`

## Scripts (branch `evidence/campaign-g1` of `paper-monolithic-fsi`)

- `campaign/scripts/provenance.py`: writes `provenance.json` (commit, versions, compiler, host, CPU, ranks, Slurm exclusivity, PETSc options blocks).
- `campaign/scripts/parse_log.py`: per-step Newton/Krylov counts of the `Up` system; status classification.
- `campaign/scripts/status.py`: one line per run.
- `campaign/jobs/b0_smoke.sh`: B0 smoke and timing calibration.
- `campaign/scripts/b0_compare.py`: B0 serial/parallel QoI comparison.
- `paper-data/campaign/b2/`: B2 jobs, scripts and `runs.csv` (subagent β).

## Philip's decisions (HANDOFF §10, branch `campaign/handoff`) and how they are applied

| Decision | Applied |
|---|---|
| Fluid `ddt(U)` = `backward` wherever possible (Euler at 257b2e564 in blobInTreacle, 3dTube, collapsibleChannel, cavityFlexibleBottom) | B1 cav/tube windows and the tube spin-up now set `ddt(U) backward` (`b1_setup.py --ddt-u`); the cav windows restart from the Euler spin-up of 20 Oct (recorded as `spinup_ddt_U`). `ddt_U` column in `b1_windows.csv`; will be a `runs.csv` column in every stream. B2 runs (submitted before the decision) keep the tutorial's Euler — to be stated in G1. |
| blobInTreacle: tutorial values (R 0.5, λ 500, μ 50), record R, λ, μ, ρ, inlet profile in R6 findings | noted for R6 |
| One tagged code version for all R results (incl. #611 deforming-wall traction, `meshMotionTotalDisplacement`, `diffusionElastic`); B1, B2 are checks on the current build (`257b2e564`); no R stream before G2 | B1/B2 continue at `257b2e564`; no R runs |
| Drop mesh-motion stiffening ablation; drop route-B old-commit ablations | removed from the plan |
| BoomerAMG is the expected solid-block default; `bjacobi`+LU only as the parallel answer-invariance check | superseded 21 Oct (below) |
| (21 Oct) Use the cheapest solid-block PC per case; hypre is probably only useful for 3D meshes that are not small | B1 criterion = cost (Krylov iterations and clock); QoI difference to S0tight reported, not a gate. Ring: S0 is cheapest. |
| (21 Oct) While MeluXina is out of hours, move work to XenoSim; phase B checks the cases work, not fine meshes | done: B1 cav/tube and B2 step 2 resubmitted on XenoSim (see Deviations 6) |
| mokLidDrivenCavity, beamInCrossFlow, membraneRoof, perpendicularFlap → appendix, no runs | removed from the plan |
| (21 Oct, `campaign/handoff` 024f045) No release lock: get every case running from the head of `feature-petsc-snes-quasi-monolithic`, fix the version later; G2 dropped; viscousStressTranspose default `no`; timing later on one machine | to be applied in the G1 run matrix; B1/B2 stay at `257b2e564` (checks) |
| (21 Oct, `campaign/handoff` 52b95c4) B1 acceptance: compare with a tight reference (snes 1e-10, ksp 1e-8); accept if the QoI difference ≤ 5% of the case's discretisation error; per-case tolerances; choose the solid PC on 3dTube/cav by cost at equal accuracy; no issue file for the ring trigger; rebuild from the branch head before reusing B1 for the paper | S0ref/S1ref configurations added (`b1_setup.py`), runs 13051–13053; `b1_analyse.py` writes `qoi_maxreldiff_vs_ref` and a per-quantity CSV |

## B1 design (as submitted)

- Configurations of the UpU solid block: S0 `redundant`+LU; S1 BoomerAMG
  with the membraneRoof solid settings; S2 `bjacobi`+`sub_pc_type lu`
  (parallel only); S0tight = S0 with `snes_rtol`, `snes_stol` ×0.01
  (iterative floor). S1n (nodal coarsening) only if S1 converges poorly.
- ringAddedMass: moderate added mass, mesh factor 2, 50 steps/period,
  2 periods from t = 0 (no developed state needed: free vibration from the
  initial velocity); ranks 1, 4.
- cavityFlexibleBottom L3 (factor 4), Δt 0.5, inlet ramp 20 s: serial
  spin-up to t = 100 s, windows t = 100 → 125 (50 steps); ranks 1, 4, 16;
  per-region `decomposePar`.
- 3dTube L2 (factor 2), Δt 1.25e-5, tutorial schemes: serial spin-up to
  t = 2 ms (160 steps), windows of 50 steps; ranks 4, 16, 32;
  `decomposeParMonolithic`.
- S0tight is run at every rank count, which also tests rank independence.
- One run per configuration (B0 shows solver time repeats to < 1%).
- Peak memory per rank from `/usr/bin/time` (`run_meta.json`), not for
  ring (run through its Allrun).
- Scripts: `campaign/scripts/b1_setup.py`, `campaign/jobs/b1.sh`.
- Note: 3dTube's monolithic tutorial uses `snes_rtol 1e-4` (other cases
  1e-6), so its S0tight floor is at 1e-6.

## Deviations from the handoff

1. Timing machine is MeluXina (per `~/.claude/CLAUDE.md`), not ICHEC/Sonic:
   XenoSim is fully loaded and cannot give exclusive nodes.
2. Two PETSc stacks (see table). Timings are never compared across machines.
3. Run drivers live in `paper-monolithic-fsi/campaign/` for now; committing
   them to a solids4foam branch on the build tree would change its
   `git describe`. They go to `verification/qm-paper-<stream>` from a separate
   worktree when each stream completes.
4. From A4: S2 in B1 must be `bjacobi` + `sub_pc_type lu` (the coupler rejects
   a bare LU solid PC in parallel).
5. B2 runs are serial: the collapsibleChannel Allrun has no parallel path, and
   the recorded 2008 s baseline is serial; the baseline is rerun on MeluXina
   for a same-machine cost comparison.
6. **XenoSim for the rest of phase B (21 Oct).** XenoSim's Slurm has
   `TaskPlugin=task/none` (no cpusets): jobs are not confined to their cores
   and the node runs at load ~185/192, so runs use `QM_BIND=none` (no
   mpirun binding) and are not exclusive (`QM_EXCLUSIVE=false` in B2
   `run_meta.json`; `--exclusive` stripped at submission). Clock times there
   are indicative only; iteration counts and QoIs are not affected. Rank
   counts capped at 16 (3dTube spin-up on 16 ranks, windows at 4 and 16; the
   32-rank windows dropped). Build: PETSc 3.24.1 / HYPRE 2.33.0 / MUMPS 5.8.1,
   `-O3`, same commit `257b2e564`. Both spin-ups now run on XenoSim with
   `ddt(U) backward` and `restart yes` (the MeluXina cav spin-up could not be
   restarted, see log), so the earlier Euler-spin-up caveat no longer applies. B2 step 2 keeps the tutorial's Euler `ddt(U)` (same as
   step 1 and the recorded 2008 s baseline).

## Open questions for Philip

None open (budget and acceptance test answered 21 Oct, see decisions).

## Log

- **2026-10-22** Read the decisions of 21 Oct on `campaign/handoff`
  (024f045, 52b95c4), which I had not applied: G2 dropped, run from the
  branch head; revised B1 acceptance test against a tight reference. Added
  S0ref/S1ref (`snes_rtol`/`snes_stol` 1e-10, `ksp_rtol` 1e-8,
  `ksp_max_it` 10000) and submitted cav (13051, 4 ranks) and tube (13052
  S1ref 16 ranks, 13053 S0ref 4 ranks). Thresholds from the READMEs (5% of
  the change between the two finest meshes): cav Uy 3.5e-4 (L3→L4 0.70%),
  Fy 2.9e-5 (0.057%); tube u_r,max 2.5e-5 (L1→L2 0.05%), u_z,min 9e-4
  (1.85%), Robin–Neumann levels. Subagent collecting R-stream costs for the
  G1 run matrix.

- **2026-10-22** All B1 windows completed (rc 0). Cheapest PC: S0 for cav
  (S1 +10–14%, S2 +38–40%), S1 for 3dTube (S0 4.3× slower at 4 ranks,
  12× at 16; S0 `redundant` LU does not scale and its memory grows with
  ranks). Fixed `b1_analyse.py` (a QoI difference of exactly 0 was shown
  blank; self-comparisons skipped; new `qoi_output_resolution` column, the
  monitors write 6 digits). B1 findings, CSV (ring + cav + tube), status and
  provenance in `paper-data/campaign/b1/`.

- **2026-10-22** First from-start window done: cav S0 1 rank (13044),
  250 steps, 2.18 Newton/step, 58.6 Krylov/Newton, 1778 s, rc 0
  (`runs/b1/b1-cav-S0-p1/run_meta.json` on XenoSim); consistent with the
  spin-up (2.23). All six window jobs (13044–13049) running.

- **2026-10-22** Restart test 13042 (spin-up 13039 wrote the restart fields
  of both the solid and the mesh-motion solid): the mesh-motion SNES again
  starts at norm 3.413470681598 (identical) and its linear solve fails
  (DIVERGED_ITS 10000). The restart fields are not the cause → suspected
  solver issue, written up in
  `paper-data/campaign/b1/issue_mesh_motion_restart.md` (Section 9); not
  worked around in code. B1 windows changed to run from t = 0 to
  t0 + 50 Δt; `b1_analyse.py` now reports Newton, Krylov, clock and QoI
  differences over the last 50 steps only (checked: the ring rows of
  `b1_windows.csv` are reproduced). Cost: cav ~3 h, tube 16-rank ~1.6 h per
  run, 4-rank runs as separate 4-core jobs. (A first attempt of the test,
  13040, failed with rc 127: `sbatch --wrap` runs sh, which lacks `source`.)

- **2026-10-22** Cav window S0-p1 (13036) started but stalled: the fluid
  mesh-motion SNES (D) starts at function norm 3.41 after the restart,
  against 3.3e-3 at the spin-up's last step, and its first linear solve did
  not converge in 6 min (spin-up: 19 Krylov iterations). So `restart no`
  for the mesh-motion solid (total-displacement, neo-Hookean) does not give
  a consistent continuation, despite the solver's message. Cancelled 13036
  and the queued tube windows 13037. Test: spin-up writing the mesh-motion
  restart fields too (`B1_FLUID_RESTART=1`, default) → 13039, then a 3-step
  window (13040). If the D residual then starts near 3e-3, windows restart
  as designed; if not, I write `issue_mesh_motion_restart.md` and run the
  windows from t = 0 without restarts. (Also: windows no longer copy the
  spin-up's run_meta.json/provenance.json; a copied run_meta.json made
  status.py report the running window as diverged.)

- **2026-10-22** 2-step serial cav window test (13035): the restart check
  passes (warning for `restart no` on the mesh motion, as intended); the test
  itself then failed in `MPI_Init` because I launched it with `srun`, and
  XenoSim's Open MPI has no Slurm PMI support (batch jobs don't use srun).
  Tube spin-up done (13029). Tube windows 13030 failed in set-up: the tube
  mesh-motion model (`linearGeometryTotalDisplacement`, linear elastic) has
  a regex-keyed coefficients block that `set_restart` didn't match; fixed
  and resubmitted as 13037.

- **2026-10-22** Cav windows 13028 failed again at start-up, same message:
  this time from the **fluid mesh-motion** solid model
  (`nonLinearGeometryTotalLagrangianTotalDisplacement`, neo-Hookean, in
  `constant/fluid/solidProperties`), not the solid region (which now has its
  restart fields). That model is total-strain with no history, so the
  windows set `restart no` for it, as the solver's message allows
  (`b1_setup.py`: `set_restart(dest, "fluid", "no")`); applies to the tube
  windows too. Failed dirs in `runs/b1/failed-20261022/`. Resubmitted as
  13036, with a 2-step serial test (13035, dev partition) ahead of it.

- **2026-10-22** B2 done on XenoSim (13024, 13025, ~75 min each, serial).
  Conformal baseline reproduces the README (−0.20650 vs −0.20691 m); AMI with
  the 640×8 solid cuts the trough error from −4.28% to −1.91% with no loss of
  Newton convergence. `b2_post.py` counted the mesh-motion SNES solves as
  steps (480, mean 2.95); fixed to count the coupled Up solve only (240,
  2.70), and gained a `ddt_U` column. Cav spin-up redone on XenoSim (13027,
  28 min, 2.23 Newton/step, restart fields written). `status.py` crashed on
  missing values; fixed.

- **2026-10-21** B3 estimate written (no runs). blobInTreacle monolithic
  fluid uses `ddt(U) Euler` at 257b2e564; R6 must switch it to `backward`.

- **2026-10-21** First XenoSim B1 jobs failed in set-up, no results lost:
  (a) cav windows 13021: the solid model refuses a restart because the
  spin-up never wrote the restart fields (`restart false` default;
  "Continuing from time 100, but the fields a consistent restart needs were
  never written"); (b) tube spin-up 13022: `decomposeParMonolithic` needs a
  `monolithicCoeffs` block (regions, weights, interface patches) that the
  3dTube decomposeParDict lacks. Fixed in `b1_setup.py` (`set_restart`,
  `MONOLITHIC_DECOMPOSITION` with fluid `wall` / solid `inner-wall`).
  Failed directories kept in `runs/b1/failed-20261021/` on XenoSim. Both
  spin-ups resubmitted (13027, 13029), now with `ddt(U) backward`; windows
  chained (13028, 13030).

- **2026-10-21** Philip: use XenoSim while MeluXina is out of hours; pick
  the cheapest solid PC. XenoSim build 12759 finished cleanly. Job scripts
  made portable (`QM_BIND`, `QM_EXCLUSIVE`, `B1_SPINUP_RANKS`, `B1_LIST`,
  B2 tutorial path from `QM_ROOT`). Submitted on XenoSim: 13021 cav windows,
  13022 → 13023 tube, 13024 / 13025 B2. Cancelled MeluXina 5364390, 5364391,
  5364295, 5364354.

- **2026-10-20** Received Philip's decisions (HANDOFF §10). B1 set-up now
  uses `ddt(U) backward` for cav/tube windows and runs the tube spin-up on 32
  ranks (whole-node billing). Held jobs pick the updated scripts up when
  released; the tube windows job 5364391 depends on the cancelled spin-up and
  must be resubmitted with a new spin-up.

- **2026-10-20** B1 ring windows done (job 5364389): S1 and S2 exceed the S0
  iterative floor (Section 8 trigger; findings in `paper-data/campaign/b1/`).
  Cavity L3 spin-up done (5364387). Found the MeluXina budget at 99.1%;
  cancelled the serial 3dTube spin-up and held all pending jobs. Waiting for
  Philip.

- **2026-10-20** B1 set up and submitted (design above). Spin-ups 5364387,
  5364388; windows 5364389–5364391.

- **2026-10-20** B0 complete (5364272, 16.7 min, exclusive node): all 10 runs
  completed; serial and 4-rank QoIs identical; cross-machine agreement with
  the XenoSim post-#597 cavity L1 value. Findings in
  `paper-data/campaign/b0/findings.md`. Starting B1 set-up.

- **2026-10-20** B2 static wall completed (5364293, 5.9 min): 640×8 is the
  coarsest solid mesh within 1% (−0.22%). Submitted the monolithic AMI run,
  fluid level 2 with the 640×8 solid (5364354, serial, exclusive node).

- **2026-10-20** Read handoff and A1–A4. Built PR #233 head on MeluXina
  (6.6 min) and queued it on XenoSim. Wrote provenance, log parser and status
  scripts. First smoke job (5364184) failed in 9 s from a `set -u` error in
  my job script (no case ran); fixed and resubmitted as 5364272. ringAddedMass
  smoke passed (2.00 Newton/step, serial and 4 ranks). Subagent β submitted
  B2 step 1 (5364293) and the conformal baseline (5364295).
