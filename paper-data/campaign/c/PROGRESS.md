# Run agent C: heavy cases (WP4 FSI3, WP6 3dTube) — progress

Branch `evidence/m-runs-c`. Machine: MeluXina, account p201136. Code: the
R0 build `/project/home/p201287/philip/qm-head` (solids4foam
`v2.4-1103-g85b0c1de6`, head of `feature-petsc-snes-quasi-monolithic`).
Run directories: `/project/home/p201136/philip-agentC/runs/`.

## Decisions in force (23 Oct 2026)

- QM run copies use the partitioned fluid schemes: no `cellLimited`,
  `div(phi,U) Gauss linearUpwind grad(U)`, `gradSchemes default
  leastSquares`, `ddt(U) backward` (Philip, via the coordinator).
- `viscousStressTranspose`: undecided (likely `yes` for second-order
  consistency, pending the blob debugging). The FSI3 4x and 3dTube L3
  production runs are **on hold** until the decision.

## 4a — FSI3 QM-AMI, tutorial meshes

### 1x check (Mx job 5377601, one exclusive node, 3 × 8 ranks)

Driver: `./verification/Allverify --coupling monolithicAMI --levels 1
--cores 8` (Δt 1 ms, t = 7 s, last 1 s analysed), as in the V runs.
Set-up edits: `jobs/fsi3_setup.py`; job: `jobs/fsi3_1x_check.sh`.

| Variant | div(phi,U) | vST | Purpose |
|---|---|---|---|
| A | `linearUpwind cellLimited leastSquares 1` (tutorial) | no | reproduce V QM-AMI 1x |
| B | `linearUpwind grad(U)` | no | scheme effect |
| C | `linearUpwind grad(U)` | yes | transpose effect |

V QM-AMI 1x (paper-fsi-verification `ring-monolithic`,
`paper-data/hronturek_fsi3_monolithic_tutorial_meshes.csv`; M1, 8 ranks,
831 s): `u_x` mean −2.1424 mm, `u_x` amplitude 2.0720 mm, `u_y` amplitude
28.831 mm, `u_y` frequency 5.5945 Hz, drag mean 453.97 N/m, drag amplitude
22.331 N/m, lift amplitude 221.74 N/m.

Status: running.

### 4x production

Registry row claimed (M run agent). On hold (vST decision).

## 6a — 3dTube QM L3

Registry row claimed (M run agent). On hold (vST decision).

## Timing jobs (4b, 6b, 6c, 4c)

To prepare; not submitted.

## Core-hours

| Project | Job | Node-hours |
|---|---|---|
| p201136 | 5377601 | running |
