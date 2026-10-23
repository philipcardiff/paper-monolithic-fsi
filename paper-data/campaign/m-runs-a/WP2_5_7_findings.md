# WP2, WP5, WP7 findings (agent A): cavity 2a–2c, blob 5b, foilInWind 7a

MeluXina, account p201136, solids4foam `85b0c1de6`, OpenFOAM v2512, as in
`WP1_findings.md`. No solver code changes. Rows in `runs.csv`, `qois.csv`.

## 2a cavityFlexibleBottom QM L1–L4

Set-up as the #597 rerun: Δt 0.5 s to 300 s, inlet ramp 20 s, `ddt(U)`
Euler (steady; the partitioned file is Euler too), `div(phi,U) Gauss
linearUpwind grad(U)`, `interpolate(U) skewCorrected linear` (tutorial),
vST no, tutorial tolerances; L1–L3 serial, L4 on 4 ranks (fluid
mesh-motion block `redundant` LU in parallel, as #597).

| Level | u_y (m) | #597 QM | Partitioned strict | QM − part. | Newton/step (max) | t_steady 1e-3 / 1e-4 (s) | Newton to steady (1e-3) | Wall (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| L1 | −0.201546 | −0.201546 | −0.202499 | +0.47% | 1.675 (3) | 138 / 166 | 612 | 168 |
| L2 | −0.228468 | −0.228468 | −0.228830 | +0.16% | 1.648 (3) | 124 / 167.5 | 547 | 620 |
| L3 | −0.235448 | −0.235448 | −0.235636 | +0.08% | 1.647 (3) | 124 / 167.5 | 545 | 3 175 |
| L4 | −0.237187 | −0.237187 | −0.237307 | +0.05% | 1.657 (3) | 124 / 167.5 | 548 | 8 590 (4 ranks) |

- The head reproduces the #597 (E597, Euler) values to all six digits,
  as expected for a steady state (`ddt` and the limiter word change
  nothing).
- Newton iterations per step and to steady state do not depend on the
  level (1.65, about 550 to 1e-3). Krylov iterations per Newton
  iteration grow: 24, 29, 42, 81.
- t_steady is the last time at which u_y differs from its final value by
  more than 1e-3 (1e-4) of it. With the 20 s ramp it is 124 s on L2–L4.
  The partitioned runs have no ramp and level-dependent Δt, so their time
  to steady is not directly comparable (decision 3a.3: the Δt reduction is
  the point of the cost comparison).

## 2b `interpolate(U) linear` (L2, L3)

| Level | u_y skewCorrected | u_y linear | Partitioned | QM − part. (skewCorr. → linear) |
|---|---:|---:|---:|---|
| L2 | −0.228468 | −0.228718 | −0.228830 | +0.16% → +0.049% |
| L3 | −0.235448 | −0.235647 | −0.235636 | +0.08% → −0.005% |

The face interpolation of U in the QM continuity flux accounts for most
of the QM–partitioned difference: with plain linear interpolation (as the
partitioned set-up effectively uses) the difference falls by a factor of 3
at L2 and 16 at L3. Newton counts are unchanged (1.648, 1.643).

## 2c `checkMesh` on the final states

`2c/checkMesh_summary.csv`. Every QM fluid and solid mesh passes, at t = 0
and at t = 300 s. Fluid max skewness 0.430/0.488/0.518/0.534 (L1–L4)
undeformed and the same to 0.1% deformed; max non-orthogonality 42.8 →
44.4° (L1) up to 54.5 → 54.3° (L4); the solid stays orthogonal. The
skewness is a property of the fluid mesh, not of the deformation.
Partitioned (Philip, 23 Oct: rerun): Aitken strict L1–L4 at the head, at
the recorded Δt 0.5/0.25/0.125/0.0625 s to 200 s (nOuterCorr 20, L4 40 with
fluid solvers 1e-8 on 4 ranks; job 5379411). u_y reproduces the
`partitioned_strict` rows to within 0.005% (−0.202499, −0.228841,
−0.235635, −0.237312). Every mesh passes; fluid max skewness 0.430→0.431,
0.488→0.491, 0.518→0.521, 0.534→0.535 (undeformed → final), the same as QM;
max non-orthogonality grows a little more than with the QM mesh motion
(L2 49.0→51.8°, L3 52.7→55.2°, L4 54.5→55.3°; QM 50.1°, 53.0°, 54.3°).

## 5b blobInTreacle QM time-step study (x1, t = 1 s)

vST no, `backward`, tight PETSc tolerances (1e-8/1e-8/1e-6).

| Δt (s) | u_x (m) | Change | Order u_x | Order interface | Newton/step | Partitioned u_x (README) |
|---:|---:|---:|---:|---:|---:|---:|
| 0.25 | 0.0556660 | – | – | – | 3.00 | 0.0558737 |
| 0.125 | 0.0564501 | 7.84e-4 | – | – | 2.75 | 0.0564184 |
| 0.0625 | 0.0565956 | 1.46e-4 | 2.43 | 3.67 | 2.00 | 0.0565219 |
| 0.03125 | 0.0566088 | 1.32e-5 | 3.46 | 2.72 | 2.00 | 0.0565398 |

The tutorial check (orders of the two coarsest pairs in 1.6–3.0) passes
for u_x (2.43), but the interface order is 3.67 for the first pair, above
the band; the finest change is 2.3e-4 of u_x (criterion 1e-3). At
Δt 0.03125 s QM is 0.12% above the partitioned u_x, the same order as the
steady x1 QM–partitioned difference in WP0. Interface vertex positions
are stored in the run results.

## 7a foilInWind to t = 0.2 s

Data in `7a/`: Newton histories (`newton_*.csv`, every SNES iterate),
IQN-ILS residuals, displacement and force monitors.

| Run | Ranks | Outcome | Newton or coupling iter./step |
|---|---:|---|---|
| QM Δt 0.0025 (R0 `r0-foil-backward-e`) | 128 | to 0.2 s (later fails at 0.95 s, R0 issue) | 2.91 (max 4) to 0.2 s |
| QM Δt 0.005 | 128 | to 0.2 s | 3.33 (max 5) |
| QM Δt 0.01 | 128 | stalls at t = 0.05 s | 4, 4, 4, 7, then 50 (DIVERGED_MAX_IT) |
| IQN-ILS Δt 0.01, strict | 8 | fails at t = 0.08 s | 4, 5, 5, 6, 8, 10, 18, then 50 unconverged |

- QM Δt 0.01 stall: the residual falls from 646 to about 150 in 15
  iterations and then stays there (148.4 at iteration 50, line search
  `bt`), as reported in #602. The steps before it already need more
  iterations (7 at t = 0.04 s).
- IQN-ILS Δt 0.01 with the strict test does not reach the end time either.
  Its coupling iterations grow every step until, at t = 0.08 s, the
  residual stagnates at 2.5e-5 against the 1e-5 tolerance. On 128 ranks it
  failed earlier, in the first step's partitioned solid solve (10 000
  Krylov iterations; 4 608 solid cells), so the run uses 8 ranks. The
  README's IQN-ILS Δt 0.01 run (13 min, pre-BDF2, legacy test) is
  therefore not reproduced at the head with the strict test. Stopped and
  reported; not retried with other tolerances or nOuterCorr.
- **Smaller Δt (Philip, 23 Oct).** IQN-ILS strict, 8 ranks, to 0.2 s:
  Δt 0.005 s 5.35 coupling iterations per step (max 7), 385 s; Δt 0.0025 s
  4.65 (max 6). Both complete. For comparison QM: Δt 0.005 s 3.33 Newton
  (max 5), Δt 0.0025 s 2.91 (max 4). Data in `7a/` (`fsiResiduals_iqn_*`,
  monitors).
- The monitored displacements are about 1e-9–1e-8 m in this window and
  depend strongly on Δt (start-up transient), so no accuracy comparison is
  drawn from them.

## Cost

Whole-node allocations on p201136: batch-2 farm 2.4 node-hours, foilInWind
jobs 0.5, checkMesh 0.01. Solver core-hours: cavity 2a/2b 11.6 (of which
L4 9.5 on 4 ranks), 5b 0.02; 7a 0.4 node-hours of exclusive 128-rank time.
