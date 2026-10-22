# B1: preconditioner of the solid block

Code `257b2e564` (`v2.2-1692-g257b2e564`). Set-up:
`campaign/scripts/b1_setup.py`; job: `campaign/jobs/b1.sh`; analysis:
`campaign/scripts/b1_analyse.py` → `b1_windows.csv` (all three cases, one
run of the script); per-run status: `status.txt`; provenance:
`provenance/<run_id>.json` and `provenance/<run_id>.run_meta.json`.

Configurations of the `UpU` solid block: S0 `redundant` + LU (tutorial
default); S1 BoomerAMG with the membraneRoof solid settings (HMIS, ext+i,
P_max 1, truncation 0.3); S2 `bjacobi` + LU per rank; S0tight = S0 with
`snes_rtol` and `snes_stol` 100 times smaller. All other options are the
tutorial's (`ksp_rtol` 1e-4, 3dTube 1e-3; LGMRES; Schur fieldsplit for the fluid;
`snes_rtol` 1e-6, except 3dTube 1e-4).

**Criterion (Philip, 21 Oct): use the cheapest preconditioner per case.**
The QoI difference from S0tight is reported but is not a gate.

QoI difference = largest difference over the window of each monitored
quantity (point displacement components and, for cav and tube, the fluid
force), relative to that quantity's largest magnitude, maximised over the
quantities. The monitors write 6 significant digits; `qoi_output_resolution`
in the CSV is one unit in the last digit of the coarsest quantity, so smaller
differences are not resolved.

## Results

| Case | Config | Ranks | Newton/step | Krylov/Newton | Clock (s) | Memory, all ranks (GB) | QoI diff vs S0tight |
|---|---|---:|---:|---:|---:|---:|---:|
| ring | **S0** | 1 | 2.00 | 23.9 | **39** | – | 9.4e-7 |
| ring | S1 | 1 | 2.00 | 47.4 | 54 | – | 1.7e-5 |
| ring | **S0** | 4 | 2.00 | 24.5 | **17** | – | 1.8e-6 |
| ring | S1 | 4 | 2.00 | 53.4 | 33 | – | 5.5e-5 |
| ring | S2 | 4 | 2.00 | 56.6 | 32 | – | 6.9e-6 |
| cav | **S0** | 1 | 2.00 | 60.1 | **352** | 0.60 | 5.3e-6 |
| cav | S1 | 1 | 2.00 | 69.7 | 386 | 0.60 | 1.1e-5 |
| cav | **S0** | 4 | 2.00 | 59.1 | **99** | 0.93 | 5.3e-6 |
| cav | S1 | 4 | 2.00 | 69.2 | 109 | 0.92 | 5.3e-6 |
| cav | S2 | 4 | 2.00 | 90.5 | 137 | 0.95 | 3.7e-5 |
| cav | **S0** | 16 | 2.00 | 64.0 | **42** | 2.23 | 0 |
| cav | S1 | 16 | 2.00 | 75.4 | 48 | 2.14 | 5.3e-6 |
| cav | S2 | 16 | 2.00 | 108.5 | 59 | 2.18 | 1.2e-4 |
| tube | S0 | 4 | 2.00 | 15.2 | 1 194 | 9.2 | 7.1e-5 |
| tube | **S1** | 4 | 2.00 | 15.0 | **279** | 4.6 | 5.5e-5 |
| tube | S2 | 4 | 2.00 | 15.1 | 337 | 5.3 | 5.5e-5 |
| tube | S0 | 16 | 2.00 | 15.5 | 1 296 | 24.8 | 6.9e-5 |
| tube | **S1** | 16 | 2.00 | 15.2 | **108** | 6.0 | 6.4e-5 |
| tube | S2 | 16 | 2.00 | 15.6 | 132 | 6.5 | 1.0e-4 |

S0tight runs (references, not candidates): ring 2.99–3.00 Newton/step;
cav 2.76–2.90; tube 2.66–2.68. Output resolution: ring 2.6e-6, cav 5.3e-6,
tube 9.8e-6. (Source: `b1_windows.csv`.)

### Set-up per case

