---

## Giannopapa 2007 — Unified single-solution FSI progress

**Full citation:** Giannopapa, C. G., Papadakis, G. Indicative results and progress on the development of the unified single solution method for fluid-structure interaction problems. N/A, 2007. DOI: N/A

**BibTeX key suggestion:** giannopapa2007

**Discretisation (fluid):** cell-centred FV

**Discretisation (solid):** cell-centred FV

**Coupling structure:** unified one-continuum

**Mesh motion treatment:** Eulerian no mesh motion

**Nonlinear solver:** PISO

**Preconditioner / linearisation:** Rhie-Chow stabilisation

**Test cases:** wave propagation in a liquid-filled flexible straight tube; pressure along tube symmetry axis; wall distension along tube; axial and radial velocity histories

**Code released?** not stated

**One-paragraph summary (under 120 words):** This paper presents preliminary FSI results for a unified single-solution method in which fluid and solid are represented on one finite-volume grid and distinguished by local material coefficients and constitutive laws. Momentum and continuity are written with velocity and pressure as common primary variables, with the elastic solid stress recast into deviatoric and hydrostatic parts and displacement obtained by time-integrating velocity. The velocity-pressure coupling is solved using PISO with Rhie-Chow face interpolation. The demonstration is wave propagation in a water-filled elastic tube, reporting pressure, wall distension, and velocity fields. The method is implicit and avoids explicit interface exchange, but it is PISO-based rather than Newton-Krylov or block-preconditioned.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "The new approach is based on continuum mechanics formulation for fluids and structures where both continua can be solved using the momentum and continuity equation" (p.1); "The finite volume method was used for the discretisation of the equations" (p.3); "the interface between fluid and solid is part of the inner computational domain and no explicit exchange of information is needed" (p.4).

**Notes for the authors:** Abstract and conclusions describe a fully implicit unified FSI method, but the numerical method is a PISO velocity-pressure algorithm, not Newton-Krylov/JFNK or block-preconditioned. The paper presents preliminary tube-wave results and states that validation against analytical and established computational methods is future work.

---
