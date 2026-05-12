---

## Schott 2019 — Hybrid Eulerian-ALE CutFEM FSI

**Full citation:** Schott, B., Ager, C., Wall, W. A. A monolithic approach to fluid-structure interaction based on a hybrid Eulerian-ALE fluid domain decomposition involving cut elements. International Journal for Numerical Methods in Engineering, 00:2-33, 2019. DOI: 10.1002/nme.6047

**BibTeX key suggestion:** schott2019

**Discretisation (fluid):** FE

**Discretisation (solid):** FE

**Coupling structure:** monolithic

**Mesh motion treatment:** inside Newton vector

**Nonlinear solver:** Newton

**Preconditioner / linearisation:** approximate Jacobian; Nitsche coupling; ghost penalty stabilisation

**Test cases:** 
- Compressing ball under moderate deformations
- Flow over a largely moving cylinder
- Vibrating flexible flag-shaped structure

**Code released?** not stated

**One-paragraph summary (under 120 words):** The paper proposes a monolithic FSI method in which the fluid is split into a fixed Eulerian background domain and a moving ALE fluid patch fitted to the structure. The interface between fluid subdomains is treated with a CutFEM/Nitsche formulation and ghost-penalty stabilisation, while the fluid-solid interface is also weakly coupled by Nitsche terms. The method uses finite elements, generalized-alpha time integration for the structure, one-step-theta fluid time integration, and a Newton-Raphson monolithic solve that handles changing active degrees of freedom as the embedded patch moves. It targets large motion FSI while preserving boundary-layer resolution near the solid.

**Relevance classification:** closest prior work in spirit

**Direct quote(s) supporting the classification:** "A novel method for complex fluid-structure interaction (FSI) involving large structural deformation and motion is proposed." (p.1); "A clear advantage over existing overlapping domain decomposition methods consists in the sharp splitting of the fluid domain which comes along with improved convergence behavior of the resulting monolithic FSI system." (p.1); "This discretization technique is not limited to finite element based schemes, but can be realized in finite volume frameworks as well, even though FEM is chosen in the present work." (p.3).

**Notes for the authors:** Closest in monolithic/hybrid FSI spirit, but it is FE/CutFEM with Nitsche and Newton-Raphson rather than cell-centred FV, JFNK, PETSc, or block-preconditioned quasi-monolithic FSI.

---
