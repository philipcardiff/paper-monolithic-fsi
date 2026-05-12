---

## Cardiff 2025 — solids4foam toolbox for OpenFOAM FSI

**Full citation:** Cardiff, P., Batistić, I., Tuković, Ž. solids4foam: A toolbox for performing solid mechanics and fluid-solid interaction simulations in OpenFOAM. Journal of Open Source Software, 10(108):7407, 2025. DOI: 10.21105/joss.07407

**BibTeX key suggestion:** cardiff2025

**Discretisation (fluid):** cell-centred FV

**Discretisation (solid):** cell-centred FV / vertex-centred FV

**Coupling structure:** partitioned

**Mesh motion treatment:** partitioned outer loop

**Nonlinear solver:** PIMPLE / segregated / coupled / explicit

**Preconditioner / linearisation:** N/A

**Test cases:** - solids tutorials: linear elasticity, elastoplasticity, hyperelasticity, poroelasticity, thermoelasticity, viscoelasticity, multiple materials, fracture; fluid tutorials; fluid-solid interaction tutorials; thermo-fluid-solid interaction tutorials

**Code released?** solids4foam; repository/archive links indicated in the JOSS sidebar, URL not stated in extracted PDF text

**One-paragraph summary (under 120 words):** This JOSS software paper describes solids4foam v2.1, an OpenFOAM toolbox for solid mechanics, fluid-solid interaction, and thermo-fluid-solid interaction. The FSI capability is presented as partitioned coupling with fixed relaxation, Aitken relaxation, interface-quasi-Newton Dirichlet-Neumann coupling, and an added-mass Robin-Neumann formulation. For solid mechanics, the toolbox supports segregated, coupled, and explicit finite-volume solution algorithms, small- and finite-strain formulations, total and updated Lagrangian approaches, and both cell-centred and vertex-centred formulations. Fluid support comes through ported OpenFOAM fluid solvers including PIMPLE, PIMPLE-overset, VOF multiphase, and weakly compressible flow.

**Relevance classification:** FV-but-partitioned

**Direct quote(s) supporting the classification:** "solids4foam provides a range of partitioned coupling methods for fluid-solid interaction" (p.2); "solids4foam remains a uniquely positioned toolbox within OpenFOAM, offering a well-maintained and feature-rich platform for solid mechanics and fluid-solid interaction simulations based on the finite volume method" (p.1)

**Notes for the authors:** JOSS software paper rather than a detailed numerical-method paper; no direct JFNK, PETSc, or quasi-monolithic method is described in the inspected text.

---
