# Timing row 6b: 3dTube strong scaling (a421f063d)

- **Runs:** MeluXina jobs 5402592 (61 runs) and 5405642 (the 5 runs lost to the p201287 file-count quota). Each run is a 50-step window restarted from t = 5 ms: L2 to 5.625 ms, L3 to 5.3125 ms. QM and RN; L2 on 1–64 ranks, L3 on 16–128. One run at a time on an exclusive node, ranks pinned to cores 0…N−1, 3 repeats. Slab decomposition (`simple`, 1×1×N; scotch leaves ranks without fluid cells, solids4foam#639). Scripts in `../jobs/timing6b_*`.
- **Measure:** median ExecutionTime of the 3 repeats. All 66 runs reached End with 0 SNES failures. Repeat spread is ≤ 3.8 %.
- **Node:** 2× AMD EPYC 7H12, 8 NUMA domains of 16 cores (lscpu on a compute node, 31 Oct). Ranks 1–16 share one domain's memory channels.

## Median ExecutionTime (s) and parallel efficiency

| ranks | QM L2 | RN L2 | QM L3 | RN L3 |
|---:|---:|---:|---:|---:|
| 1 | 799.3 | 633.0 | | |
| 2 | 479.9 | 340.6 | | |
| 4 | 366.5 | 253.8 | | |
| 8 | 288.8 | 160.6 | | |
| 16 | 220.0 | 119.5 | 3654.6 | 1209.2 |
| 32 | 116.8 | 56.4 | 1721.7 | 560.5 |
| 64 | 79.4 | 39.0 | 879.6 | 260.7 |
| 128 | | | 587.8 | 177.8 |

Efficiency relative to 16 ranks (one full NUMA domain):

| ranks | QM L2 | RN L2 | QM L3 | RN L3 |
|---:|---:|---:|---:|---:|
| 32 | 0.94 | 1.06 | 1.06 | 1.08 |
| 64 | 0.69 | 0.77 | 1.04 | 1.16 |
| 128 | | | 0.78 | 0.85 |

## Findings
- **Within one NUMA domain (1→16 ranks) both couplings scale poorly:** at 16 ranks the efficiency against 1 rank is 0.23 (QM) and 0.33 (RN). Going from 16 to 32 ranks, which adds a second domain, is near-ideal or superlinear for both. Both solvers are memory-bandwidth-bound, so efficiency against 1 rank measures the node, not the solver. The paper should quote efficiency from 16 ranks (one domain) upward.
- **Across domains:** QM L3 holds ≥ 1.04 up to 64 ranks and 0.78 at 128 ranks (about 8k fluid cells per rank). RN L3 gives 1.16 and 0.85. QM L2 falls to 0.69 at 64 ranks (about 2k fluid cells per rank).
- **Krylov iterations per Newton iteration don't depend on the rank count:** L2 18.0–18.6 (1–64 ranks), L3 27.2–27.5 (16–128). The block-Jacobi ILU(0) velocity block and the BoomerAMG solid block don't degrade with partitioning. Newton takes 2 iterations per step throughout.
- **QM/RN cost ratio for these windows:** L2 1.26× (1 rank) to 2.0× (64 ranks); L3 3.0× (16 ranks) to 3.3× (128 ranks). RN is cheaper for this case at these tolerances. QM scales slightly less well, so the ratio grows with the rank count.
- **Not recorded:** RN coupling iterations per step for these windows (`qm_result` has no RN iteration fields). They can be taken from `fsiConvergenceData.dat` if needed.
- **Clock vs ExecutionTime:** ClockTime is 10–40 % higher, most at low rank counts (start-up and I/O). ExecutionTime is used, as for the other timing rows.
