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

| level | QM (s) | Aitken (s) | QM/Aitken |
|---:|---:|---:|---:|
| L1 | 137.3 | 34.8 | 3.9 |
| L2 | 593.1 | 181.3 | 3.3 |
| L3 | 3423 | 1209 | 2.8 |
| L4 (4 ranks) | 13166 | 5060 | 2.6 |

- On this weakly coupled steady case QM costs 2.6–3.9× Aitken. The gap narrows with refinement.
