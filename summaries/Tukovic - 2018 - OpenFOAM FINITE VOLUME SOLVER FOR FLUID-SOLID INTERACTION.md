---

## Tukovic 2018 — OpenFOAM FV FSI solver

**Full citation:** Tukovic, Z., Karac, A., Cardiff, P., Jasak, H., Ivankovic, A. OpenFOAM finite volume solver for fluid-solid interaction. Transactions of FAMENA, XLII(3):1-31, 2018. DOI: 10.21278/TOF.42301

**BibTeX key suggestion:** tukovic2018

**Discretisation (fluid):** cell-centred FV

**Discretisation (solid):** cell-centred FV

**Coupling structure:** partitioned

**Mesh motion treatment:** partitioned outer loop

**Nonlinear solver:** fixed-point / quasi-Newton

**Preconditioner / linearisation:** Rhie-Chow stabilisation; segregated explicit nonlinear solid terms; preconditioned conjugate gradient

**Test cases:** 
- Plate with a hole stress-analysis verification
- Channel flow over a cavity with a flexible bottom
- Turek-Hron elastic plate behind a rigid cylinder, FSI2 and FSI3
- Wave propagation in an elastic tube
- 3D channel flow over an elastic thick plate

**Code released?** OpenFOAM; URL not stated

**One-paragraph summary (under 120 words):** This paper presents a parallel OpenFOAM FSI solver using second-order cell-centred finite volume discretisations for both incompressible ALE flow and total-Lagrangian St. Venant-Kirchhoff solid mechanics. Fluid and solid subproblems are solved separately and coupled through a strongly coupled partitioned Dirichlet-Neumann iteration, with Gauss-Seidel/Aitken or IQN-ILS interface acceleration. The solid discretisation improves face-gradient accuracy on arbitrary polyhedral meshes using central normal gradients and vertex-based Gauss-Green tangential gradients. Interface transfer uses GGI face interpolation and vertex displacement interpolation, with global face zones for parallel execution. Validation covers solid stress analysis, two- and three-dimensional FSI benchmarks, elastic-tube wave propagation, temporal/spatial accuracy, and parallel scaling.

**Relevance classification:** FV-but-partitioned

**Direct quote(s) supporting the classification:** "The solver is based on the cell-centred finite volume discretisation method for both domains and strongly coupled partitioned solution procedure" (p.2); "As mentioned earlier, the partitioned approach is adopted for the fluid-structure interaction solution procedure" (p.9).

**Notes for the authors:** The paper is highly relevant as an OpenFOAM, cell-centred FV FSI predecessor, but it is explicitly partitioned and uses PISO plus segregated solid solves rather than monolithic Newton/JFNK or a block preconditioner.

---
