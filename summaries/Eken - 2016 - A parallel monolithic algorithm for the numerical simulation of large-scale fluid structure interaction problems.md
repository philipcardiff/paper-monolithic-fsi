---

## Eken 2016 — Parallel monolithic FSI algorithm for large-scale problems

**Full citation:** Eken, A. and Sahin, M. A parallel monolithic algorithm for the numerical simulation of large-scale fluid structure interaction problems. Int. J. Numer. Meth. Fluids, 80(11):687–714, 2016. DOI: 10.1002/fld.4169

**BibTeX key suggestion:** eken2016

**Discretisation (fluid):** vertex-centred FV (side-centred, staggered unstructured; velocity at face midpoints, pressure at cell centroids)

**Discretisation (solid):** FE (Galerkin trilinear hexahedral elements, Lagrangian frame)

**Coupling structure:** monolithic

**Mesh motion treatment:** inside Newton vector (mesh displacement degrees of freedom are part of the coupled nonlinear system solved at each Newton iteration)

**Nonlinear solver:** Newton-Krylov (inexact Newton with FGMRES(m) inner Krylov solver; fixed number of outer Newton iterations per time step)

**Preconditioner / linearisation:** approximate Jacobian + block preconditioner (upper triangular right preconditioner replacing the zero pressure block with a scaled discrete Laplacian via matrix–matrix product, followed by one-level restricted additive Schwarz (RAS) with ILU(k) subdomain solves; implemented via PETSc)

**Test cases:**
- Elastic bar attached behind a rigid cylinder (Turek–Hron FSI-1 and FSI-3 benchmarks, 2D)
- Pressure pulse propagating in a flexible circular tube (3D blood-flow benchmark, Formaggia et al.)
- Vortex-induced vibration of a 3D flag attached behind a rectangular rigid body
- Elastic circular ring moving in a channel (2D)

**Code released?** Not stated (PETSc library used for linear algebra; custom in-house code; no public repository mentioned)

**One-paragraph summary (under 120 words):** Eken and Sahin present a fully monolithic ALE-based FSI algorithm combining a side-centred unstructured finite volume discretisation for incompressible Navier–Stokes (velocity at face midpoints, pressure at element centroids) with a Galerkin finite element discretisation for a Saint Venant–Kirchhoff solid on conforming hexahedral meshes. The coupled nonlinear system, which includes fluid, mesh-motion, solid, and interface unknowns, is solved with an inexact Newton–Krylov method (FGMRES). Preconditioning uses an upper triangular right preconditioner that eliminates the zero pressure block by introducing a scaled discrete Laplacian, followed by a one-level restricted additive Schwarz preconditioner with ILU(k) subdomain solves via PETSc. Special attention is paid to satisfying both local and global discrete geometric conservation laws exactly.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "The goal of the present paper is to incorporate the ALE-based unstructured finite volume algorithm [11] with the classical Galerkin finite element discretization for the solid domain in order to develop a novel monolithic algorithm for the large-scale simulation of FSI problems in a fully coupled form" (p. 688). "In the present paper, the original system of equations is multiplied with an upper triangular right preconditioner that results in a scaled discrete Laplacian instead of a zero block in the original system. Then, a one-level restricted additive Schwarz preconditioner with a block-incomplete factorization within each partitioned sub-domains is utilized for the modified fully coupled system." (p. 689).

**Notes for the authors:** The fluid discretisation is side-centred (staggered) rather than cell-centred collocated: velocities live at face midpoints, not cell centroids. This distinguishes it from the cell-centred FV approach in the paper under review. The solid uses standard FE, not FV. The Newton-Krylov preconditioner strategy (right-preconditioned triangular block approach replacing the zero divergence block with a Laplacian) is directly analogous in spirit to the block-preconditioning strategy used in the paper under review, making this a key reference for comparison, albeit on a different mesh arrangement. Parallelism is achieved via domain decomposition with PETSc/METIS; scaling results are reported up to 128 cores with ~2.5M DOF.

---
