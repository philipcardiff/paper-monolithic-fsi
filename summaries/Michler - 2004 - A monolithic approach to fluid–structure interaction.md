---

## Michler 2004 — Monolithic fluid-structure interaction

**Full citation:** Michler, C., Hulshoff, S. J., van Brummelen, E. H., de Borst, R. A monolithic approach to fluid-structure interaction. Computers & Fluids, 33:839-848, 2004. DOI: 10.1016/j.compfluid.2003.06.006

**BibTeX key suggestion:** michler2004

**Discretisation (fluid):** FE

**Discretisation (solid):** N/A

**Coupling structure:** monolithic

**Mesh motion treatment:** N/A

**Nonlinear solver:** N/A

**Preconditioner / linearisation:** N/A

**Test cases:** one-dimensional piston interacting with a compressible fluid; monolithic vs partitioned stability comparison; temporal mesh refinement study; computational cost of monolithic iterations with and without prediction

**Code released?** not stated

**One-paragraph summary (under 120 words):** The paper compares partitioned and monolithic solution procedures for a one-dimensional compressible-fluid piston FSI model. The fluid is discretised using a space-time time-discontinuous Galerkin least-squares finite element method in primitive variables, while the structure is a one-degree-of-freedom spring-mass system integrated by the trapezoidal method. Interface pressure, displacement, and velocity are enforced synchronously for the monolithic method, which is compared against partitioned schemes with and without structural prediction. The results show partitioning-induced amplitude growth and first-order coupling accuracy without prediction, while the monolithic scheme remains stable, second-order accurate, and more accurate per time step, at higher per-step cost.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "This paper compares partitioned and monolithic solution procedures for the numerical simulation of fluid-structure interactions." (p.1); "In a monolithic method, the interaction of the fluid and the structure at the mutual interface is treated synchronously." (p.4); "The discretized equations are then typically solved by multiple fluid-structure iterations" (p.4).

**Notes for the authors:** Monolithic FSI precedent focused on stability, accuracy, and cost, but the model is one-dimensional with a spring-mass piston, the fluid discretisation is FE/DG rather than cell-centred FV, and no Newton-Krylov, JFNK, PETSc, or block preconditioner is described.

---
