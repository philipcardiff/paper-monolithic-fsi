# 3dTube RN on the exact-arc meshes (L1, L2, L3)

- **Run:** MeluXina job 5404489 (p201136, 1:17 h), build a421f063d. The a421 tutorial with the exact wall arcs (solids4foam#625; `QM_S4F` set, see paper-monolithic-fsi#17). Robin–Neumann `fsiProperties.robin`, backward, 20 ms, L1 on 4 ranks and L2 on 16. Run dirs: `Mx:/project/home/p201287/philip/qm-a421/runs/rn-exact/rn-L{1,2,3}`.
- **L3:** job 5404701 (3:19 h, 64 ranks), 3200 steps, 3.18 coupling iterations per step (max 9). Post-processed with `../l3/qm_post_issue641.py` (solids4foam#641); the unpatched result is kept on Mx as `qm_result.json.post-error`.
- **Data:** `rn_exact_vs_old_and_qm.csv`. "Old" = the companion paper's RN (15a652f09, pre-#625 6-digit arc points, a wall mismatch of up to about 1 µm).

## Effect of the arc change on RN

| QoI | L1 | L2 |
|---|---:|---:|
| displacement and timing QoIs | ≤ 0.13 % | ≤ 0.12 % |
| pressure wave speed c_p | +0.215 % | +0.391 % |

c_p is the only QoI the arc change moves materially, and the shift grows with refinement.

## QM − RN, against old and exact-arc RN

| QoI | L1 (old → exact) | L2 (old → exact) |
|---|---:|---:|
| c_p | +0.29 → +0.075 % | +0.24 → −0.155 % |
| u_r,max | −0.18 → −0.08 % | +0.11 → +0.23 % |
| others | essentially unchanged | essentially unchanged |

## Interpretation
The QM L3 runs use exact arcs; the old RN L3 does not. The c_p shift grows from 0.22 % to 0.39 % between L1 and L2, so a shift of the same order at L3 would account for much of the 0.87 % QM−RN c_p difference there. Confirming this needs RN L3 on the exact-arc meshes: about 5 node-hours (the companion run took 17 512 s on 128 ranks), which is under the run gate.

Not explained: why a geometric change of about 1 µm (2e-4 of the radius) moves c_p by 0.2–0.4 %. The likely route is the arrival-time extraction, which picks threshold crossings of a pulse whose front sharpens with refinement, rather than the physical wave speed. Not checked.

## Level 3 (job 5404701)

| QoI | RN exact − old | QM − RN exact | QM − RN old |
|---|---:|---:|---:|
| displacement and timing QoIs | ≤ 0.12 % | ≤ 0.13 % | ≤ 0.07 % |
| c_w | +0.014 % | −0.009 % | +0.005 % |
| c_p | +0.667 % | +0.201 % | +0.870 % |

- The arc correction accounts for about 77 % of the 0.87 % L3 c_p gap. The L3 hypothesis above is confirmed.
- On matched meshes QM − RN for c_p is +0.08 / −0.16 / +0.20 % (L1–L3): sign-changing, not decreasing, but below the L2→L3 change of either solution (RN −0.60 %, QM −0.25 %). c_p is the least converged QoI for both couplings.
- Displacement and timing QoIs on matched meshes: the largest |QM − RN| falls 1.18 → 0.32 → 0.13 %.
- Still open: why a ~1 µm wall change moves c_p this much.
