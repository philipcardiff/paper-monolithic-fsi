# Cavity with a flexible bottom: quasi-monolithic runs with linear continuity-flux interpolation

Table `tab:cavity_m` (Section 4.5.2) compares the quasi-monolithic coupling, with `interpolate(U) linear` (the
pressure-correction solver's interpolation), against Aitken on levels 1-4.

- **Runs:** MeluXina job 5466793 (account p201287), one exclusive node, build a421f063d (`qm-a421`). The case
  definitions are those of the timing job 5400191 (`tm-cav-qm-L*`, evidence/m-runs-d timing-ma), with only
  `interpolate(U)` changed to `linear`. Three repeats per level, at most 8 runs at once, each masked to its own
  8-core CCD; level 4 on 4 ranks. Script: `job_cavlin.sh`; post-processing: `post.py`.
- **Run directories:** `/project/home/p201136/philip-ma/cavlin/runs.tar` (`tl-cav-qmlin-L{1..4}-r{1..3}`, processor directories not kept).
- **Data:** `qm_linear_runs.csv` (one row per run). The final u_y(A) and F_y agree with the earlier untimed linear
  runs on L2-L4 (jobs 5406163, 5406302) to all printed digits.
- **Cost to steady state:** the first time after which u_y(A) stays within 1e-4 (relative) of its final value,
  times the median ClockTime of the three repeats, pro rata over the steps (as for Aitken, timing_ma_summary.md):
  QM 77.7 / 330 / 1834 / 7133 s; Aitken 27.0 / 144.9 / 1062 / 4459 s; ratio 2.9 / 2.3 / 1.7 / 1.6. Measured
  directly from the logs, the QM time to steady state is 101 / 423 / 2329 / 9489 s (the early steps cost more),
  so the pro-rata estimate understates the cost of both couplings.
