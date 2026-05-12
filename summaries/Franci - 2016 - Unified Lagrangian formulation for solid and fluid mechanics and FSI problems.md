---

## Franci 2016 — Unified Lagrangian FSI formulation

**Full citation:** Franci, A., Onate, E., Carbonell, J. M. Unified Lagrangian formulation for solid and fluid mechanics and FSI problems. Computer Methods in Applied Mechanics and Engineering, 298:520-547, 2016. DOI: 10.1016/j.cma.2015.09.023

**BibTeX key suggestion:** franci2016

**Discretisation (fluid):** FE / particle finite element method (PFEM)

**Discretisation (solid):** FE

**Coupling structure:** monolithic / unified one-continuum

**Mesh motion treatment:** Lagrangian moving mesh with PFEM remeshing for fluids; conformal moving FEM mesh for solids

**Nonlinear solver:** fixed-point / two-step Gauss-Seidel iterative procedure

**Preconditioner / linearisation:** tangent matrix linearisation; FIC stabilisation; pseudo bulk modulus in fluid momentum tangent

**Test cases:**
- Falling of a cylinder in a viscous fluid
- Filling of an elastic container with a viscous fluid
- Collapse of a water column on a deformable membrane

**Code released?** not stated

**One-paragraph summary (under 120 words):** Franci et al. present a unified Lagrangian FE/PFEM formulation for solids, fluids, and FSI using common velocity-pressure unknowns. Fluids use a stabilized velocity-pressure PFEM element, while solids use velocity, velocity-pressure, or stabilized velocity-pressure hypoelastic FEM elements. The FSI system is assembled monolithically with conformal interface nodes and separate pressure degrees of freedom for fluid and solid at the interface. Each time step is advanced by a two-step Gauss-Seidel iterative procedure: solve momentum for velocity increments, update coordinates, then solve continuity for pressure. The paper validates the formulation on free-surface FSI benchmarks with large structural motion.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "We present a Lagrangian monolithic strategy for solving fluid-structure interaction (FSI) problems." (p.1); "fluids and solids are solved within the same linear system of algebraic equations" (p.3).

**Notes for the authors:** Closest in spirit because it is monolithic and unified, but it is FE/PFEM with a two-step Gauss-Seidel pressure-velocity procedure, not cell-centred FV, JFNK, PETSc, or block-preconditioned.

---
