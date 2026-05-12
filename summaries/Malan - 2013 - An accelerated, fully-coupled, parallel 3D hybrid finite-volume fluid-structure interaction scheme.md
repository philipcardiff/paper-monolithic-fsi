---

## Malan 2013 — Accelerated fully-coupled hybrid FV FSI

**Full citation:** Malan, A. G., Oxtoby, O. F. An accelerated, fully-coupled, parallel 3D hybrid finite-volume fluid-structure interaction scheme. Computer Methods in Applied Mechanics and Engineering, 253:426-438, 2013. DOI: 10.1016/j.cma.2012.09.004

**BibTeX key suggestion:** malan2013

**Discretisation (fluid):** vertex-centred FV

**Discretisation (solid):** vertex-centred FV

**Coupling structure:** partitioned

**Mesh motion treatment:** outside Newton vector

**Nonlinear solver:** fixed-point

**Preconditioner / linearisation:** approximate Jacobian; LU-SGS preconditioned GMRES; LU-SGS momentum relaxation; consistent numerical flux stabilisation

**Test cases:**
- 3D block with flexible plate in cross-flow, stiff plate case
- 3D block with flexible plate in cross-flow, flexible/twisting plate case
- Solver speed-up and parallel strong-scaling on the block-plate problem
- Pressure pulse in a flexible tube / arterial-flow benchmark

**Code released?** Elemental; not stated as open source

**One-paragraph summary (under 120 words):** This paper develops a parallel, matrix-free, strongly coupled partitioned FSI solver using vertex-centred edge-based finite volumes for both incompressible ALE fluid flow and geometrically nonlinear elastic solids. Coupling occurs through dual-time sub-iterations exchanging interface tractions and velocities, while the fluid pressure equation is accelerated with LU-SGS preconditioned GMRES and the momentum equation with LU-SGS relaxation. The solid uses a hybrid nodal/elemental strain finite volume formulation. Results on a 3D flexible-tail benchmark and a flexible-tube pressure pulse show large speedups and near-linear parallel scaling, but the FSI coupling remains partitioned/block-Jacobi rather than monolithic Newton-Krylov.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "we propose a fast, parallel 3D, fully-coupled partitioned hybrid-unstructured finite volume fluid-structure-interaction (FSI) scheme" (p.1); "We therefore advocate a strongly coupled, partitioned, matrix-free iterative solution process" (p.4); "the method above represents a block-Jacobi method" (p.6).

**Notes for the authors:** The "fully-coupled" terminology means strongly coupled partitioned dual-time iterations, not a monolithic Newton or JFNK solve; Section 4.5 explicitly identifies the FSI-level method as block-Jacobi and notes possible added-mass robustness limits.

---
