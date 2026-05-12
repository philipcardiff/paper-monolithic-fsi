---

## Degroote 2009 — Partitioned versus monolithic FSI

**Full citation:** Degroote, J., Bathe, K.-J., Vierendeels, J. Performance of a new partitioned procedure versus a monolithic procedure in fluid-structure interaction. Computers and Structures, 87:793-801, 2009. DOI: 10.1016/j.compstruc.2008.11.013

**BibTeX key suggestion:** degroote2009

**Discretisation (fluid):** FE

**Discretisation (solid):** FE

**Coupling structure:** partitioned / monolithic

**Mesh motion treatment:** inside Newton vector for monolithic; partitioned outer loop for IQN-ILS

**Nonlinear solver:** quasi-Newton / Newton

**Preconditioner / linearisation:** exact Jacobian for monolithic Newton; approximate inverse Jacobian from least-squares model for IQN-ILS

**Test cases:** wave propagation in elastic tube; mass conservation tube test; strong coupling test; shell in steady-state cross-flow; flexible restrictor flap in a converging channel

**Code released?** commercial (ADINA); IQN implementation release not stated

**One-paragraph summary (under 120 words):** The paper presents IQN-ILS, a partitioned interface quasi-Newton method that treats the flow and structural solvers as black boxes and approximates the inverse interface Jacobian using least-squares information from previous coupling iterations and time steps. It compares this partitioned method against ADINA's monolithic Newton-Raphson FSI solver on several incompressible FSI benchmarks. Both fluid and solid are discretised with finite elements, the fluid uses ALE motion for deforming meshes, and the solves use direct sparse linear solvers with full Newton-Raphson iterations. The reported IQN/MN runtime ratio ranges from about 1/2 to 4 when the partitioned method converges.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "compared with a monolithic Newton algorithm" (p.1); "the partitioned IQN-ILS method and the MN method are compared" (p.4)

**Notes for the authors:** Not directly competing with cell-centred FV/JFNK work: this study uses finite elements in ADINA, direct sparse solves, and full Newton-Raphson iterations rather than OpenFOAM/solids4foam, PETSc Krylov solvers, or a cell-centred FV discretisation.

---
