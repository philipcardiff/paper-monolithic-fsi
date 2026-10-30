# Timing rows ringAddedMass and cavityFlexibleBottom (a421f063d)

- **Job:** MeluXina 5400191 (p201136), one exclusive node.
- **Script:** `../jobs/ma_timing_a421.sh` (agent A's protocol, with `BUILD=qm-a421`). Up to 8 runs at a time, one per NUMA domain. Serial, except cavity L4, which uses 4 ranks.
- **Repeats:** 3 per configuration; all 51 runs reached End.
- **Measure:** median solver ExecutionTime. The repeat spread (max/min − 1) is at most 1.6 %. The ClockTime medians are in `timing_ma_medians.csv`; the per-run times are in `timing_ma_runs.csv`.
- **Run dirs:** `Mx:/project/home/p201287/philip/qm-a421/runs/timing-ma/runs/`.

## ringAddedMass, strong regime, mesh 2, standard solid

| steps/period | QM (s) | IQN-ILS (s) | RN (s) | QM/IQN-ILS | QM/RN |
|---:|---:|---:|---:|---:|---:|
| 25 | 31.6 | 55.0 | 402.7 | 0.57 | 0.08 |
| 50 | 60.0 | 121.1 | 499.4 | 0.50 | 0.12 |
| 100 | 114.5 | 223.7 | 315.3 | 0.51 | 0.36 |

- QM is about 2× faster than IQN-ILS at every Δt.
- RN becomes slower as Δt grows (25 steps per period takes longer than 100), because it needs more coupling iterations per step at large Δt in the strong regime.

## cavityFlexibleBottom (steady)

**Correction (30 Oct).** The two couplings do not run the same simulated time:
- QM uses the tutorial Δt = 0.5 s on every level, to 300 s (600 steps).
- Aitken uses the tutorial's Δt = 0.5 / 0.25 / 0.125 / 0.0625 s on L1–L4, to 200 s (400 to 3200 steps).

The whole-run ratio first reported here (QM 3.9 / 3.3 / 2.8 / 2.6× Aitken) therefore did not compare equal work. The fair measure is the cost to reach steady state: the first time after which u_y(A) stays within 1e-4 of its final value, taken from each run's history. The cost to that point is estimated pro rata from the run's ExecutionTime. Aitken's early steps need more coupling iterations than its late ones (4.2–5.0 mean against 2.1–2.8 over the last 10), so the pro-rata estimate slightly *under*-states Aitken's cost.

| level | QM steps / t to steady | QM cost (s) | Aitken steps / t to steady | Aitken cost (s) | QM/Aitken |
|---:|---:|---:|---:|---:|---:|
| L1 | 334 / 167 s | 76 | 309 / 154.5 s | 27 | 2.8 |
| L2 | 336 / 168 s | 332 | 623 / 155.75 s | 141 | 2.4 |
| L3 | 336 / 168 s | 1917 | 1381 / 172.6 s | 1043 | 1.8 |
| L4 (4 ranks) | 336 / 168 s | 7373 | 2784 / 174.0 s | 4402 | 1.7 |

- Whole-run ExecutionTime medians: QM 137.3 / 593.1 / 3423 / 13166 s; Aitken 34.8 / 181.3 / 1209 / 5060 s.
- Newton iterations per step: 1.64–1.67. Krylov iterations per Newton iteration: 24.6 / 29.9 / 45.3 / 89.7.
- Aitken coupling iterations per step: 4.6 / 5.0 / 4.6 / 4.2.
- Steady u_y(A), QM − Aitken: −0.47 / −0.18 / −0.085 / −0.055 % (|QM| smaller).
- Steady F_y, QM − Aitken: −0.59 / −0.24 / −0.12 / −0.078 %.
- QM costs 1.7–2.8× Aitken to reach steady state; the gap narrows with refinement, because Aitken has to reduce Δt with the mesh.