- **ringAddedMass** (MeluXina, AMD EPYC 7H12, job 5364389): moderate added
  mass (ρf = 140), mesh factor 2, 50 steps per period, 2 periods (100 steps)
  from t = 0; exclusive node, ranks bound to cores.
- **cavityFlexibleBottom L3** (XenoSim, AMD EPYC 9684X, job 13044): mesh
  factor 4, Δt = 0.5 s, inlet ramp 20 s, `ddt(U) backward`. Spin-up to
  t = 100 s (job 13039, 200 steps, serial); each window runs from t = 0 to
  t = 125 s and is measured over t = 100–125 s (50 steps). Per-region
  `decomposePar`.
- **3dTube L2** (XenoSim, jobs 13045 for 16 ranks, 13046–13049 for 4
  ranks): mesh factor 2, Δt = 1.25e-5 s, `ddt(U) backward`. Spin-up to
  t = 2 ms (job 13029, 160 steps, 16 ranks); each window runs from t = 0 to
  2.625 ms and is measured over the last 50 steps. `decomposeParMonolithic`.
- Windows run from t = 0 because a restart from the spin-up fails
  (`issue_mesh_motion_restart.md`). Newton, Krylov and Clock are taken over
  the last 50 steps only.
- XenoSim: shared node (load ~185 of 192 cores), not exclusive, no core
  binding (Slurm has no cpusets there). Clock times are indicative;
  differences of ≈10% are within what the shared node can produce, factors
  of 4–12 are not.

## Findings

- **ring and cav: S0 is cheapest.** On the ring S1 costs 1.4–1.9 times S0
  (twice the Krylov iterations); on the cavity S1 costs 10–14% more (16–18%
  more Krylov iterations per Newton iteration) and S2 38–40% more. S0 is
  kept for both (tutorial default).
- **3dTube: S1 (BoomerAMG) is cheapest, by a wide margin.** Against S0 it
  is 4.3 times faster at 4 ranks (279 against 1 194 s) and 12 times faster
  at 16 ranks (108 against 1 296 s), and uses half (4 ranks) to a quarter
  (16 ranks) of the memory. S0 does not scale: `redundant` factorises the
  whole solid block on every rank, so its time does not fall from 4 to 16
  ranks and its memory grows with the rank count (9.2 → 24.8 GB). S2 is
  close to S1 (+21–22%). This matches the expectation that hypre pays off
  for 3D meshes that are not small.
- **Krylov iterations per Newton iteration hardly depend on the solid PC
  for 3dTube** (15.0–15.6), unlike the 2D cases, so there the cost
  difference is the cost of setting up and applying the PC.
- **All configurations converge in 2 Newton iterations per step** in every
  case at the tutorial tolerances (S0tight 2.7–3.0).
