---

## Richter 2015 — Monolithic geometric multigrid ALE FSI solver

**Full citation:** Richter, T. A monolithic geometric multigrid solver for fluid-structure interactions in ALE formulation. International Journal for Numerical Methods in Engineering, 104:372-390, 2015. DOI: 10.1002/nme.4943

**BibTeX key suggestion:** richter2015

**Discretisation (fluid):** FE

**Discretisation (solid):** FE

**Coupling structure:** monolithic

**Mesh motion treatment:** inside Newton vector

**Nonlinear solver:** Newton-Krylov

**Preconditioner / linearisation:** exact Jacobian / multigrid / approximate Jacobian

**Test cases:** 2d Hron-Turek FSI3 benchmark; 3d channel with elastic obstacle; parameter-robustness tests varying density, inflow velocity, shear modulus, and Poisson ratio

**Code released?** GASCOIGNE 3D, http://www.gascoigne.uni-hd.de

**One-paragraph summary (under 120 words):** Richter presents a fully monolithic ALE finite-element formulation for incompressible fluid interaction with nonlinear hyperelastic solids. Each time step is solved by Newton linearisation of velocity, pressure, and deformation, with analytic Jacobian assembly or reused Jacobians in an approximate Newton variant. The linear systems are treated by monolithic GMRES preconditioned by a geometric multigrid method; only the multigrid smoother is partitioned into solid, mesh-extension, and Navier-Stokes subproblems with Dirichlet-Neumann interface coupling and blockwise ILU/Richardson smoothing. The paper demonstrates mesh-robust convergence and linear memory growth on 2d and 3d FSI benchmarks, arguing that partitioning inside the smoother avoids the conditioning and memory problems of direct or fully coupled smoothers.

**Relevance classification:** FE precedent for block-preconditioned Newton-Krylov FSI

**Direct quote(s) supporting the classification:** "Our proposed solver is based on a Newton linearization of the fully monolithic system of equations, discretized by a Galerkin finite element method" (p.1); "Approximation of the linearized systems is based on a monolithic generalized minimal residual method iteration, preconditioned by a geometric multigrid solver" (p.1); "The special character of fluid-structure interactions is accounted for by a partitioned scheme within the multigrid smoother only" (p.1).

**Notes for the authors:** Strongly relevant monolithic FE Newton-GMRES/multigrid precedent, but not cell-centred FV, OpenFOAM/PETSc, or Jacobian-free; the Jacobian is analytically evaluated and sometimes reused in an approximate Newton scheme.

---
