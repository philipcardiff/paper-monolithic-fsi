# B0: environment, smoke test and timing calibration

Code: solids4foam PR #233 head `257b2e564` (`v2.2-1692-g257b2e564`), built
on MeluXina against a self-built OpenFOAM v2512, PETSc 3.22.0, Hypre 2.31.0,
MUMPS 5.7.3, gcc 13.3.0 with `-O2 -fno-tree-vectorize -march=znver2`.
All runs: Slurm job 5364272, one exclusive `cpu` node (mel0198, AMD EPYC 7H12,
`OverSubscribe=NO`), runs one after another. Ranks mapped and bound to cores
(`OMPI_MCA_rmaps_base_mapping_policy=core`,
`OMPI_MCA_hwloc_base_binding_policy=core`). Provenance:
`provenance/<run_id>.json`. Driver: `campaign/jobs/b0_smoke.sh`.

## Smoke test

Source: `status.txt` (output of `campaign/scripts/status.py`).

| Run | Case | Ranks | Status | Steps | Newton/step (max) | Krylov/Newton |
|---|---|---:|---|---:|---|---:|
| b0-ram-s1 | ringAddedMass | 1 | completed | 400 | 2.00 (2) | 18.6 |
| b0-ram-p4 | ringAddedMass | 4 | completed | 400 | 2.00 (2) | 19.0 |
| b0-cav-s1 | cavityFlexibleBottom L1 | 1 | completed | 400 | 2.025 (5) | 35.2 |
| b0-cav-p4 | cavityFlexibleBottom L1 | 4 | completed | 400 | 2.03 (5) | 36.8 |

- ringAddedMass converges in exactly two Newton iterations in every step, as
  its verification README states.
- The repeats give identical Newton and Krylov counts.

## QoI consistency

Source: `b0_compare.csv` (`campaign/scripts/b0_compare.py`).

- cavityFlexibleBottom L1 plate displacement at t = 200 s: Dy = −0.201546 m
  and Fy = −5.122611 N in serial, on 4 ranks and in all three repeats
  (identical to the printed digits).
- This equals the post-#597 level-1 value recorded on XenoSim with PETSc
  3.24.1 and `-O3` (`monolithic_597`, `uy_bot` = −0.201546 m, in
  `cavityFlexibleBottom/verification/results/four_level_partitioned_monolithic.csv`
  on `verification/cavityflexiblebottom-partitioned-fine`). Note that `uy_bot`
  there is sampled from `pointD` at the plate node and here from the
  tutorial's `solidPointDisplacement` function object; the values coincide.
- ringAddedMass, 4 ranks against serial: the largest difference in the Dy
  history is 2.3e-7 of the maximum |Dy|.

## Timing calibration

Same job three times on the exclusive node (source: `status.txt`). ExecutionTime
is the solver's CPU time of rank 0, ClockTime its wall time (whole seconds),
Allrun the wall time of the whole script including meshing, decomposition and
reconstruction.

| Run | ExecutionTime (s) | ClockTime (s) | Allrun (s) |
|---|---|---|---|
| ringAddedMass serial, r1/r2/r3 | 37.43 / 37.24 / 37.15 | 46 / 45 / 47 | 60.9 / 59.4 / 63.4 |
| cavity L1 4 ranks, r1/r2/r3 | 65.54 / 65.53 / 65.73 | 72 / 75 / 77 | 99.2 / 104.3 / 108.0 |

- Spread (max − min over median): ExecutionTime 0.8% (ring) and 0.3%
  (cavity); ClockTime 4% and 7%; Allrun 7% and 8%.
- The solver's computation repeats to better than 1%; the extra spread is in
  start-up, file output and the pre/post-processing utilities.

**Decision.** Timing runs use three repeats and report the median, as the
handoff proposes. The timed quantity is the wall-clock difference across a
fixed window of steps inside the solver (from a restart), not the Allrun or
whole-job time, and windows are long enough (≥ 100 s) that the 1 s ClockTime
resolution is below 1%. Output writing inside timing windows is switched off
where the case allows. Rank placement: map and bind by core, as above, for
every timing run.

## Not done

- XenoSim smoke test: the XenoSim build (job 12759) is still waiting for
  resources on a fully loaded machine. MeluXina is the campaign machine; the
  XenoSim post-#597 cavity value above already gives a cross-machine check.
