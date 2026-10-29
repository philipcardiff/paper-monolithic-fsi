# Job d1 findings (Mx 5398193, p201136, COMPLETED 4:33 h, build a421f063d)

## blobInTreacle QM x4, current mesh motion: steadiness

Point displacement (`solidPointDisplacement_pointDisp.dat`) and the maximum |meshPhi| over the fluid cells at each write time.

| t (s) | Dx (m) | Dy (m) | max abs(meshPhi) |
|---:|---:|---:|---:|
| 1.5 | 0.09954061 | -0.013643404 | 1.08e-3 |
| 3.0 | 0.11999105 | -0.014096352 | 1.31e-6 |
| 4.5 | 0.11999355 | -0.014088211 | 1.65e-8 |
| 6.0 | 0.11999356 | -0.014088194 | 4.22e-11 |

The solution is steady: Dx changes by 1e-8 m between t = 4.5 and 6, and the mesh flux decays to round-off.
The 'new' mesh motion set-up (`mm_switch.py "(interface)"`) aborted at t = 2.11 on a line-search trial step that inverted the mesh (solids4foam#635); it gives no result.

## FSI3 QM-AMI (tutorial meshes) 1x/2x/4x

Space and time are refined together (dt 1e-3, 5e-4, 2.5e-4 s).
1x and 4x: `evidence/m-runs-c` `paper-data/campaign/c/fix/mfix-fsi3-{1x,4x}.sweep.csv`, build 1252bd2e5 (#618).
2x: this job, build a421f063d (`monolithicAMI_mesh_sweep.csv`).
Observed order p = log2(ratio of successive differences); extrapolated value = Richardson with the observed p.

| Quantity | 1x | 2x | 4x | ratio | p | extrapolated | Turek-Hron history |
|---|---:|---:|---:|---:|---:|---:|---:|
| uy amplitude (mm) | 28.474 | 32.798 | 34.460 | 2.60 | 1.38 | 35.50 | 34.916 |
| ux mean (mm) | -2.0886 | -2.5777 | -2.8001 | 2.20 | 1.14 | -2.986 | -2.865 |
| uy frequency (Hz) | 5.5997 | 5.5420 | 5.5002 | 1.38 | 0.47 | (5.39) | 5.473 |
| drag mean (N/m) | 453.64 | 458.95 | 460.47 | 3.49 | 1.80 | 461.08 | 460.29 |
| drag amplitude (N/m) | 21.67 | 24.84 | 27.07 | 1.42 | 0.51 | (32.3) | 27.43 |
| lift amplitude (N/m) | 219.04 | 168.97 | 159.04 | 5.05 | 2.34 | 156.59 | 153.44 |

Bracketed extrapolations are not meaningful: p < 1 means these three levels are not in the asymptotic range for that quantity.
Caveats: the levels come from two builds (1252bd2e5 and a421f063d); 3dTube L1 on two builds with #618 agreed to about 0.5%, so the build mix is small next to the 1x-2x differences but not zero.
The tutorial mesh family has volume ratios up to 1.43 (`../fsi3_mesh_audit.md`), so it is usable for observed orders, unlike the conformal family.
