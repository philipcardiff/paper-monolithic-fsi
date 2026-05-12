---

## Lozovskiy 2015 — Unconditionally stable semi-implicit FSI FEM

**Full citation:** Lozovskiy, A., Olshanskii, M. A., Salamatova, V., Vassilevski, Y. V. An unconditionally stable semi-implicit FSI finite element method. Comput. Methods Appl. Mech. Engrg., 297:437-454, 2015. DOI: 10.1016/j.cma.2015.09.014

**BibTeX key suggestion:** lozovskiy2015

**Discretisation (fluid):** FE

**Discretisation (solid):** FE

**Coupling structure:** monolithic

**Mesh motion treatment:** ALE displacement extension from solid to fluid by auxiliary linear elasticity equation; no Newton vector

**Nonlinear solver:** semi-implicit linear scheme

**Preconditioner / linearisation:** extrapolated geometry and linearised fluid inertia; exact sparse factorization used; preconditioned iterative methods left for future work

**Test cases:** Flexible beam in 2D / Turek-Hron FSI3 benchmark; 2D blood flow in compliant vessel with aneurysm; comparison of compressible and incompressible neo-Hookean vessel wall models

**Code released?** Ani2D, http://sourceforge.net/projects/ani2d

**One-paragraph summary (under 120 words):** The paper develops a monolithic ALE finite element method for incompressible Newtonian fluid coupled to hyperelastic solids. Interface velocity and traction coupling are enforced strongly, while geometry and inertial nonlinearities are extrapolated so each time step requires one linear algebraic solve. The authors prove an energy balance and unconditional stability for a first-order version with Saint Venant-Kirchhoff or incompressible neo-Hookean solids, and use a second-order variant in computations. Results cover the Turek-Hron FSI3 beam benchmark and a hemodynamic aneurysm case, including comparisons of incompressible and nearly incompressible wall models.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "monolithic strongly coupled finite element method" (p.3); "only a linear algebraic system should be solved" (p.7)

**Notes for the authors:** Closest in monolithic/ALE/strong-coupling spirit, but not cell-centred FV and not Newton-Krylov; the paper explicitly leaves preconditioned iterative solvers for future work.

---
