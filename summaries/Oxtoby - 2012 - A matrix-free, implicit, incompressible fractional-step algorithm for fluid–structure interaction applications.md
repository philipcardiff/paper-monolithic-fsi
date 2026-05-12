---

## Oxtoby 2012 — Matrix-free implicit fractional-step algorithm for FSI

**Full citation:** Oxtoby, O.F., Malan, A.G. A matrix-free, implicit, incompressible fractional-step algorithm for fluid–structure interaction applications. Journal of Computational Physics, 231(14):5389–5405, 2012. DOI: 10.1016/j.jcp.2012.04.037

**BibTeX key suggestion:** oxtoby2012

**Discretisation (fluid):** vertex-centred FV

**Discretisation (solid):** vertex-centred FV

**Coupling structure:** partitioned

**Mesh motion treatment:** partitioned outer loop

**Nonlinear solver:** fixed-point (dual-timestepping pseudo-temporal iteration; Jacobi for momentum, preconditioned GMRES for pressure)

**Preconditioner / linearisation:** approximate Jacobian (LU-SGS preconditioned GMRES for the pressure equation)

**Test cases:**
- Lid-driven cavity at Re = 5000 (fluid-only validation, mesh-independence study)
- Block with flexible tail in cross-flow (FSI benchmark from Hübner et al., limit-cycle oscillation, tip displacement)
- GMRES speedup and parallel strong-scaling study using the block-tail problem (up to 40 processors)

**Code released?** Elemental multiphysics code (CSIR/UCT); not stated as open source, no URL given.

**One-paragraph summary (under 120 words):** This paper develops a fast, fully-coupled, partitioned FSI solver within the *Elemental* multiphysics code, using a vertex-centred edge-based FV discretisation for both fluid and solid on hybrid unstructured meshes. Two novel matrix-free implicit fractional-step incompressible flow algorithms are introduced: an Upwind Pressure-Projection Artificial Compressibility (UP-AC) scheme and a Consistent Numerical Flux Artificial Compressibility (CNF-AC) scheme. A dual-timestepping strategy drives explicit Jacobi iterations for momentum concurrently with implicit LU-SGS preconditioned GMRES for pressure. The partitioned coupling exchanges tractions and velocities at the fluid-solid interface each pseudo-timestep. The preconditioned GMRES pressure solver achieves speedups of 50–80× over Jacobi, and near-linear parallel scaling is demonstrated to ~30 processors.

**Relevance classification:** FV-but-partitioned

**Direct quote(s) supporting the classification:** N/A

**Notes for the authors:** The solver is partitioned but achieves strong (sub-iteration level) coupling via the dual-timestepping loop — fluid and solid are solved concurrently within each pseudo-timestep, with interface conditions exchanged every iteration. This is worth distinguishing from loosely-coupled staggered partitioned schemes. The LU-SGS preconditioned GMRES applied to the pressure equation is conceptually analogous to (but distinct from) the block-preconditioned Krylov approach used for the monolithic system in the target paper. The Elemental code appears to be an in-house research code and is not publicly available.

---
