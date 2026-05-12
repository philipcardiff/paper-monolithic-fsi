---

## Yvin 2018 — Added mass evaluation via FV solver for FSI co-simulation

**Full citation:** Yvin, C., Leroyer, A., Visonneau, M., Queutey, P. Added mass evaluation with a finite-volume solver for applications in fluid–structure interaction problems solved with co-simulation. Journal of Fluids and Structures, 81:528–546, 2018. DOI: 10.1016/j.jfluidstructs.2018.05.008

**BibTeX key suggestion:** yvin2018

**Discretisation (fluid):** cell-centred FV

**Discretisation (solid):** N/A (rigid body multibody dynamics; no deformable solid discretisation)

**Coupling structure:** partitioned

**Mesh motion treatment:** partitioned outer loop (ALE mesh deformation handled within the fluid solver ISIS-CFD; rigid body motion via MBDyn; interface position exchanged at coupling iterations)

**Nonlinear solver:** fixed-point (Block Gauss–Seidel with Internal Fluid Coupling, BGS-IFC; one linearised Picard iteration of the fluid operator per coupling iteration)

**Preconditioner / linearisation:** N/A (partitioned co-simulation; relaxation via artificial added mass operator serves as the stabilisation/relaxation mechanism)

**Test cases:**
- Cylinder in a pipe: analytical validation of the added mass in translation (convergence with mesh refinement)
- Cargo Series 60 ship hull: added mass matrix computed and compared against the frequency-domain potential flow code Aqua+
- Parallelepiped (Application 1): single density ratio d = 0.1, six-DOF free motion with strong anisotropic added-mass effects; convergence study over multiple time steps
- Parallelepiped (Application 2): multiple density ratios (d = 0.1–0.7), off-centre gravity, coupled heave–pitch and sway–yaw motions; influence of full vs. diagonal relaxation operator studied

**Code released?** ISIS-CFD is part of the commercial FINE/Marine suite (Cadence/NUMECA). MBDyn is open source (GNU GPL, Politecnico di Milano). No URL stated for the coupled framework.

**One-paragraph summary (under 120 words):** This paper develops and validates a method to evaluate the added mass matrix directly within a cell-centred finite-volume RANS solver (ISIS-CFD) by solving an auxiliary impulsive pressure equation on the same mesh used for the FSI problem. The computed matrix is used to construct a physical relaxation operator that stabilises the partitioned BGS-IFC co-simulation algorithm between ISIS-CFD and the rigid-body solver MBDyn. The approach avoids modifying the structural solver, handles free-surface and confinement effects naturally, and requires fewer than 1% extra CPU cost. Validation against analytical solutions and a potential flow code is provided, followed by six-DOF free-motion simulations of buoyant parallelepipeds with extreme added-mass effects.

**Relevance classification:** added-mass / FSI stability theory

**Direct quote(s) supporting the classification:** N/A

**Notes for the authors:** The paper is relevant as background on the added-mass instability that motivates implicit/monolithic coupling. The BGS-IFC algorithm (one linearised Picard fluid iteration per coupling step) is distinct from the JFNK approach but is a noteworthy partitioned alternative that also avoids full fluid resolves at each coupling iteration. The FV added-mass pressure equation (Eq. 20) is solved with the same cell-centred discretisation as the main flow, which may be of interest when discussing how partitioned methods handle added-mass stabilisation compared to the monolithic block-preconditioned approach.

---
