---

## Hubner 2004 — Monolithic FSI using space-time finite elements

**Full citation:** Hubner, B., Walhorn, E., Dinkler, D. A monolithic approach to fluid–structure interaction using space–time finite elements. Computer Methods in Applied Mechanics and Engineering, 193(23–26):2087–2104, 2004. DOI: 10.1016/j.cma.2004.01.024

**BibTeX key suggestion:** hubner2004

**Discretisation (fluid):** FE (stabilised space-time, Petrov–Galerkin, hexahedral elements)

**Discretisation (solid):** FE (stabilised space-time, mixed velocity–stress formulation, geometrically nonlinear)

**Coupling structure:** monolithic

**Mesh motion treatment:** inside Newton vector (fluid mesh coordinates treated as unknowns solved within the same iteration loop as fluid and structure; mesh pseudo-elasticity solved as a sub-step within each Picard iteration but within the single loop)

**Nonlinear solver:** Picard (fixed-point iteration; Newton–Raphson avoided due to cost of exact Jacobian for convection-dominated flow and moving domains)

**Preconditioner / linearisation:** approximate Jacobian (Picard linearisation with direct LU decomposition used as preconditioner for BiCGStab; SOR and ILU noted as insufficient)

**Test cases:**
- Piston-channel system: 1-D verification with analytical comparison, large ALE mesh deformation
- 2D wind flow over a building with elastic membrane roof (Re ≈ 1700, membrane flutter)
- Vortex-excited elastic cantilever plate in the wake of a rigid square cylinder (Re = 204, two stable solutions)

**Code released?** Not stated

**One-paragraph summary (under 120 words):** This paper presents a fully monolithic FSI method in which incompressible Navier–Stokes equations and geometrically nonlinear elastodynamics are discretised with a unified stabilised space-time finite element scheme (time-discontinuous Galerkin, Petrov–Galerkin stabilisation). Fluid, structure, and ALE mesh motion are assembled into a single block equation system and solved in one Picard iteration loop per time slab, avoiding the time-lag of partitioned schemes. The linearised system is solved with BiCGStab preconditioned by direct LU decomposition of the approximate (Picard) Jacobian. The method achieves third-order time accuracy, satisfies the GCL inherently, and converges in 2–4 Picard iterations even for strongly coupled problems with large deformations, at roughly the same cost as solving the fluid alone.

**Relevance classification:** FE precedent for block-preconditioned Newton-Krylov FSI

**Direct quote(s) supporting the classification:** N/A

**Notes for the authors:** The nonlinear solver is Picard (not Newton or JFNK), but the paper is the canonical early monolithic FE-FSI reference with a block-assembled system solved by a Krylov method (BiCGStab) with an LU-based preconditioner — directly analogous in spirit to the block-preconditioned JFNK approach of the paper being written, but using FE rather than cell-centred FV. The scalability limitation is explicitly acknowledged: the direct LU preconditioner is impractical for large 3D problems, which motivates the need for approximate block preconditioners such as those used in the authors' own work.

---
