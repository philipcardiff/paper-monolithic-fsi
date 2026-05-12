---

## Meduri 2018 — Fully explicit partitioned Lagrangian FSI

**Full citation:** Meduri, S., Cremonesi, M., Perego, U., Bettinotti, O., Kurkchubasche, A., Oancea, V. A partitioned fully explicit Lagrangian finite element method for highly nonlinear fluid-structure interaction problems. International Journal for Numerical Methods in Engineering, 113:43-64, 2018. DOI: 10.1002/nme.5602

**BibTeX key suggestion:** meduri2018

**Discretisation (fluid):** FE

**Discretisation (solid):** FE

**Coupling structure:** partitioned

**Mesh motion treatment:** N/A

**Nonlinear solver:** explicit

**Preconditioner / linearisation:** N/A

**Test cases:** 1D shock pressure wave propagation; breaking dam flow through an elastic gate; breaking dam flow over an elastic obstacle; filling of an elastic container

**Code released?** commercial Abaqus/Explicit; PFEM code not stated

**One-paragraph summary (under 120 words):** The paper presents a fully explicit, fully Lagrangian partitioned FSI method for highly nonlinear transient problems with free surfaces and large structural deformation. The fluid is solved with an explicit weakly compressible Particle Finite Element Method using remeshing, while the solid is solved with Abaqus/Explicit using standard explicit finite elements. Coupling uses the Gravouil-Combescure domain-decomposition algorithm, imposing velocity continuity through interface Lagrange multipliers and allowing nonconforming meshes and different time steps. The method targets fast dynamics where explicit time steps are acceptable and avoids nonlinear iterations. Validation covers shock-wave transmission and several dam-break/elastic-structure benchmarks against analytical, experimental, and numerical references.

**Relevance classification:** background

**Direct quote(s) supporting the classification:** "In this work, a fully explicit partitioned method for the simulation of Fluid Structure Interaction (FSI) problems is presented." (p.1); "the interaction problem is solved using the Gravouil and Combescure (GC) algorithm." (p.2)

**Notes for the authors:** The paper is relevant as a highly nonlinear FSI method, but it is partitioned, fully explicit, Lagrangian PFEM/FEM, and commercial-software-based rather than monolithic, cell-centred FV, Newton-Krylov/JFNK, PETSc, or block-preconditioned. The filename uses 2017, while the PDF citation line gives International Journal for Numerical Methods in Engineering, 2018;113:43-64, with DOI 10.1002/nme.5602.

---
