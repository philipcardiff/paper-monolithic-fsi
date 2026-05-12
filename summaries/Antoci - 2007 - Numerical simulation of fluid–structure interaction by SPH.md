---

## Antoci 2007 — Fluid-structure interaction by SPH

**Full citation:** Antoci, C., Gallati, M., Sibilla, S. Numerical simulation of fluid-structure interaction by SPH. Computers and Structures, 85:879-890, 2007. DOI: 10.1016/j.compstruc.2007.01.002

**BibTeX key suggestion:** antoci2007

**Discretisation (fluid):** particle

**Discretisation (solid):** particle

**Coupling structure:** monolithic

**Mesh motion treatment:** N/A

**Nonlinear solver:** explicit

**Preconditioner / linearisation:** N/A

**Test cases:** - free oscillation of an elastic cantilever plate; dam-break/free-surface sensitivity study; elastic rubber gate deformed by rapidly varying water pressure

**Code released?** not stated

**One-paragraph summary (under 120 words):** The paper presents a fully Lagrangian SPH formulation for FSI in which both fluid and solid phases are represented by particles. The fluid is treated as inviscid and weakly compressible, while the solid uses an incremental hypoelastic law with Jaumann-rate stress update. Fluid-solid coupling is imposed through interface conditions: the fluid pressure contribution on the solid is computed using an approximate SPH surface integral, and the reaction on the fluid is obtained by interpolation to preserve action-reaction balance. Time integration is explicit and staggered. Validation compares SPH predictions with an experiment involving a rubber gate deformed by water outflow from a tank.

**Relevance classification:** background

**Direct quote(s) supporting the classification:** N/A

**Notes for the authors:** SPH particle-based FSI with simultaneous explicit updates, not a finite-volume, ALE moving-mesh, Newton-Krylov, PETSc, or block-preconditioned method.

---
