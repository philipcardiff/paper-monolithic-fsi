# 3dTube level 3, quasi-monolithic (a421f063d)

## Run
- MeluXina job 5399576 (p201136), 64 ranks. Case: tutorial with exact wall arcs (#625). Settings as the R5 L1/L2 `t6` consistency runs (snes_rtol 1e-6, BoomerAMG). Δt = 6.25e-6 to t = 0.02. Run dir `Mx:/project/home/p201287/philip/qm-a421/runs/r5/r5-tube-mono-L3-t6`. Build `v2.2-1808-ga421f063d`.
- Completed: 3200 steps, 2 Newton iterations per step (max 2), 25.4 KSP iterations per Newton step (L1 14.0, L2 18.2), 0 SNES failures.
- ExecutionTime 59 663 s (16.6 h); ClockTime 63 551 s.

## Post-processing
- `qm_post.py` stopped at the 3dTube driver's time-spacing check: "has 3200 time levels, expected 3200". The check uses `rel_tol=1e-3`, but times are written with 6 digits, which resolves the L3 spacing only to about 0.8 %. 1600 of the 3199 spacings fail. Filed as solids4foam#641.
- Re-run with `qm_post_issue641.py`, which relaxes only that tolerance to 1e-2. The first, failed result is kept on Mx as `qm_result.json.post-error`. `qm_result_L{1,2,3}.json` here are the a421f063d L1/L2 gate runs and this L3.

## Quasi-monolithic vs Robin–Neumann (`3dtube_qm_vs_rn_L1_L3.csv`)
RN values are from `paper-fsi-verification:main:paper-data/3dtube_level3_mesh_study.csv`. Differences are QM − RN, as % of |RN|:

| QoI | L1 | L2 | L3 |
|---|---:|---:|---:|
| ur_max_A | −0.18 | +0.11 | −0.05 |
| t_ur_max_A | +0.32 | +0.13 | +0.004 |
| uz_min_A | −0.93 | −0.13 | −0.07 |
| t_uz_min_A | +0.76 | +0.09 | +0.02 |
| ur_min_late_A | +1.30 | −0.20 | −0.02 |
| t_arrival_A | +0.09 | +0.07 | +0.004 |
| wave_speed_wall | −0.13 | −0.14 | +0.005 |
| wave_speed_pressure | +0.29 | +0.24 | +0.87 |

- The two couplings converge towards each other under refinement. At L3 every displacement and timing QoI agrees within 0.07 %, well inside the RN uncertainty bands (Fs = 3).
- The QM level-to-level changes have the same character as RN's. ur_max and the wall wave speed are non-monotone, and uz_min and t_arrival converge at low order. The non-asymptotic behaviour is a property of the case and mesh family, not of the coupling.
- **Open:** the pressure wave speed differs by 0.87 % at L3 (QM 4.634, RN 4.594 m/s). This is the only QoI whose difference grows. RN's own value changes by 0.88 % from L2 to L3 ("changes do not decrease"), so the difference is mainly RN's L3 value moving. It may also reflect the interface transfer (QM directMap, RN as in V) or pressure-probe extraction. Not diagnosed.
