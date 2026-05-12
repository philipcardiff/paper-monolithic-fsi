---

## Cerquaglia 2019 — Fully partitioned Lagrangian FSI framework

**Full citation:** Cerquaglia, M. L., Thomas, D., Boman, R., Terrapon, V., Ponthot, J.-P. A fully partitioned Lagrangian framework for FSI problems characterized by free surfaces, large solid deformations and displacements, and strong added-mass effects. Computer Methods in Applied Mechanics and Engineering, 348:409-442, 2019. DOI: 10.1016/j.cma.2019.01.021

**BibTeX key suggestion:** cerquaglia2019

**Discretisation (fluid):** particle finite element method (PFEM)

**Discretisation (solid):** FE

**Coupling structure:** partitioned

**Mesh motion treatment:** partitioned outer loop

**Nonlinear solver:** quasi-Newton (IQN-ILS) for FSI coupling; Picard fluid; Newton-Raphson solid

**Preconditioner / linearisation:** approximate inverse interface Jacobian by IQN-ILS least-squares; no monolithic preconditioner

**Test cases:** 
- vortex-induced vibrations of a cantilever
- dam break against an elastic-plastic obstacle
- fluid column on an elastic column
- dam break through an elastic gate
- cylinder pop-off; filling of an elastic container

**Code released?** not stated

**One-paragraph summary (under 120 words):** The paper couples an in-house PFEM incompressible free-surface fluid solver with the nonlinear FE solid solver Metafor through CUPyDO. The method is fully partitioned and exchanges interface loads and displacements through Dirichlet-Neumann coupling. Its main technical contribution is extending CUPyDO with IQN-ILS coupling for fully Lagrangian PFEM/FEM FSI problems with large solid motion, free surfaces, and strong added-mass effects. Fluid equations are solved with a stabilized monolithic PFEM formulation and Picard iterations; the solid uses Newton-Raphson. Results compare BGS/Aitken and IQN-ILS on several benchmarks, showing IQN-ILS reduces or avoids added-mass convergence failures.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "fully partitioned Lagrangian framework" (p.1); "partitioned FSI coupling" (p.1); "matrix-free and directly provides an approximation of the inverse Jacobian" (p.8).

**Notes for the authors:** Closest in spirit because it uses matrix-free IQN-ILS and black-box solver coupling for severe added-mass FSI, but it is fully partitioned PFEM/FEM rather than quasi-monolithic cell-centred FV/JFNK/PETSc. No abstract-method inconsistency found.

---
