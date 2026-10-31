# cavityFlexibleBottom QM with interpolate(U) linear, L2-L4 (a421f063d)

- **Runs:** MeluXina jobs 5406163 (L2, L3) and 5406302 (L4, 8 ranks). The L4 run in 5406163 failed at start-up because the job script didn't set Open MPI oversubscription with `--ntasks=1`; that was a set-up error in the script, not a solver problem.
- **Definition:** the R-fix definitions of `tab:cavity_m` (`ma_run.py` `definitionsRfix`, tutorial schemes), with only `interpolate(U)` changed from `skewCorrected linear` to `linear`. Wrapper `cav_linear.py`, job `job_cav_linear.sh`.
- **Data:** `cavity_interp_vs_aitken.csv`. The Aitken and skewCorrected values are those of `tab:cavity_m`.

| level | QM−Aitken u_y, skewCorrected | QM−Aitken u_y, linear | F_y, skewCorrected | F_y, linear |
|---:|---:|---:|---:|---:|
| 2 | +0.178 % | +0.066 % | +0.240 % | +0.092 % |
| 3 | +0.085 % | +0.0004 % | +0.119 % | +0.0034 % |
| 4 | +0.055 % | −0.0067 % | +0.078 % | −0.0068 % |

- **L2 and L3 reproduce the 1252bd2e5 values:** +0.065 % and below 0.001 %.
- **With linear interpolation, the difference changes sign between L3 and L4** and is below 0.01 % in both u_y and F_y from L3 on. That is 8× smaller than with skewCorrected at L4.
- **The skewCorrected continuity-flux interpolation is the source of the slowly decreasing difference.** Without it the remaining difference is at the level of the other O(h²) items.
- **QM-linear u_y converges at second order:** changes of 7.10e-3 and 1.73e-3, ratio 4.10 (Aitken 4.05). Newton takes 1.65 iterations per step on every level, and KSP per Newton is 30 / 45 / 91 (L2 / L3 / L4 on 8 ranks).
