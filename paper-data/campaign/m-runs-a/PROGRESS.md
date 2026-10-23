# Run agent A (2-D cases: WP1, WP2, WP5, WP7): progress

Code: solids4foam `feature-petsc-snes-quasi-monolithic` at `85b0c1de6`
(`v2.4-1103-g85b0c1de6`). MeluXina runs use the R0 build
`/project/home/p201287/philip/qm-head` (`env.sh`). The mac-studio
diagnostics use the WP0 build (`claude-runs/m-wp0`, read-only). No solver
code changes.

Machines: xenosim was saturated on 23 Oct (load ~160/192, nine 32-core jobs
queued), so the correctness runs go to MeluXina as farm jobs on account
p201136 (Philip, 23 Oct). Run directories are on p201136 storage
(`/project/home/p201136/philip-ma/runs`), because p201287 is at 92% of its
file quota (the R0 foil `-d` run hit "Disk quota exceeded").

## Decisions applied

- `viscousStressTranspose no`, set explicitly, except 1e (yes and no).
- QM schemes as the case's partitioned `fvSchemes`, with no limiters. Ring
  and Womersley already match (Gauss linear, leastSquares, ddt(U)
  backward), so no scheme edits were needed.
- Partitioned: `requireAllResidualMeasures yes`; IQN-ILS `couplingReuse 0`
  written explicitly.
- Tolerances. Ring QM uses the tutorial values (snes 1e-6/1e-6, ksp 1e-4)
  plus a tight B1 check (1e-8/1e-8/1e-6) at m2 n100 for the 3 levels.
  Womersley QM is tight, as in the WP0 m2 n50 rows.

## Status

| Item | Runs | Where | Job | Status |
|---|---|---|---|---|
| smoke tests | 5 + 5 | Mx p201136 | 5377599, 5377771 | done |
| 1a ring QM | 36 wet + 12 dry + 3 tight | Mx p201136 | 5377679 | done |
| 1d ring IQN-ILS, RN (standard solid, strong, m2) | 6 (QM in 1a) | Mx p201136 | 5377679 | done |
| 1e Womersley QM yes/no, RN, IQN-ILS | 10 + 5 + 5 | Mx p201136 | 5377679 | done (`WP1_findings.md`) |
| 1b ring zeroGradient p | 6 | Mx p201136 | 5377777 | done |
| 1c ring AMI, coarser/finer solid x conservative/interpolated | 36 wet + 6 dry | Mx p201136 | 5377777 | done |
| 1f BDF2 start-up | analysis of 1a (first period excluded); Womersley periodicity | local | – | done: no start-up effect |
| 2a cavity QM L1-L4 | 4 (L4 on 4 ranks) | Mx p201136 | 5377777 | L1-L3 done; L4 running |
| 2b cavity interpolate(U) linear | L2, L3 | Mx p201136 | 5377777 | L2 done; L3 running |
| 2c checkMesh | on 2a/2b final states | Mx | – | after 2a; partitioned strict directories no longer exist (see notes) |
| 5b blob QM time steps | 4 | Mx p201136 | 5377777 | done |
| 7a foilInWind QM dt 0.01, 0.005; IQN-ILS dt 0.01 | 3 (+1 failed set-up at 128 ranks) | Mx p201136 | 5377780, 5377781, 5377823 | QM 0.01 stalls at 0.05 s (as #602); QM 0.005 to 0.2 s; IQN-ILS 0.01 fails at 0.08 s (stopped, reported) |
| vST diagnostic D1, D3 (blob x1) | 3 restarts + post-processing | MS | – | done: `../wp0/vST_diagnostic.md` |

Registry: rows of agent A on `campaign/registry`; WP1, 5b, 7a closed (7a IQN-ILS `failed`); cavity rows running.

Cost so far (whole-node allocations on p201136): batch 1 2.1 node-h, smoke 0.2, foil 0.5, batch 2 ~2 node-h so far and about 8 in total (the cavity L4 run holds its node alone for its last ~6 h).

## Notes

- 7a IQN-ILS on 128 ranks (job 5377782) stopped in the first step: the
  partitioned PETSc solid solve (4 608 cells over 128 ranks) reached 10 000
  Krylov iterations. Rerun on 8 ranks (5377823): outer iterations per step
  4, 5, 5, 6, 8, 10, 18, then 50 without convergence at t = 0.08 s
  (residual 2.5e-5 against 1e-5, strict test). Not retried with other
  settings; reported.
- 2c: the strict partitioned cavity directories behind the
  `partitioned_strict` CSV rows are not on the mac-studio any more (only
  legacy-test Aitken/IQN-ILS runs at dt 0.5 from September). A head rerun
  of Aitken strict L1-L4 at the recorded time steps would cost about 2
  core-hours; proposed, not run.

- The R0 foilInWind run `r0-foil-backward-e` (Δt 0.0025, 128 ranks)
  diverged at t = 0.95 s (380 steps, 2.44 Newton/step). It covers 0–0.2 s
  for 7a. Run `-d` ended with a quota error when writing its metadata.
- Smoke: ring IQN-ILS strong m2 n25 ω 0.800420 (README 0.80042); 4.23
  iterations/step with the strict test (README legacy 3.86).
