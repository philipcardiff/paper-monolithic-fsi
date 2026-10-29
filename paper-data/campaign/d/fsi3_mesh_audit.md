# FSI3 fluid-mesh audit: neighbour cell-size ratios (item 3 of the handover)

Meshes only, no runs. solids4foam `a421f063d`, `tutorials/fluidSolidInteraction/TurekHron2006`.
Each level is the driver's refinement (in-plane block divisions × 1, 2, 4) of
`system/fluid/blockMeshDict` (tutorial family: QM-AMI and IQN-ILS, option b)
and `system/fluid/blockMeshDict.monolithic` (conformal family: R4).
Metric: the volume ratio V_P/V_N of the two cells of each internal face.
In these 2-D quad meshes this equals the jump in cell thickness normal to the face.
It reproduces the verification paper's 1.43 for the standard family.
Wake band: 0.6 < x < 2.5, 0.1 < y < 0.3.
Scripts: `scripts/audit_run.sh`, `audit_ratio.py`, `audit_where.py`; raw output in `audit/`.

| Family | Level | Fluid cells | Max V ratio | Where | Max in wake | Faces > 2 |
|---|---|---:|---:|---|---:|---:|
| tutorial | 1x | 5,336 | 1.43 | x = 0.24, y = 0.24 (around the cylinder) | 1.32 (x = 1.0) | 0 |
| tutorial | 2x | 21,344 | 1.43 | same | 1.33 (x = 1.0) | 0 |
| tutorial | 4x | 85,376 | 1.43 | same | 1.34 (x = 1.0) | 0 |
| conformal | 1x | 1,859 | 3.50 | lines y = 0.19 and 0.21, x = 0.6–2.3 | 3.50 | 70 + 27 |
| conformal | 2x | 7,436 | 3.50 | same | 3.50 | – |
| conformal | 4x | 29,744 | 3.50 | lines y = 0.189 and 0.211, x = 0.60–2.45 | 3.50 | 280 + 108 |

Conformal family, all levels (`audit/conformal-*.lines.txt`):
- **3.5:1** across the two horizontal block lines at the flag's upper and lower faces (y = 0.19 and 0.21).
  They run downstream from the flag root (x = 0.6) to x ≈ 2.45, through the whole wake.
  The flag-thickness band of cells is continued downstream to keep the flag interface conformal.
- **2.3–2.4:1** across the vertical block line x ≈ 1.0, over the full channel height.
- **1.5–1.9:1** around the cylinder ring and along y ≈ 0.28.
- The jumps do not shrink with refinement; the number of such faces doubles per level.

Reading:
- The tutorial family (option b) is smooth (≤ 1.43, the verification paper's "standard family").
  The §7 comparison of QM-AMI with IQN-ILS and Featflow is on this family.
- The conformal family has larger level-independent jumps (3.5:1) than the ring+box family (2–2.8:1).
  These lie in the wake, which the verification paper found was not asymptotic at 8x′.
  The R4 conformal 1x/2x/4x series should not be used for observed orders or extrapolation.
  It still serves as a same-mesh QM vs IQN-ILS comparison.

Decision (Philip, 29 Oct): R4 stays in §7 only as a same-mesh QM vs IQN-ILS comparison, with this caveat; accuracy and orders come from option (b).
