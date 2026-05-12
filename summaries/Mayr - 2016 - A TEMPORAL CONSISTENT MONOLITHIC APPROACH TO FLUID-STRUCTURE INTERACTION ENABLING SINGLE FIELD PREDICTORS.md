---

## Mayr 2016 — Temporal-consistent monolithic FSI with single-field predictors

**Full citation:** Mayr, M., Klöppel, T., Wall, W. A., Gee, M. W. A Temporal Consistent Monolithic Approach to Fluid-Structure Interaction Enabling Single Field Predictors. SIAM Journal on Scientific Computing, 37(1):B30–B59, 2015. DOI: 10.1137/140953253

**BibTeX key suggestion:** mayr2015

**Discretisation (fluid):** FE (stabilised equal-order linear elements, ALE)

**Discretisation (solid):** FE (mixed/hybrid with enhanced assumed strains)

**Coupling structure:** monolithic

**Mesh motion treatment:** inside Newton vector (ALE mesh displacements `d^G` are part of the global linear system, see (3.10) and the condensed Jacobian (4.14a))

**Nonlinear solver:** Newton

**Preconditioner / linearisation:** full block Jacobian assembled with field sub-blocks (S_II, S_IΓ, F_II, F_IΓ, F^G, A_II, A_IΓ) plus mortar projection operator P; saddle-point system condensed to remove dual Lagrange multipliers; outer solve uses GMRES with per-field ILU(0) preconditioning (Section 5.2)

**Test cases:**
- Pseudo one-dimensional FSI with analytical solution (temporal convergence study)
- Two-dimensional leaky driven cavity with flexible bottom (predictor effect on linear-solver iteration count)
- Three-dimensional pressure wave through a collapsible tube (hemodynamic-style benchmark, meshes pw1-pw5 up to ~6.4M DOFs; comparison of generalized-α vs one-step-θ fluid integrators)

**Code released?** Not stated (developed at TUM Institute for Computational Mechanics)

**One-paragraph summary (under 120 words):** The paper presents a monolithic FE-FE FSI scheme that allows independent fully-implicit single-step time integrators in the fluid and structure fields while preserving temporal consistency via interpolation of interface tractions and a discrete ALE-displacement-to-velocity conversion. Spatial coupling uses a dual mortar method permitting nonmatching interface meshes; Lagrange multipliers are condensed and the resulting block Jacobian containing structure, fluid, and ALE sub-blocks (with mortar projection P) is solved by Newton with GMRES and per-field ILU(0) preconditioning. The framework additionally accommodates single-field predictors whose interface-continuity violations are absorbed inside the monolithic increment. Numerical examples include a pseudo-1D analytical test, a driven cavity, and a 3D pressure-wave tube.

**Relevance classification:** FE precedent for block-preconditioned Newton-Krylov FSI

**Direct quote(s) supporting the classification:** "To solve (3.4), a Newton-type method is applied requiring the full linearization of r^FSI" (p. B37); "The linear solver utilizes an ILU(0) preconditioner for each field and is solved using a GMRES procedure where the Krylov space dimension is set to 50" (p. B52); "Preconditioners based on block-triangular approximations of the Jacobian matrix have been introduced in [17] and extended in [27]" (p. B31, situating this work in the block-preconditioned monolithic FE-FSI tradition).

**Notes for the authors:** A textbook FE counterpart to the monolithic block-preconditioned FSI strategy: full Newton on a structured block Jacobian (with mortar projection coupling), GMRES with per-field ILU(0) as the outer preconditioner, and ALE mesh DOFs inside the Newton vector. It is FE rather than FV and uses field-wise ILU(0) rather than a Schur-complement-style approximate block preconditioner, but the algorithmic spine matches the new paper's quasi-monolithic JFNK target very closely.

---
