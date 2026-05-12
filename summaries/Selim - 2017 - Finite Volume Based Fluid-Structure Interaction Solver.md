---

## Selim 2017 — Finite Volume FSI Solver

**Full citation:** Selim, M. M., Koomullil, R. P., and McDaniel, D. R. Finite Volume Based Fluid-Structure Interaction Solver. 58th AIAA/ASCE/AHS/ASC Structures, Structural Dynamics, and Materials Conference, AIAA SciTech Forum, AIAA 2017-0868, 2017. DOI: 10.2514/6.2017-0868

**BibTeX key suggestion:** selim2017

**Discretisation (fluid):** cell-centred FV

**Discretisation (solid):** cell-centred FV

**Coupling structure:** partitioned

**Mesh motion treatment:** partitioned outer loop

**Nonlinear solver:** explicit

**Preconditioner / linearisation:** N/A

**Test cases:**
- Flow-induced cantilever beam vibration with inlet speeds 0.25, 0.5, 0.75, and 1.0 m/s
- CPU-time analysis for CSD, CFD, and RBF mesh deformation modules
- Cantilever beam validation against Lorentzon FE/FV FSI results for structural densities 10 and 50 kg/m3

**Code released?** not stated

**One-paragraph summary (under 120 words):** The paper develops a loosely coupled FSI framework using an in-house HYB3D cell-centred finite-volume Euler/Navier-Stokes solver, a new finite-volume linear-elastic structural solver, and RBF mesh deformation. The structural solver discretises Cauchy's law and Hooke's law over control volumes, advances with dual time stepping and Runge-Kutta pseudo-time iterations, and exchanges loads/displacements with the fluid solver on matching interface surface meshes. Mesh deformation uses compact-support RBF interpolation with greedy centre selection and incremental LU updates. Validation is limited to flow-induced cantilever beam vibration, including comparison with a finite-element/finite-volume coupled reference solution.

**Relevance classification:** FV-but-partitioned

**Direct quote(s) supporting the classification:** "In this study a loosely-coupled FSI methodology with all of the above components in a single framework has been developed" (p.1); "The spatial discretization of the governing equations is based on a cell-centered, finite volume upwind scheme" (p.6).

**Notes for the authors:** 

---
