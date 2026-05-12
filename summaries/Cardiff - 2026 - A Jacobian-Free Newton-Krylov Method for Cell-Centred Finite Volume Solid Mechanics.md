---

## Cardiff 2026 — JFNK for FV Solid Mechanics

**Full citation:** Cardiff, P., Armfield, D., Tuković, Ž., Batistić, I. A Jacobian-Free Newton-Krylov Method for Cell-Centred Finite Volume Solid Mechanics. International Journal for Numerical Methods in Engineering, 127(3):e70268, 2026. DOI: 10.1002/nme.70268

**BibTeX key suggestion:** cardiff2026

**Discretisation (fluid):** N/A

**Discretisation (solid):** cell-centred FV

**Coupling structure:** N/A

**Mesh motion treatment:** N/A

**Nonlinear solver:** JFNK

**Preconditioner / linearisation:** approximate Jacobian; compact-stencil approximate Jacobian used as preconditioner; GMRES with LU, ILU(k), or HYPRE BoomerAMG; Rhie-Chow stabilisation

**Test cases:** manufactured-solution elastic cube; spherical cavity under remote stress; elliptic plate bending; Cook's membrane linear elastic/hyperelastic/hyperelastoplastic variants; idealised ventricle, dynamic cantilever beam, and Turek-Hron FSI3 plate benchmark

**Code released?** solids4foam for OpenFOAM, https://github.com/solids4foam/solids4foam, feature-petsc-snes branch; benchmark cases and plotting scripts at https://github.com/solids4foam/solid-benchmarks

**One-paragraph summary (under 120 words):** The paper introduces a Jacobian-free Newton-Krylov solver for Lagrangian cell-centred finite volume solid mechanics in solids4foam/OpenFOAM using PETSc. It evaluates a compact-stencil approximate Jacobian, equivalent to the segregated diffusion-style FV matrix, as a preconditioner for GMRES. The method is benchmarked against the conventional segregated solver over static, dynamic, linear elastic, hyperelastic, and elastoplastic cases. It usually gives large speedups for elastic and hyperelastic problems, with preconditioner choice controlling performance and memory use, but it diverges for the elastoplastic Cook's membrane cases. The included FSI benchmark uses existing partitioned FSI coupling rather than a monolithic FSI formulation.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "the first (to the authors' knowledge) to propose a Jacobian-free Newton-Krylov approach for finite volume solid mechanics" (p.4); "we propose to use the compact-stencil approximate Jacobian from the segregated algorithm as the preconditioning matrix" (p.12); "The implementation is made publicly available within the solids4foam toolbox for OpenFOAM" (p.31).

**Notes for the authors:** Do not cite this as monolithic FSI prior work: the paper is solid-mechanics-focused, and the Turek-Hron FSI3 case uses a segregated PIMPLE fluid solver with partitioned interface quasi-Newton coupling. The abstract reports elastoplastic divergence, consistent with Section 4.2.

---
