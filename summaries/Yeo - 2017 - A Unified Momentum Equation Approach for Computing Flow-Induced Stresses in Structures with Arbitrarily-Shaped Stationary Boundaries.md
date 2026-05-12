---

## Yeo 2017 — Unified Momentum Equation for Flow-Induced Stresses

**Full citation:** Yeo, H., Ki, H. A Unified Momentum Equation Approach for Computing Flow-Induced Stresses in Structures with Arbitrarily-Shaped Stationary Boundaries. Communications in Computational Physics, 22(1):39-63, 2017. DOI: 10.4208/cicp.OA-2016-0035

**BibTeX key suggestion:** yeo2017

**Discretisation (fluid):** cell-centred FV

**Discretisation (solid):** cell-centred FV

**Coupling structure:** unified one-continuum

**Mesh motion treatment:** Eulerian no mesh motion

**Nonlinear solver:** SIMPLE

**Preconditioner / linearisation:** N/A

**Test cases:** 
- Lid-driven square cavity inside a solid container
- Lid-driven semi-circular cavity inside a solid container
- Flow over a fixed circular cylinder with structural stresses

**Code released?** not stated

**One-paragraph summary (under 120 words):** The paper derives a velocity-based unified momentum equation by hybridising incompressible Newtonian fluid momentum and linear elastic solid momentum for stationary fluid-structure boundaries. Material properties and source terms are smeared across a finite-thickness interface using a shifted Heaviside/level-set function, allowing arbitrarily shaped embedded boundaries on a Cartesian grid without a body-fitted interface. The resulting equations are discretised by a finite volume method on a staggered grid and solved with SIMPLE, with pressure correction applied only in fluid and smeared-interface regions. Validation compares stress and velocity fields for cavity and cylinder cases against COMSOL and literature data.

**Relevance classification:** FV-but-unified-SIMPLE

**Direct quote(s) supporting the classification:** "a unified momentum equation for a continuum consisting of both fluids and solids is derived in terms of velocity" (p.1); "A finite volume approach is employed to discretize the obtained governing equations on a Cartesian grid" (p.1); "the Semi-Implicit Method for Pressure Linked Equations (SIMPLE) algorithm [31] is employed as the coupling method" (p.8).

**Notes for the authors:** Although the abstract calls the method monolithic, the method is a unified stationary-boundary/SIMPLE formulation rather than a moving-mesh FSI formulation with Newton-Krylov or block preconditioning.

---
