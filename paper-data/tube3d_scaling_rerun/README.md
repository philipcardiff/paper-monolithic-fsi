# 3dTube strong scaling: rerun of 17 Nov 2026 (Section 6.4)

This rerun replaces timing row 6b (MeluXina job 5402592, Oct–Nov 2026) in `paper-data/tube3d_strong_scaling.csv` and `figures/3dTube-strong-scaling.pdf`.

## Why
- **File-system stalls.** In row 6b, the elapsed time was 11–39 % above the CPU time and the repeats spread by up to 34 %. The cause was Lustre I/O during the runs.
- **Meshes.** The row-6b 5 ms restart states of QM L2, RN L2 and RN L3 were computed on the companion paper's tutorial meshes, whose wall arcs are given to 6 digits (`exact_arcs: false`, a wall mismatch of up to about 1 µm). Only QM L3 used the exact-arc meshes (solids4foam#625). The rerun uses the exact-arc meshes for both couplings and all levels, the same meshes as the consistency comparison of Section 6.4.

## Set-up
- **Build:** qm-a421 (solids4foam `a421f063d`, OpenFOAM v2512, Open MPI 5.0.3), as for the other 3dTube results. Only the meshes differ from row 6b: every `system/` and `constant/` dictionary and the 0 fields are identical. This was checked with md5 for the QM and RN L2 cases.
- **Restart states at t = 5 ms (`prep.sh`, job 5466787):**
  - QM L3: the saved 5 ms state of `r5-tube-mono-L3-t6`.
  - QM L2: the `r5-tube-mono-L2-t6` case rerun from 0 to 5 ms.
  - RN L2: `rn-exact/rn-L2` restarted from 4 to 5 ms.
  - RN L3: `rn-exact/rn-L3` rerun from 0 to 5 ms.
  - Each state was reconstructed (`reconstructPar` per region) and is re-decomposed per run.
- **Timing (`timing.sh`):** one exclusive node per series (2× AMD EPYC 7H12, 8 NUMA domains of 16 cores).
  - Windows: 50 steps from t = 5 ms (L2 to 5.625 ms, L3 to 5.3125 ms).
  - Decomposition: slabs (`simple`, 1×1×N) for both couplings.
  - Processes bound to cores 0…N−1 (`--map-by core --bind-to core`; serial runs `taskset -c 0`).
  - One run at a time, three repeats, with the repeat loop outermost.
- **No shared file-system I/O during the runs:** every case is decomposed, run and logged in node-local memory (`/tmp`, tmpfs). Nothing is written during the window (`writeInterval 1000000` time steps). Only the logs are copied to Lustre, between runs.
- **Measures (`analyse.py`):**
  - Window time = ClockTime (elapsed) and ExecutionTime (CPU) differences from the end of step 1 to step 50; the median of the repeats is used (three, five for QM L3).
  - Spread = (max − min)/median of the elapsed window.
  - QM: Newton iterations per step and Krylov iterations per Newton iteration of the monolithic Up system.
  - RN: coupling iterations per step.

## Files
- `prep.sh`, `timing.sh`, `analyse.py`: job and analysis scripts. After the run, `prep.sh` was made to stop on a reconstruction failure, and `analyse.py` now rejects incomplete runs. Neither case occurred.
- `tube3d_scaling_rerun_runs.csv`: every run used.
- `tube3d_scaling_rerun_medians.csv`: medians, which are copied into `../tube3d_strong_scaling.csv`.
- Logs: `Mx:/project/home/p201136/philip-tube-scaling/logs.tar.gz`.

## Compute
18.1 node-hours on p201136. Jobs:
- 5466787: prep.
- 5466788, 5466789, 5466791, 5467088: one per series.
- 5468357, 5468358: two extra QM L3 repeats, see below.
- 5466790: the first RN L3 job, cancelled after a decomposition-dictionary bug (1 min).

## Results (median elapsed window, s; 49 timed steps)

