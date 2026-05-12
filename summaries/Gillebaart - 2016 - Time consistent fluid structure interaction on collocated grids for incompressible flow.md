---

## Gillebaart 2016 — Time consistent FSI on collocated grids

**Full citation:** Gillebaart, T., Blom, D. S., van Zuijlen, A. H., Bijl, H. Time Consistent Fluid Structure Interaction on Collocated Grids for Incompressible Flow. Computer Methods in Applied Mechanics and Engineering, N/A(N/A):N/A, 2016. DOI: 10.1016/j.cma.2015.09.025

**BibTeX key suggestion:** gillebaart2016

**Discretisation (fluid):** cell-centred FV

**Discretisation (solid):** cell-centred FV

**Coupling structure:** partitioned

**Mesh motion treatment:** partitioned outer loop

**Nonlinear solver:** PISO / fixed-point

**Preconditioner / linearisation:** Rhie-Chow stabilisation

**Test cases:** circular cavity flow on static and moving grids; circular cavity coupled to a 3-DoF rigid body; three-dimensional flow over an elastic beam in a channel; Turek-Hron FSI-3 fixed cylinder with flexible flap benchmark

**Code released?** not stated

**One-paragraph summary (under 120 words):** The paper develops time-consistent finite-volume FSI on collocated grids for incompressible flow using an ALE PISO formulation. Its main contribution is a detailed treatment of face fluxes, face-normal/area corrections, moving-wall velocity boundary conditions, and fluid-force interpolation so that BDF1, BDF2, and BDF3 schemes retain their formal order on moving grids and in partitioned FSI. The structure is treated either as a 3-DoF rigid body or as a finite-volume total-Lagrangian elastic solid. Coupling is strongly partitioned with Aitken or IQN-ILS interface iterations, rather than monolithic Newton-Krylov coupling. Results demonstrate order behaviour and efficiency on cavity, elastic-beam, and Turek-Hron FSI-3 cases.

**Relevance classification:** FV-but-partitioned

**Direct quote(s) supporting the classification:** N/A

**Notes for the authors:** Highly relevant collocated FV/ALE FSI predecessor, but Section 2.6.1 explicitly uses partitioned black-box fluid/solid coupling with Aitken or IQN-ILS interface iterations, not monolithic or quasi-monolithic JFNK with a block preconditioner.

---
