---

## Malan 2012 — Accelerated parallel hybrid FV FSI

**Full citation:** Malan, A. G., Oxtoby, O. F. An accelerated, fully-coupled, parallel 3D hybrid finite-volume fluid-structure interaction scheme. Preprint submitted to Computer Methods in Applied Mechanics and Engineering, 2012. DOI: N/A

**BibTeX key suggestion:** malan2012

**Discretisation (fluid):** vertex-centred FV

**Discretisation (solid):** vertex-centred FV

**Coupling structure:** partitioned

**Mesh motion treatment:** outside Newton vector

**Nonlinear solver:** fixed-point

**Preconditioner / linearisation:** approximate Jacobian / LU-SGS preconditioned GMRES

**Test cases:** block with flapping flexible plate; stiff and flexible plate variants; pressure pulse in flexible tube

**Code released?** not stated

**One-paragraph summary (under 120 words):** The paper presents a parallel 3D strongly coupled partitioned FSI solver using vertex-centred edge-based finite volumes for both incompressible fluid and nonlinear elastic solid domains. The fluid uses an ALE artificial-compressibility split-step method with consistent numerical flux stabilisation, dual-time stepping, implicit pressure solution by LU-SGS preconditioned GMRES, and LU-SGS relaxation for momentum terms. The solid is advanced with a Jacobi iterative procedure, while interface tractions and velocities are exchanged during pseudo-time iterations. Mesh motion is handled by a separate interpolation procedure. The method is evaluated on 3D flapping-plate and flexible-tube benchmarks, reporting large solver speedups and near-linear MPI scaling.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "a fast, parallel 3D, fully-coupled partitioned hybrid-unstructured finite volume fluid-structure-interaction (FSI) scheme" (p.1); "a strongly coupled, partitioned, matrix-free iterative solution process" (p.7); "As far as fluid-structure interaction is concerned, the method above represents a block-Jacobi method" (p.14).

**Notes for the authors:** The abstract and title emphasise "fully-coupled", but Section 4.5 states the FSI coupling is block-Jacobi and the introduction explicitly frames the method as partitioned. It is close in finite-volume, matrix-free, strongly coupled spirit, but not quasi-monolithic and not JFNK.

---
