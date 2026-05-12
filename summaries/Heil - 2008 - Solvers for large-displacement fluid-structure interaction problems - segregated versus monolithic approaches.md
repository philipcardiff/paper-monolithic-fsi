---

## Heil 2008 — Solvers for large-displacement FSI

**Full citation:** Heil, M., Hazel, A. L., Boyle, J. Solvers for large-displacement fluid-structure interaction problems: segregated versus monolithic approaches. Computational Mechanics, 43:91-101, 2008. DOI: 10.1007/s00466-008-0270-6

**BibTeX key suggestion:** heil2008

**Discretisation (fluid):** FE

**Discretisation (solid):** FE

**Coupling structure:** monolithic

**Mesh motion treatment:** inside Newton vector

**Nonlinear solver:** Newton-Krylov

**Preconditioner / linearisation:** exact Jacobian / block preconditioner / pressure Schur complement

**Test cases:**
- 2D collapsible channel with elastic wall
- Immersed elastic leaflet in pulsatile channel flow
- Turek-Hron FSI2 and FSI3 cylinder-with-flag benchmarks
- 3D collapsible tube with self-excited oscillations

**Code released?** oomph-lib, http://www.oomph-lib.org

**One-paragraph summary (under 120 words):** This paper compares segregated Picard and monolithic Newton solvers for large-displacement FSI in the finite-element library oomph-lib. The fluid is solved with ALE incompressible Navier-Stokes elements and the structures with geometrically nonlinear beam, shell, or finite-thickness solid elements. For large problems, the monolithic Newton linear systems are solved by GMRES with block-triangular FSI preconditioners that reuse single-physics fluid and solid solvers; the fluid block uses an LSC pressure-Schur-complement preconditioner. The paper argues that monolithic Newton solvers can be competitive even for weak FSI and more robust for strong FSI, provided effective block preconditioners are used.

**Relevance classification:** FE precedent for block-preconditioned Newton-Krylov FSI

**Direct quote(s) supporting the classification:** "the complete system of nonlinear algebraic equations that arises from the coupled discretisation of the equations of motion in the fluid and solid domains is solved as a whole" (p.1); "iterative, Krylov subspace, methods, such as GMRES, which require the provision of efficient preconditioners" (p.7); "a block-triangular FSI preconditioner allows the re-use of existing single-physics solver/preconditioning strategies within the framework of a monolithic solver" (p.7).

**Notes for the authors:** Monolithic FE Newton-Krylov/block-preconditioned FSI precedent in oomph-lib; not cell-centred FV, not OpenFOAM/PETSc, and not Jacobian-free. The paper compares against segregated Picard solvers and includes exact Jacobian interaction blocks in the monolithic Newton linearisation.

---
