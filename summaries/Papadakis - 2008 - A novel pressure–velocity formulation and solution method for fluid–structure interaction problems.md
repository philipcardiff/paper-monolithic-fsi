---

## Papadakis 2008 — Pressure-velocity finite-volume FSI

**Full citation:** Papadakis, G. A novel pressure-velocity formulation and solution method for fluid-structure interaction problems. Journal of Computational Physics, 227:3383-3404, 2008. DOI: 10.1016/j.jcp.2007.12.004

**BibTeX key suggestion:** papadakis2008

**Discretisation (fluid):** cell-centred FV

**Discretisation (solid):** cell-centred FV

**Coupling structure:** quasi-monolithic

**Mesh motion treatment:** Eulerian no mesh motion

**Nonlinear solver:** SIMPLE

**Preconditioner / linearisation:** Rhie-Chow stabilisation; SIMPLE pressure correction

**Test cases:** pressure wave propagation in an axisymmetric elastic tube; mesh and time-step sensitivity for elastic-tube wave propagation; incompressible-solid tube wall case; zero-ramp inlet-pressure robustness case; stiff-wall wave-speed case

**Code released?** not stated

**One-paragraph summary (under 120 words):** Papadakis reformulates linear Hookean solid dynamics in velocity-pressure variables so fluid and solid subdomains can use collocated finite-volume discretisation and SIMPLE pressure-velocity coupling. Solid pressure is derived from the constitutive equation, while fluid pressure is derived from continuity. The interface treatment uses common velocity unknowns and a pressure-correction relation enforcing normal traction compatibility while allowing a pressure jump across the fluid-solid interface. The method is implemented in an in-house unstructured finite-volume code and tested on pressure-wave propagation in an elastic tube, including compressible and incompressible solid walls. It is a unified SIMPLE-type FV FSI method, not a Newton-Krylov or block-preconditioned monolithic method.

**Relevance classification:** FV-but-unified-SIMPLE

**Direct quote(s) supporting the classification:** "finite volume and SIMPLE algorithm respectively" (p.3).

**Notes for the authors:** The abstract and conclusions call the approach fully coupled, but the nonlinear solution strategy is SIMPLE pressure correction rather than Newton-Krylov/JFNK or a block-preconditioned monolithic solve. The paper assumes small displacements and a fixed Eulerian mesh; it explicitly states that large deformations would require ALE mesh motion.

---
