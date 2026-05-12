---

## Ryzhakov 2010 — Monolithic Lagrangian FSI with PFEM

**Full citation:** Ryzhakov, P. B., Rossi, R., Idelsohn, S. R., Oñate, E. A monolithic Lagrangian approach for fluid–structure interaction problems. Computational Mechanics, 46:883–899, 2010. DOI: 10.1007/s00466-010-0522-0

**BibTeX key suggestion:** ryzhakov2010

**Discretisation (fluid):** FE

**Discretisation (solid):** FE

**Coupling structure:** monolithic

**Mesh motion treatment:** inside Newton vector for Lagrangian nodal displacements; re-meshing after convergence

**Nonlinear solver:** Newton

**Preconditioner / linearisation:** global pressure condensation; matrix-free diagonally preconditioned CG; pressure stabilization using consistent-minus-lumped pressure mass matrices

**Test cases:** dam-break fluid-only case; dam break against elastic obstacle; elastic plate subjected to water pressure; 3D water-filled elastic membrane balloon

**Code released?** Kratos Multi-Physics System; release/URL not stated

**One-paragraph summary (under 120 words):** The paper develops a monolithic Lagrangian PFEM/finite-element FSI method for flexible structures interacting with free-surface flows. The fluid is modeled as quasi-incompressible with linear displacement-pressure interpolation, while solids use standard displacement-based finite elements. Pressure is condensed globally to form a displacement-only linearized system, and the expensive pressure-gradient contribution is applied matrix-free inside a diagonally preconditioned conjugate-gradient solve. Newton iterations solve the nonlinear monolithic system, with remeshing after convergence. The examples emphasize free-surface FSI with light structures and compare against prior monolithic or unified Lagrangian methods.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "Current work presents a monolithic method for the solution of fluid–structure interaction problems involving flexible structures and free-surface flows." (p.1); "The method described features a global pressure condensation which in turn enables the definition of a purely displacement-based linear system of equations." (p.1); "The choice of using Krylov-type methods implies that a matrix-free approach can be used" (p.9).

**Notes for the authors:** Closest in monolithic/matrix-free spirit, but the discretisation is PFEM/finite element with diagonally preconditioned CG, not cell-centred FV, JFNK, PETSc, or block-preconditioned FSI.

---
