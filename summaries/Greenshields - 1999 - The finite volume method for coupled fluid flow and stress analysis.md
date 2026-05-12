---

## Greenshields 1999 — Coupled FV fluid-stress analysis

**Full citation:** Greenshields, C. J., Weller, H. G., and Ivankovic, A. The finite volume method for coupled fluid flow and stress analysis. Computer Modeling and Simulation in Engineering, 4(3):213-218, 1999. DOI: N/A

**BibTeX key suggestion:** greenshields1999

**Discretisation (fluid):** cell-centred FV

**Discretisation (solid):** cell-centred FV

**Coupling structure:** partitioned

**Mesh motion treatment:** partitioned outer loop

**Nonlinear solver:** PISO

**Preconditioner / linearisation:** approximate Jacobian

**Test cases:** water hammer wave propagation in a 200 mm water-filled PVCu pipe; impact test on a 1 m water-filled PVCu pipe; underrelaxation/stability test for a compliant liquid-filled tube

**Code released?** not stated

**One-paragraph summary (under 120 words):** The paper presents a cell-centred finite volume method for coupled transient fluid flow and linear elastic stress analysis, implemented in FOAM. Fluid and solid equations are solved on separate meshes in one code, with fluid tractions transferred to the structure and structural displacement used to move the fluid boundary. The method uses PISO for the compressible liquid equations and segregated iterative linear solvers, with outer fluid-structure iterations to obtain strong coupling within each time step. It is demonstrated on water-filled flexible pipe transients and impact tests, and includes a stability analysis showing when underrelaxation is required for compliant structures.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "The use of a single code enables simple transfer of information" (p.3); "dependent variables and material properties are stored at each cell centroid" (p.4).

**Notes for the authors:** The abstract describes an implicit solution procedure for the whole system, but Section 4 shows a partitioned strong-coupling algorithm with separate fluid and structure solves plus outer iterations. It is highly relevant as early OpenFOAM/FOAM cell-centred FV FSI, but it is not quasi-monolithic, Newton-Krylov, PETSc-based, or block-preconditioned.

---
