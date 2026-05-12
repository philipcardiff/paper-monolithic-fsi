---

## Zarifian 2018 — Sloshing effects on supersonic shell flutter

**Full citation:** Zarifian, P., Ovesy, H. R., Firouz-Abadi, R. D. Sloshing effects on supersonic flutter characteristics of circular cylindrical shell partially filled with a liquid. International Journal for Numerical Methods in Engineering, 00:1-26, 2017. DOI: 10.1002/nme.5984

**BibTeX key suggestion:** zarifian2018

**Discretisation (fluid):** FE

**Discretisation (solid):** FE

**Coupling structure:** monolithic

**Mesh motion treatment:** N/A

**Nonlinear solver:** N/A

**Preconditioner / linearisation:** exact Jacobian

**Test cases:** 
- Vibration of empty and 75%-filled cantilevered circular cylindrical shells
- Supersonic flutter of an empty pressurized circular cylindrical shell
- Sloshing frequencies of a rigid cylindrical water container
- Buckling of a pressurized circular cylindrical shell
- Flutter of 60%-filled and 20%-filled simply-supported circular cylindrical shells

**Code released?** not stated

**One-paragraph summary (under 120 words):** The paper develops a finite element fluid-structure interaction model for supersonic flutter of a circular cylindrical shell partially filled with liquid. The internal incompressible inviscid liquid is represented by a hydroelastic added-mass model with gravity, including free-surface sloshing; the shell uses linear Sanders shell theory; and external aerodynamic loading uses first-order piston theory. The assembled coupled system is reduced to structural displacement, free-surface elevation, and a pressure-constraint variable, then solved as a frequency-domain eigenvalue problem to locate flutter boundaries. The main claim is that, for the cases studied, sloshing has little influence on the flutter boundary and the simpler hydroelastic added-mass model gives conservative results.

**Relevance classification:** background

**Direct quote(s) supporting the classification:** N/A

**Notes for the authors:** Citation metadata in the PDF is an accepted-article version: first page says Int. J. Numer. Meth. Engng 2017; 00:1-26, while the file name and PDF creation date indicate 2018. Method is a linear FE coupled eigenvalue formulation, not a Newton-Krylov, JFNK, PETSc, cell-centred FV, or block-preconditioned FSI method.

---
