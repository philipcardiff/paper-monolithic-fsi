---

## Idelsohn 2009 — strong added-mass FSI

**Full citation:** Idelsohn, S. R., Del Pin, F., Rossi, R., and Oñate, E. Fluid-structure interaction problems with strong added-mass effect. International Journal for Numerical Methods in Engineering, 80:1261-1294, 2009. DOI: 10.1002/nme.2659

**BibTeX key suggestion:** idelsohn2009

**Discretisation (fluid):** FE

**Discretisation (solid):** FE

**Coupling structure:** monolithic pressure-segregated; also extended to partitioned

**Mesh motion treatment:** ALE/Lagrangian framework; remeshing used in examples

**Nonlinear solver:** fixed-point / projection

**Preconditioner / linearisation:** static condensation; approximate Laplace interface matrix; pressure segregation

**Test cases:** 
- incompressible water column over an elastic solid bottom
- mesh sensitivity study for flexible flap in a converging channel
- 3D flexible flap in a converging channel
- flexible valve in pulsatile flow

**Code released?** not stated

**One-paragraph summary (under 120 words):** The paper studies added-mass convergence problems in FSI by starting from a monolithic finite element system and segregating pressure through static condensation of velocity. It interprets Chorin-Temam projection as an approximation to exact velocity condensation, then introduces an approximate Laplace/interface matrix intended to restore convergence for small time steps, soft solids, and similar fluid-solid densities. The same pressure-segregation argument is applied to staggered partitioned FSI, where an interface Laplace contribution is added to the fluid pressure equation. Examples use conforming FE/PFEM-ALE style meshes and include water-column, flexible-flap, and valve cases.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "The monolithic fluid–structure problem is partitioned using a static condensation of the velocity terms." (p.1); "Starting from the monolithical approach the ‘exact’ way to segregate the pressure" (p.3); "The problems were tested with both methods: monolithic with pressure segregation and with a strongly coupled partitioned scheme" (p.23).

**Notes for the authors:** Close algorithmic precedent for using an approximate pressure/interface operator derived from monolithic static condensation to address added-mass effects, but it is FE/PFEM-ALE and projection/fixed-point based rather than cell-centred FV, JFNK, PETSc, or block-preconditioned Newton-Krylov. No abstract/method inconsistency found.

---
