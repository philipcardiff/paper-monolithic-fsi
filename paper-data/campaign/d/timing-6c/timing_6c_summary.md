# Timing row 6c: 3dTube L2 quasi-monolithic solver options (a421f063d)

- **Job:** MeluXina 5400422 (p201136), script `../jobs/timing6c_job_6c.sh`.
- **Runs:** 16 ranks on one exclusive node, one run at a time. Each is a 50-step window restarted from t = 5 ms (to 5.625 ms), repeated 3 times.
- **Measure:** median ExecutionTime. The repeats agree within 0.3 %, and every run reached End with 0 SNES failures.
- **Iteration counts:** Newton iterations per step and KSP iterations per Newton step are from repeat 1. They are deterministic across repeats.

| variant | time (s) | / base | Newton/step | KSP/Newton |
|---|---:|---:|---:|---:|
| base | 229.3 | 1.00 | 2.0 | 18.3 |
| vel-amg | 234.8 | 1.02 | 2.0 | 18.3 |
| ksp1e-3 | 261.6 | 1.14 | 2.7 | 15.8 |
| schur-upper | 283.0 | 1.23 | 2.0 | 25.2 |
| lag1 | 286.5 | 1.25 | 2.0 | 18.3 |
| assembled | 297.8 | 1.30 | 8.0 | 16.6 |
| solid-S0 | 1891.9 | 8.25 | 2.0 | 18.6 |

- The default settings are the fastest.
- **ksp1e-3:** a looser linear tolerance needs more Newton iterations (2.7 vs 2.0), so it costs more overall.
- **assembled:** needs 8 Newton iterations per step instead of 2, yet costs only 30 % more.
- **solid-S0:** the iteration counts are the same as base, so its 8× cost comes from the solid-block solve itself.

**Provenance note (30 Oct).** These windows restart from `p5-tube-mono-L2`. That run was set up from the 18a24427f tutorial files, with the 6-digit arc points from before solids4foam#625, not from the a421 tutorial (paper-monolithic-fsi#17). The wall geometry differs by at most about 1 µm and the solver settings are identical, so the timings stand. The same applies to 6b, except QM L3, which restarts from the exact-arc run.
