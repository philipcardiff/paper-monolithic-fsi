# Run agent C: timing jobs 4b, 4c, 6b, 6c (prepared, not submitted)

All jobs run on MeluXina exclusive `cpu` nodes (AMD EPYC 7H12, 128 cores),
account p201136. They need the **fixed build** (transpose wall treatment
hard-coded, `viscousStressTranspose` removed) with **solids4foam#616**
(restart fix, still open) merged on top. That build goes in a separate
directory (`/project/home/p201136/philip-agentC/build-fixed-616`), with
`git describe` recorded per run. Pinning is fixed (`taskset` plus MPI
binding to cores). One timing run per node at a time. Each window is
repeated 3 times and the median reported (protocol). Registry rows are
claimed just before submission (claims lapse after 24 h).

Wall-time estimates scale the measured 1x/2x/L1/L2 runs, with assumed
parallel efficiency. They are rough (±50%). One node-hour = 128 core-hours.

## 4b — FSI3 timing windows (cost axis of Fig. 7.1)

- Levels 1x/2x/4x on the tutorial meshes, QM-AMI and IQN-ILS (strict
  test, `couplingReuse 0`, coupling tolerance 1e-5 unless B1 says
  otherwise).
- Ranks 1 / 8 / 32 for both couplings, the IQN-ILS accuracy-run counts.
- Window: 2 `u_y` periods (0.357 s) from a restart at t = 7 s, i.e.
  357 / 714 / 1428 steps.
- Restart states:
  - QM: the t = 7 s fields of the fixed-build 1x rerun, the 4c QM 1e-6 run
    (2x) and the 4a production run (4x). No extra runs.
  - IQN-ILS: xenosim `~/ht_archive/fsi3_work_2026-10/iqnils_mesh_{1x,2x,4x}/7`,
    copied to MeluXina. These are older-code states, but the flow is
    periodic, so the timing is unaffected. A 5-step smoke restart checks
    that the head reads them.

| Level | Ranks | QM window (est.) | IQN-ILS window (est.) |
|---|---:|---:|---:|
| 1x | 1 | 7 min | 6 min |
| 2x | 8 | 6 min | 17 min |
| 4x | 32 | 24 min | 2.1 h |

Per repeat about 3.3 h including set-up; × 3 repeats ≈ **10 node-hours**.

## 4c — FSI3 2x tolerance sweep (Fig. 7.1 inset)

- QM-AMI `snes_rtol` (= `snes_stol`) 1e-4 / 1e-6 / 1e-8; IQN-ILS strict
  1e-4 / 1e-5 / 1e-6.
- Accuracy: six full runs to t = 7 s, 8 ranks each, packed on one
  exclusive node (48 cores). Wall time is set by IQN-ILS 1e-6, about 7 h:
  ≈ **8 node-hours**. QM 1e-6 is also the 4b 2x restart state, and QM
  1e-6 / IQN 1e-5 give the 4b 2x accuracy points.
- Cost: a 2-period window from each run's own t = 7 s state, 8 ranks,
  3 repeats; the 4b 2x windows are reused for the middle tolerances.
  ≈ **3 node-hours**.

## 6b — 3dTube strong scaling (Fig. 8.1)

- L2 at 1, 2, 4, 8, 16, 32 and 64 ranks; L3 at 16, 32, 64 and 128 ranks;
  QM (driver set-up: BDF2, BoomerAMG solid, `directMap`) and RN
  (verification set-up, AMI).
- Window: 50 steps from a restart at t = 5 ms, while the pulse is in the
  tube (A is reached at t ≈ 5.85 ms). 0.625 ms on L2, 0.31 ms on L3.
- Restart states at 5 ms (fixed build; RN from the same build):
  - QM L3: written by the 6a production run. 6a must write at 5 ms; the
    3dTube driver has no `--write-interval`, so the run copy's
    controlDict is edited.
  - QM L2, RN L2, RN L3: prefix runs to 5 ms, packed on one node,
    ≈ **4 node-hours** (RN L3 dominates).
- Decomposition per rank count is done once and reused across repeats.

| Level | Coupling | Sum of windows over the rank counts (est.) |
|---|---|---:|
| L2 | QM | 35 min |
| L2 | RN | 35 min |
| L3 | QM | 25 min |
| L3 | RN | 25 min |

Per repeat about 2 h; × 3 ≈ **6 node-hours**, plus the prefix runs:
≈ **10 node-hours**.

## 6c — 3dTube preconditioner and Jacobian variants (Table 8.2)

L2, 8 ranks, the same 50-step window from the QM L2 5 ms state. Each
variant changes one setting relative to the driver default (Schur full,
lag 8, `ksp_rtol` 1e-3, block-Jacobi ILU(0) velocity block, BoomerAMG
solid block, `snes_mf_operator`):

| # | Variant | Window (est.) |
|---|---|---:|
| 1 | default | 3 min |
| 2 | `schur_fact_type upper` | 3 min |
| 3 | lag 1 (Jacobian and preconditioner every iteration) | 7 min |
| 4 | `ksp_rtol` 1e-4 | 4 min |
| 5 | solid block redundant LU (`--solid-preconditioner lu`) | 15 min |
| 6 | velocity block BoomerAMG | 3 min |
| 7 | assembled Jacobian as operator (no `snes_mf_operator`, `snes_max_it` raised) | 10 min |

Per repeat about 45 min; × 3 ≈ **2.5 node-hours**.

## Total

| Job | Node-hours (est.) |
|---|---:|
| 4b | 10 |
| 4c | 11 |
| 6b | 10 |
| 6c | 2.5 |
| **Timing jobs** | **≈ 34 (≈ 4 300 core-hours)** |
| 4a 4x + 6a L3 production + 1x recheck | ≈ 15 |

## Prerequisites and order

1. The fixed build is announced; build it with #616 on top.
2. 1x recheck on the fixed build (QM-AMI, tutorial 1x), then 4a 4x and 6a
   L3 (6a writing at 5 ms). Then 4c accuracy runs and the 6b prefix runs.
3. Smoke restarts (5 steps) of each restart state on the timing build.
4. Windows: 6c, 6b, 4c, 4b.