| ranks | QM L2 | RN L2 | QM L3 | RN L3 |
|---:|---:|---:|---:|---:|
| 1 | 827 | 669 | | |
| 2 | 522 | 374 | | |
| 4 | 397 | 295 | | |
| 8 | 310 | 172 | | |
| 16 | 227 | 133 | 4004 | 1241 |
| 32 | 120 | 58 | 1854 | 575 |
| 64 | 80 | 44 | 951 | 268 |
| 128 | | | 617 | 176 |

**Efficiency relative to 16 processes, elapsed (CPU in brackets):**

| ranks | QM L2 | RN L2 | QM L3 | RN L3 |
|---:|---:|---:|---:|---:|
| 32 | 0.95 (0.94) | 1.15 (1.12) | 1.08 (1.06) | 1.08 (1.08) |
| 64 | 0.71 (0.70) | 0.76 (0.74) | 1.05 (1.04) | 1.16 (1.17) |
| 128 | | | 0.81 (0.79) | 0.88 (0.88) |

- **CPU times vs row 6b:** they match row 6b to within 2 % except QM L2 at 2 processes (+3 %) and RN L2 at 2, 16, 4 and 64 processes (+4, +5, +8 and +9 %). Row 6b did not record the RN coupling iterations, so whether the exact-arc mesh changed them is not known.
- **Elapsed vs CPU:** the elapsed medians are 6–12 % above the CPU time, against 11–39 % in row 6b.
- **Repeat spread of the elapsed window:**
  - Below 7 % for QM L2, RN L2 and RN L3; the largest is RN L2 at 64 processes, 44 s at a 1-s clock resolution.
  - The CPU-time spread is below 2 % everywhere.
- **QM L3 timing variation:** QM L3 alone shows a run-to-run variation of 5–19 % in the time rank 0 spends off-CPU, with no file-system I/O.
  - The first job (mel0014) gave 1.05 in repeat 1 and 1.12–1.19 in repeats 2–3.
  - Two extra repeats on fresh nodes (mel0308, mel0374) gave 1.08–1.13.
  - All five repeats are kept and the QM L3 values are medians of five, with an elapsed spread of 8–15 %.
  - The QM L3 efficiencies from the median of five and from the median of repeats 1, 4 and 5 differ by at most 0.01.
- **Iterations:**
  - QM: 2 Newton iterations per step everywhere. Krylov iterations per Newton iteration: 18.0–18.6 (L2), 27.2–27.5 (L3), independent of the process count.
  - RN: 4.0–4.1 coupling iterations per step (L2) and 3.1 (L3); row 6b did not record these.
- **QM/RN cost ratio (elapsed):** L2 1.24 (1 process) to 2.07 (32 processes), and 1.82 at 64. L3 3.2 (16) to 3.5 (128); in CPU time over the same window 3.1 to 3.4.
- **CSV columns:**
  - `speedup_vs_min` and `efficiency` are relative to the smallest process count of each series, from the elapsed window. The row-6b file computed them from the final ExecutionTime.
  - `efficiency_vs16` is relative to 16 processes.
- **Restart time state (checked 20 Nov 2026, solids4foam #740):** the runs on more than one process restarted without `0.005/uniform/time` (`decomposeParMonolithic` and region-by-region `decomposePar` do not copy it, and `timing.sh` deleted `0.005`), so they continued as new runs; the serial runs kept it. From the iteration counts the effect on the timed windows is estimated at about 2% or less, within the repeat spread: the extra Krylov (QM) and coupling (RN) iterations fall in the first steps. A QM L3 check on 64 processes with `uniform/time` copied (MeluXina job 5478008, `/project/home/p201136/philip-tube-scaling/check`) gave 26.75 Krylov iterations per Newton iteration against 27.18, identical after the first 10 steps, and 906 s elapsed (steps 2–50) against 904–1010 s for the three repeats, too close for node-to-node variation to resolve a 2% effect. The remaining offset from the continuous production run (25.4, 64 scotch processes) is the slab partitioning.
