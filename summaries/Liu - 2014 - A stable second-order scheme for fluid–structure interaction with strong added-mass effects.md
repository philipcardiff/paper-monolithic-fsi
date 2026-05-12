---

## Liu 2014 — Stable second-order added-mass FSI scheme

**Full citation:** Liu, J., Jaiman, R. K., Gurugubelli, P. S. A stable second-order scheme for fluid-structure interaction with strong added-mass effects. Journal of Computational Physics, 270:687-710, 2014. DOI: 10.1016/j.jcp.2014.04.020

**BibTeX key suggestion:** liu2014

**Discretisation (fluid):** FE

**Discretisation (solid):** FE

**Coupling structure:** quasi-monolithic

**Mesh motion treatment:** outside Newton vector

**Nonlinear solver:** explicit

**Preconditioner / linearisation:** linearisation by extrapolation; direct solver; no Newton-Raphson iteration

**Test cases:** elastic semi-circular cylinder temporal-accuracy test; Turek-Hron cylinder-elastic bar FSI-I; Turek-Hron cylinder-elastic bar FSI-II/FSI-III; thin flexible plate flapping with low mass ratio

**Code released?** not stated

**One-paragraph summary (under 120 words):** The paper presents a second-order combined-field with explicit-interface-advancing (CFEI) scheme for ALE fluid-structure interaction. Fluid and solid velocities are solved in a single finite-element weak formulation, with velocity continuity built into the function space and traction continuity enforced weakly, while the solid position and fluid mesh are extrapolated explicitly. The resulting method solves one linearized coupled system per time step, avoiding Newton iterations, and proves energy stability for arbitrary density ratio. Verification covers temporal convergence, Turek-Hron FSI benchmarks, and low-mass-ratio flexible-plate flapping.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "fully coupled FSI problems which is stable for any mass density ratio" (p.2).

**Notes for the authors:** The paper is close in spirit because it targets stable fully coupled FSI with strong added-mass effects, but it is FE-based CFEI with explicit interface advancement, semi-implicit linearisation, and direct linear solves, not cell-centred FV/JFNK/PETSc/block-preconditioned. The abstract calls the method stable for any mass density ratio; Section 3 clarifies that no Newton-Raphson iteration is used.

---
