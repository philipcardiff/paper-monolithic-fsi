# WP3 progress (run agent B)

## 23 Oct 2026

- Inputs read: run-agent brief, submission plan §§3–4, registry, WP0
  findings, reuse map, B2 findings (13109–13111 done: AMI 640×8 at fluid
  L2 −1.91%, L4 −1.83%; chosen for 3b), verification paper PR #13 (no
  overlap).
- Philip (23 Oct): launch approved; extended ring level = ρf 14 000
  (μ ≈ 100); gradient `leastSquares` in both 3b arms.
- Failure criterion and caps fixed before the runs (README).
- MeluXina p201136: 457/681 node-hours used this month before WP3. Nodes
  are exclusive (`OverSubscribe=EXCLUSIVE`), so cost = node wall time ×
  128 cores; runs are packed onto one node per map.
- Smoke job 5377659 (4 ring + 4 collapsible short runs): ring pipeline
  verified (Aitken/IQN-ILS/QM pass; RN at strong n12 hits the 200-iteration
  cap at step 10, classified `cap`). Fixed a false `nan` match on the
  `trapFpe` start-up line.
- 3a submitted: job 5377695 (80 runs, one node, 2 h per-run limit, 2 h 15
  min job limit). Registry row: running.
- 3b: not submitted. Waiting for the smoke cost per step and Philip's go
  (estimated cost above 300 core-hours once node billing is counted).
- **3a done** (5377695, 9 min 53 s on one node; 2.66 core-hours of CPU,
  0.16 node-hours billed). 79/80 pass; RN strong n12 hits the 200-iteration
  cap at step 10. Mean iterations per step: Aitken 3.2–10.2, IQN-ILS 3.0–6.1,
  RN 3.0–42, QM 2.0 everywhere. All couplings agree on ω to ~0.1%; the +6.3%
  error at n200 is the standard solid on mesh 2 (second order, cf. README
  +1.58% on mesh 4), the same for every coupling. With the predictor, the
  strict test and the 200 cap, the partitioned couplings do not fail on this
  case even at μ = 100: the map separates them by iterations, not by
  pass/fail. CSVs and draft map in `3a/`.
- Collapsible smoke: QM at Δt 0.025, ρs/ρf 1 aborts at t = 0.275 s in the
  fluid mesh-motion SNES (`DIVERGED_LINEAR_SOLVE` of the pseudo-solid
  motion solver), after Newton steps of 3 iterations. Judgement point for
  Philip (mesh-motion failure, not coupling).
- Collapsible smoke (Δt 0.025, ρs/ρf 1, MeluXina, 40 min node): Aitken,
  IQN-ILS, RN pass (mean 40.5, 18.6, 31.1 iterations per step; trough
  −1.79% against oomph-lib in all three); QM fails at t = 0.275 s in the
  mesh-motion SNES (status `mesh`).
- Philip (23 Oct): 3b on XenoSim, 16 cores (MeluXina would bill ~380
  core-hours for one exclusive node); QM mesh-motion failures counted as
  failures and labelled `mesh`.
- 3b claimed in the registry; submission on XenoSim waits for the load
  average to fall below 165 (it was 193/192 at 14:40).
- MeluXina p201136 use so far: smoke 0.67 + 3a 0.16 node-hours (≈ 107
  billed core-hours).
- 3b submitted on XenoSim at 15:06 (load5 155): job 13279, 16 tasks; registry running.
- 18:07 check (3 h in, load5 169): 67/80 3b runs finished, 13 running
  (all past t = 0.3 s); no setup failures. So far: QM passes every
  Δt ≤ 0.0125 at every density (2.0–3.0 Newton/step); QM Δt 0.025 fails
  `mesh` at t = 0.275 s for all five densities. Aitken and IQN-ILS fail
  (`cap`) for ρs/ρf ≤ 0.1 at small Δt within the first steps, pass at
  ρs/ρf 10. RN at ρs/ρf = 0: floating-point exception on the first
  coupling iteration (Robin coefficient ∝ wall density vanishes, as the
  verification README notes), classified `nan`.
- Coordinator (23 Oct): `viscousStressTranspose` will be removed and the
  transpose wall treatment hard-coded; QM results at the current head will
  be rerun after the fix. No further QM runs until the fixed build is
  announced (none were pending: all 3a/3b QM runs had already finished).
  QM rows carry `pre-vST-fix` in the `runs.csv` notes (3a regenerated; 3b
  will have it); registry status becomes `superseded` once the fixed build
  exists.
