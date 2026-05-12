---

## Heil 2004 — Efficient solver for monolithic FSI

**Full citation:** Heil, M. An efficient solver for the fully coupled solution of large-displacement fluid-structure interaction problems. Computer Methods in Applied Mechanics and Engineering, 193:1-23, 2004. DOI: 10.1016/j.cma.2003.09.006

**BibTeX key suggestion:** heil2004

**Discretisation (fluid):** FE

**Discretisation (solid):** FE

**Coupling structure:** monolithic

**Mesh motion treatment:** inside Newton vector

**Nonlinear solver:** Newton-Krylov

**Preconditioner / linearisation:** exact Jacobian; approximate Jacobian; block preconditioner; pressure Schur complement; multigrid

**Test cases:** 
- Steady flow in a two-dimensional collapsible channel with a pre-stressed elastic membrane
- Multiple steady wall shapes and limit points at finite Reynolds number
- Unsteady self-excited oscillations of the elastic membrane
- Stabilisation tests for steady and unsteady channel-collapse simulations

**Code released?** not stated

**One-paragraph summary (under 120 words):** The paper develops a fully coupled finite-element solver for large-displacement incompressible FSI in a moving ALE domain. Fluid, solid, pressure, and mesh-coupling effects are assembled into one nonlinear system solved by Newton's method; the linear Newton systems are solved using GMRES with block-triangular preconditioners formed by dropping selected FSI Jacobian blocks. The fluid block is further approximated by a pressure Schur-complement preconditioner and fixed-cost multigrid solves. The method is demonstrated on steady and unsteady collapsible-channel simulations, including large-amplitude self-excited oscillations, and shows mild dependence of GMRES counts on Reynolds number and mesh size.

**Relevance classification:** FE precedent for block-preconditioned Newton-Krylov FSI

**Direct quote(s) supporting the classification:** "fully coupled ('monolithic') solution" (p.1); "provide good preconditioners for the solution of the linear systems with GMRES" (p.1).

**Notes for the authors:** Strong FE precedent for monolithic Newton-GMRES FSI with block-triangular approximate Jacobian preconditioning and pressure Schur-complement/multigrid approximations. Not cell-centred FV, not Jacobian-free, and not OpenFOAM/PETSc.

---
