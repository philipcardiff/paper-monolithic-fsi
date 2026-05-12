---

## Lozovskiy 2019 — Monolithic finite element FSI assessment

**Full citation:** Lozovskiy, A., Olshanskii, M. A., Vassilevski, Y. V. Analysis and assessment of a monolithic FSI finite element method. Computers and Fluids, 179:277–288, 2019. DOI: 10.1016/j.compfluid.2018.11.004

**BibTeX key suggestion:** lozovskiy2019

**Discretisation (fluid):** FE

**Discretisation (solid):** FE

**Coupling structure:** monolithic

**Mesh motion treatment:** inside Newton vector

**Nonlinear solver:** N/A

**Preconditioner / linearisation:** approximate Jacobian

**Test cases:** 
- pressure wave propagation in a flexible tube
- clamped beam in a pipe flow
- hydrostatic equilibrium of the beam
- Phase I steady pipe-flow benchmark
- Phase II pulsatile pipe-flow benchmark

**Code released?** Ani3D, http://sourceforge.net/projects/ani3d

**One-paragraph summary (under 120 words):** The paper analyses a monolithic finite element method for incompressible Navier–Stokes flow coupled to a Saint Venant–Kirchhoff hyperelastic solid. Fluid and structure equations are written on reference domains, using ALE mapping for the fluid and Lagrangian coordinates for the solid, with a globally continuous displacement and velocity. The interface velocity and stress coupling are imposed strongly, and the fully discrete method is shown to satisfy an energy balance and unconditional stability estimate. Numerical tests use Taylor–Hood velocity-pressure elements and P2 displacement, with lagged geometric/advection terms and MUMPS direct solves, on a flexible-tube pressure-wave problem and a 3D clamped-beam-in-pipe benchmark.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "we analyze and investigate numerically a monolithic finite element method for the incompressible Navier–Stokes equations coupled to the Saint Venant–Kirchhoff hyperelastic model" (p.2); "The approach strongly enforces the coupling conditions on the fluid–structure interface" (p.2); "In the monolithic approach we consider conforming FE spaces" (p.6).

**Notes for the authors:** The method is monolithic FE and uses lagged geometric/advection terms with a direct MUMPS solve in the reported experiments; it does not describe JFNK, PETSc, cell-centred FV, or a block preconditioner.

---
