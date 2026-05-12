---

## Gee 2010 — Truly monolithic algebraic multigrid

**Full citation:** Gee, M. W., Küttler, U., and Wall, W. A. Truly monolithic algebraic multigrid for fluid–structure interaction. International Journal for Numerical Methods in Engineering, 85:987–1016, 2011. DOI: 10.1002/nme.3001

**BibTeX key suggestion:** gee2010

**Discretisation (fluid):** FE

**Discretisation (solid):** FE

**Coupling structure:** monolithic

**Mesh motion treatment:** inside Newton vector

**Nonlinear solver:** Newton-Krylov

**Preconditioner / linearisation:** exact Jacobian / block preconditioner / multigrid

**Test cases:** pressure wave in flexible tube; abdominal aortic aneurysm; flexible flag behind rigid obstacle

**Code released?** Baci code used; release not stated

**One-paragraph summary (under 120 words):** Gee et al. develop two AMG-based preconditioners for a monolithic Newton-Krylov ALE FSI formulation with fluid, solid, and mesh-motion unknowns in the coupled algebraic system. The first applies block Gauss-Seidel preconditioning with field-specific AMG approximate inverses; the second constructs a coupled nonsymmetric monolithic AMG hierarchy using field-wise transfer operators and block Gauss-Seidel smoothing. The implementation targets stabilized finite-element fluids, mixed/hybrid finite-element solids, and implicit time integration. Large pressure-wave, aneurysm, and flexible-flag examples compare the monolithic AMG preconditioners against partitioned Aitken and interface JFNK approaches, showing improved robustness and performance for strong added-mass cases.

**Relevance classification:** FE precedent for block-preconditioned Newton-Krylov FSI

**Direct quote(s) supporting the classification:** "a Newton–Krylov method is applied to the monolithic set of nonlinear equations" (p.1); "We propose two preconditioners that apply algebraic multigrid techniques to the entire fluid–structure interaction system of equations" (p.1); "mainly stabilized finite elements for the fluid [23] and mixed/hybrid finite elements for the structural domain are used" (p.3).

**Notes for the authors:** Strong prior art for monolithic block-preconditioned Newton-Krylov FSI, but it is FE/ALE with assembled Jacobian blocks and AMG, not cell-centred FV, OpenFOAM/solids4foam, PETSc, or Jacobian-free residual differencing.

---
