# R-fix reruns of agent A's quasi-monolithic runs (24–25 October 2026)

Code: `feature-petsc-snes-quasi-monolithic` at `1252bd2e5` (`git describe`
`v2.2-1725-g1252bd2e5`): #618 (transpose viscous term always on, in the wall
pressure gradient, wall value from a decomposition-independent least-squares
fit of the boundary velocity, cached once per residual) and #617 (tutorial
schemes: `ddt(U)`, `ddt(dU)`, `ddt(p)` backward, `linearUpwind grad(U)`,
`interpolate(U)` as in the partitioned file). Run copies use the merged
tutorial files as they are; no `viscousStressTranspose` entry. MeluXina,
account p201136: farm job 5382220 (118 runs, one exclusive node, 2 h 40 min)
and foilInWind jobs 5382221–5382223 (128 ranks each). Every run completed.
Set-ups and tolerances otherwise as in `../m-runs-a/` (same scripts,
`ma_run.py` batch 7). Partitioned results are not repeated (unchanged by the
fix). Rows: `runs.csv`, `qois.csv`, `provenance/`; foilInWind data in `7a/`.

## Results against the pre-fix runs (`../m-runs-a/`)

**ringAddedMass.** 2.00–2.01 Newton iterations per step everywhere.
- 1a wet/dry ratio errors slightly smaller everywhere; strong m1/m2/m4 n100
  −0.0324/−0.0039/−0.0005% → −0.0312/−0.0035/−0.0004%; strong m1 n25
  −0.0468 → −0.0454%; weak and moderate changes ≤ 0.0007%. Tight
  tolerances change ω by at most 3.6e-9 (B1 met).
- 1b zero-gradient interface pressure: unchanged to 0.001% (strong
  −0.335/−0.199/−0.108%, first order).
- 1c AMI: all ratio errors within 0.0135%; interpolated and conservative
  transfer differ by at most 0.0025%.
- 1d QM arm: strong m2 n25/50/100 in the 1a set.

**womersleyTube (1e).** QM minus Robin–Neumann (head RN runs of
`../m-runs-a/`; m2 n50 against WP0 RN):

| Cell | wall amp | wall phase (rad) | attenuation |
|---|---:|---:|---:|
| m1 n200 | +8.6e-5 | −4.6e-5 | −2.6e-4 |
| m2 n200 | −1.5e-4 | −2.9e-5 | −1.3e-5 |
| m4 n200 | −1.7e-4 | −3.6e-5 | +1.4e-5 |
| m2 n50 | −1.6e-4 | −2.6e-5 | −5.7e-6 |
| m2 n100 | −1.5e-4 | −2.8e-5 | −7.9e-6 |
| m2 n400 | −1.4e-4 | −3.0e-5 | −8.5e-6 |

The pre-fix vST-no offset (phase −4.8e-4 rad at every cell, amplitude
−3.2 to −3.6e-4) is gone; the remaining amplitude offset is the size of the
RN/IQN-ILS spread. Time-step orders 1.98–2.07; 2 Newton iterations per step.

**blobInTreacle.** Steady u_x (x1/x2/x4, 1/2/4 ranks) 0.116390 / 0.119224 /
0.119991: −0.72 / −0.39 / −0.18% from the WP0 partitioned values (vST no
before: −0.33/−0.29/−0.16%; vST yes before: −2.34/−1.04/−0.44%); order 1.9,
extrapolated 0.12028, within 0.05% of the partitioned extrapolation. Newton
2.00/2.01/2.62. 5b time steps (t = 1 s): u_x 0.0552143, 0.0559736,
0.0561266, 0.0561436 (Δt 0.25 … 0.03125 s); observed orders 2.31 and 3.17;
2.0–3.0 Newton iterations per step. At Δt 0.03125 s 0.70% below the
partitioned README value (0.0565398; pre-fix +0.12%), consistent with the
steady x1 difference.

**cavityFlexibleBottom.** Steady u_y L1–L4 −0.201551 / −0.228439 /
−0.235436 / −0.237183 (pre-fix −0.201546 / −0.228468 / −0.235448 /
−0.237187): QM minus the head partitioned strict rerun +0.468 / +0.176 /
+0.084 / +0.054% (pre-fix +0.47 / +0.16 / +0.08 / +0.05%). 2b with
`interpolate(U) linear`: L2 +0.065%, L3 +0.000%. Newton 1.64–1.67 per step;
time to steady (1e-3) 138 s (L1) and 124 s (L2–L4), as before.

**foilInWind (7a), to t = 0.2 s, 128 ranks.** Δt 0.01 still stalls at
t = 0.05 s (50 Newton iterations, DIVERGED_MAX_IT; steps before 4, 4, 4, 7);
Δt 0.005 3.30 Newton/step (max 4); Δt 0.0025 2.89 (max 4). Unchanged from
the pre-fix runs (14.0 at the stall, 3.33, 2.91).

## Cost

Allocations on p201136: R-fix build 0.3 node-hours, farm 2.7 node-hours,
foil 0.55 node-hours.
