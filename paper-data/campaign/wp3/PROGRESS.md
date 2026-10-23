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
