---

## Kassiotis 2010 — Nonlinear FSI Part II

**Full citation:** Kassiotis, C., Ibrahimbegovic, A., Niekamp, R., Matthies, H. G. Nonlinear fluid-structure interaction problem. Part II: space discretization, implementation aspects, nested parallelization and application examples. Computational Mechanics, 47:335-357, 2011. DOI: 10.1007/s00466-010-0544-7

**BibTeX key suggestion:** kassiotis2010

**Discretisation (fluid):** cell-centred FV

**Discretisation (solid):** FE

**Coupling structure:** partitioned

**Mesh motion treatment:** partitioned outer loop; ALE Laplace smoothing outside fluid pressure-velocity solve

**Nonlinear solver:** fixed-point

**Preconditioner / linearisation:** PISO pressure correction; Aitken relaxation; PBiCG/PCG linear solvers

**Test cases:**
- 3D Newtonian flow in a cylinder for OpenFOAM component performance
- 3D flag in the wind / oscillating appendix
- 3D sloshing wave / dam-break impact on a flexible structure
- Nested parallel CFD and coupled FSI performance studies

**Code released?** not stated

**One-paragraph summary (under 120 words):** This paper describes a CTL component-coupling implementation for nonlinear FSI that reuses FEAP for geometrically nonlinear Lagrangian finite-element solids and OpenFOAM for ALE finite-volume fluid flow, including VOF free-surface treatment. Interface fields are transferred with radial-basis interpolation, and the coupled problem is advanced by explicit or implicit Direct Force-Motion Transfer/Block-Gauss-Seidel fixed-point iterations with Aitken relaxation. The CFD subproblem uses segregated PISO pressure-velocity coupling rather than a monolithic fluid solve. The main contribution is software architecture and nested parallelization for large 3D partitioned FE/FV FSI examples, not a monolithic Newton-Krylov or block-preconditioned formulation.

**Relevance classification:** FV-but-partitioned

**Direct quote(s) supporting the classification:** "finite element code FEAP for structural and finite volume code OpenFOAM for fluid mechanics" (p.1); "large problems from fluid-structure interactionapplications are solved by using existing fluid and structure solvers, along with the corresponding partitioned strategy" (p.2); "The COupling COmponents by a Partitioned Strategy (cops) provides a generic implementation of the explicit and implicit DFMT-BGS algorithms for fluid-structure interaction" (p.8).

**Notes for the authors:** Published online in 2010 but the journal issue is Computational Mechanics 47, 2011. The abstract says the framework can accommodate other schemes, but the implemented FSI examples use partitioned DFMT-BGS coupling, not monolithic Newton/JFNK.

---
