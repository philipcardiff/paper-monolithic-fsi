---

## Giannopapa 2008 — Unified FV elastodynamics stability analysis

**Full citation:** Giannopapa, C. G., Papadakis, G. Linear stability analysis and validation of a unified solution method for fluid-structure-interaction on a structural dynamic problem. Journal of Pressure Vessel Technology, N/A, 2008. DOI: N/A

**BibTeX key suggestion:** giannopapa2008

**Discretisation (fluid):** cell-centred FV

**Discretisation (solid):** cell-centred FV

**Coupling structure:** unified one-continuum

**Mesh motion treatment:** N/A

**Nonlinear solver:** PISO

**Preconditioner / linearisation:** N/A

**Test cases:** transient cantilever beam bending; comparison with standard stress analysis formulation; Euler implicit vs backward differencing; mesh/time-step sensitivity; beam dimension and load parametric study

**Code released?** not stated

**One-paragraph summary (under 120 words):** The paper reformulates linear elastodynamics in velocity-pressure variables so Hookean solids can be solved with the same finite-volume pressure-velocity machinery used for fluids. It presents the unified continuum equations, derives a pressure equation for solids, applies PISO coupling, and performs von Neumann stability analysis for Euler implicit, backward differencing, and central differencing choices. Validation is limited to transient beam bending, where the velocity-pressure formulation is compared with analytical beam estimates, a conventional displacement finite-volume formulation, and ANSYS for modal behaviour. The work is directly relevant as an OpenFOAM-style finite-volume precursor to unified FSI, but it does not present a Newton-Krylov or block-preconditioned monolithic FSI solve.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "treats both fluid and solid as a single continuum" (p.1); "A single set of equations is used to describe the fluid and solid" (p.2); "the finite volume method is used here for solids as well" (p.3).

**Notes for the authors:** Although framed as a unified FSI method, the validation in this paper is a solid-only transient beam-bending problem; full FSI is described as the next step rather than demonstrated.

---
