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
| smoke test (5 runs) | ring QM/dry/IQN/RN, Womersley QM | Mx p201136 | 5377599 | ring QM/dry/IQN and Womersley QM done, match README; RN running |
| 1a ring QM | 36 wet + 12 dry + 3 tight | Mx p201136 | 5377679 | submitted |
| 1d ring IQN-ILS, RN (standard solid, strong, m2) | 6 (QM in 1a) | Mx p201136 | 5377679 | submitted |
| 1e Womersley QM yes/no, RN, IQN-ILS | 10 + 5 + 5 | Mx p201136 | 5377679 | submitted |
| vST diagnostic D1, D3 (blob x1) | 3 restarts + post-processing | MS | – | done: `../wp0/vST_diagnostic.md` |

Registry: rows of agent A on `campaign/registry` (`68349d0`, then running).

## Notes

- The R0 foilInWind run `r0-foil-backward-e` (Δt 0.0025, 128 ranks)
  diverged at t = 0.95 s (380 steps, 2.44 Newton/step). It covers 0–0.2 s
  for 7a. Run `-d` ended with a quota error when writing its metadata.
- Smoke: ring IQN-ILS strong m2 n25 ω 0.800420 (README 0.80042); 4.23
  iterations/step with the strict test (README legacy 3.86).