- **QoI differences (reported, not a gate).**
  - ring: S0 9.4e-7 / 1.8e-6; S1 1.7e-5 / 5.5e-5; S2 6.9e-6. With
    `ksp_rtol 1e-4` the error left after two Newton iterations depends on
    the PC. Section 8 trigger reported on 20 Oct.
  - cav: S0 and S1 within 1–2 units of the output resolution (≤ 1.1e-5);
    S2 3.7e-5 (4 ranks) and 1.2e-4 (16 ranks), above it.
  - tube: S0 itself is 7e-5 from S0tight (the tutorial's `snes_rtol 1e-4`);
    S1 (5.5e-5, 6.4e-5) and S2 (5.5e-5, 1.0e-4) are of the same order. S1
    is as close to the tight reference as the default S0.
- **Rank count** (largest QoI difference between rank counts): cav S0tight
  1 / 4 / 16 ranks identical in the written digits, S0 1 against 16 ranks
  5.3e-6 (one output digit); tube S0tight 4 against 16 ranks 6.1e-6, S0
  6.7e-5, S1 6.1e-5. (Computed with `b1_analyse.histories` and
  `max_rel_diff` over the windows; not in the CSV.)

## Revised acceptance test (HANDOFF Section 10, 21 Oct)

Reference: S0ref and S1ref = S0 and S1 at `snes_rtol`/`snes_stol` 1e-10,
`ksp_rtol` 1e-8 (`ksp_max_it` 10000), same windows. XenoSim jobs 13051
(cav, both on 4 ranks), 13052 (tube S1ref, 16 ranks), 13053 (tube S0ref,
4 ranks); all rc 0, every step converged (`CONVERGED_FNORM_RELATIVE`).
Per-quantity differences: `b1_qoi_vs_ref.csv`; maxima:
`qoi_maxreldiff_vs_ref` in `b1_windows.csv`.

- **The reference is preconditioner-independent:** S1ref against S0ref is
  0 in the written digits for every quantity of both cases.
- Cost at the reference tolerances (window): cav S0ref 231 s, S1ref 237 s
  (4 ranks; 2.74 Newton/step, 115 and 128 Krylov/Newton); tube S0ref
  1 573 s (4 ranks), S1ref 227 s (16 ranks).

Thresholds: 5% of the change between the two finest meshes in the
verification READMEs. cav (monolithic L3 → L4): Uy 0.70% → 3.5e-4, Fy
0.057% → 2.9e-5. 3dTube (Robin–Neumann L1 → L2, the only levels
recorded): u_r,max(A) 0.05% → 2.5e-5, u_z,min(A) 1.85% → 9.3e-4.

| Case | Quantity | S0 | S1 | S2 | Threshold |
|---|---|---:|---:|---:|---:|
| cav | Uy at the monitor point | 0 | 0 | 0 | 3.5e-4 |
| cav | Fy | 0 | ≤ 1.9e-7 | 1.9e-7 | 2.9e-5 |
| tube | u_r at A | 4.6e-6 | 4.6e-6 | 4.6e-6 | 2.5e-5 |
| tube | u_z at A | 4.5e-6 | 4.5e-6 | 4.5e-6 | 9.3e-4 |

(Largest over rank counts; tutorial tolerances. Source:
`b1_qoi_vs_ref.csv`.)

- **cav: every configuration passes**, by two orders of magnitude or more.
  The tutorial tolerances (`snes_rtol` 1e-6) are sufficient. (The 5.3e-6
  in `qoi_maxreldiff_vs_ref` is the x component of the monitor point, not
  a paper QoI.)
- **tube: every configuration passes at point A**, at the tutorial
  tolerances (`snes_rtol` 1e-4, `ksp_rtol` 1e-3).
- The radial displacement at the wall points z = 0.40 and 0.45 m differs
  by up to 6.5e-5 (S1) and 1.0e-4 (S2) relative to its own maximum, above
  2.5e-5. The pulse has not reached them in the window (their maximum is
  ≤ 1.1e-7 m, against 1.5e-4 m at z = 0.05 m), so the relative difference
  is of a precursor of ~1e-7 m. Relative to the u_r peak (1.57e-4 m), every
  wall difference is below 1e-5. Not a failure in my reading; reported.
- **Limitation:** the 3dTube window (t = 2.0–2.625 ms) ends before the u_r
  peak (7.2 ms); the test of `snes_rtol` 1e-4 on the peak itself needs a
  full-run tight reference, which belongs in R5 (tolerance calibration).
  The cavity window is at the steady state, so its test is final for L3.
- **Solid PC at equal accuracy:** unchanged. All configurations meet the
  rule, so the cheapest is chosen: S0 for cav, S1 for 3dTube.

## Recommendation (frozen solid-block options for R)

| Case | Solid block |
|---|---|
| ringAddedMass, cavityFlexibleBottom and the other 2D cases | S0 (`redundant` + LU), unchanged |
| 3dTube (and other 3D cases that are not small) | S1 (BoomerAMG, membraneRoof settings) |

## Deviations

- 3dTube at 32 ranks not run (XenoSim had ~20 free cores; MeluXina out of
  hours). The 4 → 16 rank trend is already decisive.
- 3dTube spin-up on 16 ranks rather than serial.
- cav and tube on XenoSim (shared, unbound) instead of MeluXina exclusive
  nodes; ring on MeluXina. Costs are compared only within a case.
- One run per configuration; no timing repeats.
- The ring rows have no `ddt_U` entry in the CSV (its `b1_window.json`
  does not record it); its fluid `fvSchemes` has `ddt(U) backward`.
