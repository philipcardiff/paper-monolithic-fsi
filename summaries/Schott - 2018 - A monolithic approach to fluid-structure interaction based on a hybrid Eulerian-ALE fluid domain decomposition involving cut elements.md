---

## Schott 2018 — Hybrid Eulerian-ALE CutFEM FSI

**Full citation:** Schott, B., Ager, C., Wall, W. A. A monolithic approach to fluid-structure interaction based on a hybrid Eulerian-ALE fluid domain decomposition involving cut elements. arXiv preprint arXiv:1808.00343, 2018.

**BibTeX key suggestion:** schott2018b

**Discretisation (fluid):** FE

**Discretisation (solid):** FE

**Coupling structure:** monolithic

**Mesh motion treatment:** outside Newton vector, updated within Newton iterations

**Nonlinear solver:** Newton

**Preconditioner / linearisation:** pseudo-directional derivatives / approximate Jacobian; no preconditioner stated

**Test cases:**
- Compressing ball under moderate deformations
- Flow over a largely moving cylinder
- Vibrating flexible flag-shaped structure

**Code released?** not stated

**One-paragraph summary (under 120 words):** The paper proposes a monolithic FSI method using a hybrid fluid domain: a moving ALE boundary-layer patch fitted to the structure is embedded in a fixed Eulerian background mesh. Both the fluid-fluid interface and fluid-solid interface are coupled weakly using Nitsche-type terms in a CutFEM finite-element formulation, with ghost-penalty and RBVM stabilisation for the cut background fluid mesh. The coupled system is advanced with a fully implicit Newton-Raphson procedure, including algorithmic handling of changing active degrees of freedom as the cut interface moves. The method targets large structural motion while retaining near-wall mesh resolution.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "full-implicit monolithic way" (p.29); "not limited to Finite Element based schemes" (p.8).

**Notes for the authors:** No abstract/method inconsistency found. This is monolithic FE/CutFEM with Newton-Raphson and Nitsche coupling, not cell-centred FV, OpenFOAM/PETSc, JFNK, or a block-preconditioned method. The PDF is an arXiv 2018 preprint and no DOI appears in the PDF or metadata.

---
