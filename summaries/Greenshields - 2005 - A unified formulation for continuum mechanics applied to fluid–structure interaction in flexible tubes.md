---

## Greenshields 2005 — Unified continuum FSI in flexible tubes

**Full citation:** Greenshields, C. J., Weller, H. G. A unified formulation for continuum mechanics applied to fluid-structure interaction in flexible tubes. International Journal for Numerical Methods in Engineering, 64:1575-1593, 2005. DOI: 10.1002/nme.1409

**BibTeX key suggestion:** greenshields2005

**Discretisation (fluid):** cell-centred FV

**Discretisation (solid):** cell-centred FV

**Coupling structure:** unified one-continuum

**Mesh motion treatment:** Eulerian no mesh motion

**Nonlinear solver:** PISO

**Preconditioner / linearisation:** Rhie-Chow stabilisation

**Test cases:** clamped elastic beam dynamic bending; pressure-wave propagation in a highly flexible straight tube; mesh-refinement study for tube wave speed; tube wave speed over wall modulus 10^6 to 10^11 Pa

**Code released?** OpenFOAM, URL not stated in PDF

**One-paragraph summary (under 120 words):** The paper derives a single velocity-pressure continuum formulation for Newtonian fluids and small-strain Hookean solids, using accumulated deviatoric stress to express the solid momentum equation in a fluid-like Eulerian form. Fluid and solid are represented in one mesh and discretised with finite volumes in OpenFOAM. A PISO-like segregated pressure-velocity procedure solves the weakly compressible continuum equations. Validation uses an undamped clamped beam and pressure-wave propagation in flexible tubes representative of arteries. The work is relevant as an early OpenFOAM cell-centred FV one-continuum FSI method, but it is not a moving-mesh quasi-monolithic formulation and does not use Newton-Krylov or block preconditioning.

**Relevance classification:** Eulerian-one-continuum FV FSI

**Direct quote(s) supporting the classification:** "both fluid and solid components are solved within a single discretized continuum domain" (p.1); "described by a single mesh and solved using one set of equations" (p.4); "An algorithm similar to PISO [23] is adopted to ensure that the velocity field satisfies the continuity equation" (p.9).

**Notes for the authors:** Abstract and method are consistent. The paper is highly relevant as an OpenFOAM FV unified-continuum predecessor, but the solver is segregated/PISO-like and Eulerian, not JFNK/PETSc/block-preconditioned or ALE quasi-monolithic.

---
